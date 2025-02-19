from re import sub, I
from json import load
from os import getenv
from time import sleep
from smtplib import SMTP
from pathlib import Path
from copy import deepcopy
from sqlite3 import connect
from string import Template
from datetime import datetime
from dotenv import load_dotenv
from bisect import bisect_left
from selenium import webdriver
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.chrome.service import Service
load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class Browser:
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    SELECTOR_TABLE = '#td-precos_taxas-tab_{0} > div > div.td-mercado-titulos__content > table'
    button_resgatar = 'body > main > div.td-precosTaxas > div:nth-child(2) > div > div > ul > li:nth-child(2)'
    LINK = 'https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm'

    def __init__(self, hide=True) -> None:
        self.driver = self.make_chrome_browser()
        # if hide == True:
        #     self.driver.set_window_position(-10000,0)
        self.driver.get(self.LINK)
        pass

    def make_chrome_browser(self,*options: str) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()

        # chrome_options.add_argument('--headless')
        if options is not None:
            for option in options:
                chrome_options.add_argument(option)

        chrome_service = Service(
            executable_path=str(self.CHROME_DRIVER_PATH),
        )

        browser = webdriver.Chrome(
            service=chrome_service,
            options=chrome_options
        )
        return browser
    
    def search(self) -> list[tuple]:
        table_lines = []
        table_lines = self._pull_data(1)
        self.driver.execute_script("window.scrollTo(0, 250)")
        self.driver.find_element(By.CSS_SELECTOR, self.button_resgatar).click()
        table_lines = table_lines + self._pull_data(2)
        self.driver.quit()
        table_lines.sort(key= lambda x: x[0])
        return table_lines

    def _pull_data(self, table_index):
        temp_lines = []
        tabela = self.driver.find_element(By.CSS_SELECTOR, self.SELECTOR_TABLE.format(table_index))
        linhas = tabela.find_elements(By.TAG_NAME, 'tbody')

        sleep(2)
        for linha in linhas:
            info = linha.find_elements(By.TAG_NAME, 'span')
            item = []
            for data in info:
                if data.text != '':
                    item.append(data.text)

            #Apenas funciona com o segundo método chamado 
            if 'com juros semestrais' in item[1]\
                or "aposentadoria extra" in item[1]:
                item.pop(1)

            if len(item) == 5:
                item.insert(3, '--')
                
            temp_lines.append((*[item_data for item_data in item],))
            
        return temp_lines

class Users:
    PATH = Path(__file__).parent / 'src' / 'json' / 'users.json'

    def __init__(self):
        with open(self.PATH, 'r') as file:
            self.data = load(file)
        pass

    def prefers(self, moves: list[tuple], infos_db: list[tuple]) -> dict[str, list[tuple]]:
        prefers_dict = {}
        for email, pref_list in self.data.items():
            found_data = []
            for user_data in pref_list:
                result = self._search(user_data, moves)
                if result == None:
                    result = self._search(user_data, infos_db) 
                if result == None:
                    result = (user_data['title'], user_data['year'],'--','--','--','--')
                found_data.append(result)
            prefers_dict[email] = found_data
        return prefers_dict
            
    def _search(self, user_data: dict, base_data: list[tuple]) -> tuple:
        fees = ''
        if user_data['fees'] == True:
            fees = '\ncom juros semestrais {0}'.format(user_data['year'])

        wish = 'TESOURO {0} {1}{2}'.format(user_data['title'], user_data['year'], fees)

        arr_copy = deepcopy(base_data)
        arr_copy.sort(key= lambda x: x[0])
        
        arr = [item[0] for item in arr_copy]
        i = bisect_left(arr, wish)
        if i != len(arr) and arr[i] == wish:
            return arr_copy[i]
        return None

class Message:
    PATH = Path(__file__).parent / 'src' / 'doc' / 'base_message.html'

    ref_cor = {
        'IPCA': 'lightyellow',
        'RENDA': 'lightblue',
        'EDUCA': 'lightpink',
        'PREFIXADO': 'lightcyan',
        'SELIC': 'lightcoral',
        'IGPM': 'lightgreen'
    }

    sign_up = '▲'
    sign_down = '▼'

    def __init__(self, moves: list[tuple]):
        self.moves = self._rows(moves)
        pass

    def create(self, pref: list[tuple]):
        with open (self.PATH, 'r', encoding='utf-8') as file:
            text_message = file.read()
            return Template(text_message)\
                    .substitute(
                        moves = ''.join(x for x in self.moves),
                        prefer = ''.join(y for y in self._rows(pref))
                    )

    def _rows(self, table: list[tuple]) -> list[str]:
        format_data = []
        for item in table:
            item = self.style(item)

            item_str = ''.join(
                [f'<td> {data} </td>' for data in item]
            )

            color = self.set_color(item[0])
            format_data.append(
                 f'<tr style="background-color: {color};"> {item_str} </tr>'
            )

        return format_data

    def style(self, item):
        y = list(item)
        variation_value = float(y[3])

        color_font = 'green' if variation_value > 0 else\
                        'red' if variation_value < 0 else 'black'
        
        signal = f'% {self.sign_up if variation_value > 0 else\
                        self.sign_down if variation_value < 0 else '◆'}'

        y[3] = f'<span style="color:{color_font}";> {variation_value} {signal} </span>'
        
        y[0] = sub(r"[0-9]", "", item[0])
        return tuple(y)
        
    def set_color(self, name_row: str):
        for key, color in self.ref_cor.items():
            if key in name_row:
                return color
        return 'white'
    
class Email:
    def __init__(self) -> None:
        self.smtp_server = getenv("SMTP_SERVER","")
        self.smtp_port = getenv("SMTP_PORT", 0)

        self.smtp_username = getenv("EMAIL_SENDER","")
        self.smtp_password = getenv("PASSWRD_SENDER","")
        pass

    def send(self, texto_email: str, to: str) -> None:
        mime_multipart = MIMEMultipart()
        mime_multipart['From'] = self.smtp_username
        mime_multipart['To'] = to
        mime_multipart['Subject'] = f'Atualização Tesouro Direto {datetime.strftime(datetime.now(), '%d/%m - %H:%M')}'

        mime_multipart.attach(MIMEText(texto_email, 'html', 'utf-8'))

        self._open_server(mime_multipart)

    def _open_server(self, mime_multipart: MIMEMultipart) -> None:
        with SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(mime_multipart)
        
class DataBase:
    FOLDER_DB = Path(__file__).parent / 'src'/'db'/ 'tesouro_db.sqlite3'
    TABLE_LATE = 'Infos_Late'
    TABLE_OLD = 'Infos_Const'

    def __init__(self) -> None:
        
        self.query_columns = (
            'PRAGMA table_info({0});'
        )

        self.query_late = (
            f'SELECT id_late, Titulo, Ano, Rentabilidade_Anual, Investimento_Minimo, Preco_Unitario, Vencimento FROM {self.TABLE_LATE} ORDER BY Titulo ASC;'
        )

        self.update_late = (
            f'UPDATE {self.TABLE_LATE} SET '
            'Titulo = ?, Ano = ?, Rentabilidade_Anual = ?, Investimento_Minimo = ?, Preco_Unitario = ?, Vencimento = ? '
            'WHERE id_late = ?; '
        )

        self.insert_late = (
            f'INSERT INTO {self.TABLE_LATE} '
            '(Titulo, Ano, Rentabilidade_Anual, Investimento_Minimo, Preco_Unitario, Vencimento)'
            ' VALUES '
            '(?,?,?,?,?,?)'
        )

        self.insert_old = (
            f'INSERT INTO {self.TABLE_OLD}'
            ' (Título, Rentabilidade Anual) VALUES '
            '(?, ?)'
        )

        self.connection = connect(self.FOLDER_DB)
        self.cursor = self.connection.cursor()
        pass

    def init(self, infos_site: list[tuple]):
        for item in infos_site:
            self.cursor.execute(
                self.insert_late,
                (item[0], item[1], item[2], item[3], item[4], item[5])
            )
        self.connection.commit()

    def query(self) -> list[tuple]:
        self.cursor.execute(
            self.query_late
        )
        return self.cursor.fetchall()
    
    def insert(self, data_site) -> None:
         for item in data_site:
            self.cursor.execute(
                self.insert_late,
                (item[0], item[1], item[2], item[4], item[5], item[6])
            )
            self.connection.commit()
    
    def update(self, move: dict[str,tuple]):
        for id, item in move.items():
            self.cursor.execute(
                self.update_late,
                (item[0], item[1], item[2], item[4], item[5], item[6], id)
            )
            self.connection.commit()

    def exit(self):
        self.cursor.close()
        self.connection.close()

class Report:
    path = Path(__file__).parent / 'src' /'doc' / 'relatório_emails.txt'
    
    def __init__(self) -> None:
        pass

    def is_error(self, message):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write(f'Erro ocorrido: {message}')
            file.write('\n')

    def is_send(self, email: str):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Email enviado às ' + datetime.strftime(datetime.now(), '%d/%m - %H:%M') + '\n'
            )
            file.write(f'- {email} \n')
            file.write('\n')

    def is_new(self, unfound: list[tuple]):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Linhas Adcionadas:\n')
            for row in unfound:
                file.write(row[0])
            file.write('\n')

    def is_updated(self, outdated: dict[str, tuple]):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Linhas Atualizadas:\n')
            for row in outdated.values():
                file.write(row[0])
            file.write('\n')

class Main:
    def __init__(self) -> None:
        self.email = Email()
        self.db = DataBase()
        self.report = Report()
        pass

    def hard_work(self):
        try:
            infos_site = Browser().search()
            infos_db = self.db.query()

            #Ganham variação
            outdated_site, unfound_site = self.filter(infos_db, infos_site)

            if unfound_site != []:
                self.db.insert(unfound_site)
                self.report.is_new(unfound_site)

            if outdated_site != {}:
                self.db.update(outdated_site)
                self.report.is_updated(outdated_site)

            moves = list(outdated_site.values()) + unfound_site

            if moves != []:
                msg = Message(moves)
                infos_db = [(item[1:4] + (0,) + item[4:]) for item in infos_db]
                users_pref = Users().prefers(moves, infos_db)
                for email, pref in users_pref.items():
                    message = msg.create(pref)
                    self.email.send(message, email)
                self.report.is_send(email)

        except Exception as err:
            self.report.is_error(err)
        finally:
            self.db.exit()

    def filter(self, infos_db: list[tuple], infos_site: list[tuple]):
        outdated_site = {}
        unfound_site = []

        for data_site in infos_site:
            achado = False
            for data_db in infos_db:
                if data_site[0] == data_db[1]:

                    if data_site[3] == '--' and data_db[4] == '--':
                        achado = True
                    elif data_site[3] != '--' and data_db[4] != '--':
                        achado = True
                    else:    
                        continue

                    if data_site[2] != data_db[3]:
                        outdated_site[str(data_db[0])] = (
                            data_site[0:3] + 
                            (self.variacao(data_site[2], data_db[3]),) + 
                            data_site[3:]
                        )
                    break
            if achado == False: 
                unfound_site.append((data_site[0:3] + (0,) + data_site[3:]))

        return outdated_site, unfound_site
    
    def variacao(self, new_value: str, old_value: str, ):
        new_value = float(sub(r'[A-Z !+%]', '',\
                        new_value.replace(',','.'), flags= I))
        
        old_value = float(sub(r'[A-Z !+%]', '',\
                        old_value.replace(',','.'), flags= I))

        result = ((new_value - old_value) / old_value) * 100

        return float(f'{result:,.2f}')
    
    def init_db(self):
        self.db.init(Browser().search())

if __name__ == '__main__':
    Main().hard_work()