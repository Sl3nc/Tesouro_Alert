from time import sleep
from abc import abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import sqlite3
import sys
import os

import re
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

def resource_path(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Browser:
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    SELECTOR_TABLE = '#td-precos_taxas-tab_1 > div > div.td-mercado-titulos__content > table'
    LINK = 'https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm'

    def __init__(self, hide=True) -> None:
        self.driver = self.make_chrome_browser()
        if hide == True:
            self.driver.set_window_position(-10000,0)
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
        tabela = self.driver.find_element(By.CSS_SELECTOR, self.SELECTOR_TABLE)
        linhas = tabela.find_elements(By.TAG_NAME, 'tbody')

        p = []
        for linha in linhas:
            info = linha.find_elements(By.TAG_NAME, 'span')
            for index, data in enumerate(info):
                info[index] = data.text
            p.append((*[data for data in info if data != ''\
                and data[:3] != 'com' \
                    and data[:3] != 'apo'],))
            
        self.driver.quit()
        return p
    
class Email:
    PATH_MESSAGE = Path(__file__).parent / 'src' / 'base_message.html'

    def __init__(self) -> None:
        self.smtp_server = os.getenv("SMTP_SERVER","")
        self.smtp_port = os.getenv("SMTP_PORT", 0)

        self.smtp_username = os.getenv("EMAIL_SENDER","")
        self.smtp_password = os.getenv("PASSWRD_SENDER","")

        self.ref_cor = {
            'IPCA': 'lightyellow',
            'RENDA': 'lightblue',
            'EDUCA': 'lightgreen',
            'PREFIXADO': 'lightcyan',
            'SELIC': 'lightcoral'
        }
        pass

    def create_message(self, move: list[tuple]) -> str:
        format_data = []
        for item in move:
            y = list(item)
            y[1] = re.sub(r"\d", "", item[1])
            item = tuple(y)

            item_str = ''.join(
                [f'<td> {data} </td>' for data in item[1:]]
            )

            color = self.get_color(item[1])
            format_data.append(
                 f'<tr style="background-color: {color};"> {item_str} </tr>'
            )

        with open (self.PATH_MESSAGE, 'r', encoding='utf-8') as file:
            text_message = file.read()
            return Template(text_message)\
                .substitute(infos =  ''.join(x for x in format_data))
        
    def get_color(self, name_row):
        print(name_row)
        for key, color in self.ref_cor.items():
            if key in name_row:
                return color
        return 'white'

    def send(self, texto_email: str, to: str) -> None:
        mime_multipart = MIMEMultipart()
        mime_multipart['From'] = self.smtp_username
        mime_multipart['To'] = to
        mime_multipart['Subject'] = f'Atualização Tesouro Direto {datetime.strftime(datetime.now(), '%d/%m - %H:%M')}'

        mime_multipart.attach(MIMEText(texto_email, 'html', 'utf-8'))

        self._open_server(mime_multipart)

    def _open_server(self, mime_multipart: MIMEMultipart) -> None:
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(mime_multipart)
        
class DataBase:
    DB_NAME = 'tesouro_db.sqlite3'
    FOLDER_DB = resource_path(f'src\\db\\{DB_NAME}')
    TABLE_LATE = 'Infos_Late'
    TABLE_OLD = 'Infos_Const'

    def __init__(self) -> None:
        
        self.query_columns = (
            'PRAGMA table_info({0});'
        )

        self.query_late = (
            f'SELECT * FROM {self.TABLE_LATE} ORDER BY Titulo ASC;'
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

        self.connection = sqlite3.connect(self.FOLDER_DB)
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
                (item[0], item[1], item[2], item[3], item[4], item[5])
            )
            self.connection.commit()
    
    def update(self, move: list[tuple]):
        for item in move:
            self.cursor.execute(
                self.update_late,
                (item[1], item[2], item[3], item[5], item[6], item[7], item[0])
            )
            self.connection.commit()

    def exit(self):
        self.cursor.close()
        self.connection.close()

class Report:
    def __init__(self) -> None:
        self.path = resource_path('relatório_emails.txt')
        pass

    def is_send(self, to: list[str]):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n')
            file.write(
                '#'*10 + ' Email enviado às' + datetime.strftime(datetime.now(), '%d/%m - %H:%M') + '#'*10 + '\n'
            )
            for person in to:
                file.write(person)
            file.write('\n')

    def is_new(self, unfound: list[tuple]):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n')
            file.write('\n#'*10 + 'Linhas Adcionadas:\n')
            for row in unfound:
                file.write(row[1])
            file.write('\n')

    def is_updated(self, outdated: list[tuple]):
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('#'*10 + 'Linhas Atualizadas:\n')
            for row in outdated:
                file.write(row[1])
            file.write('\n')

class Main:
    def __init__(self) -> None:
        self.email = Email()
        self.db = DataBase()
        self.report = Report()

        self.sign_up = '▲'
        self.sign_down = '▽'
        pass

    def hard_work(self):
        try:
            infos_site = Browser().search()

            infos_db = self.db.query()

            moves = self.filter(infos_db, infos_site)

            if moves != []:
                message = self.email.create_message(moves)
                to = json.loads(os.environ['ADDRESSE'])
                for person in to:
                    self.email.send(message, person)
                self.report.is_send(to)
        finally:
            self.db.exit()

    def filter(self, infos_db: list[tuple], infos_site: list[tuple]):
        outdated_site = []
        unfound_site = []

        for data_site in infos_site:
            # print(f'{data_site}  - opção do site')
            achado = False
            for data_db in infos_db:
                # print(f'{data_db} - movimento db')
                if data_site[0] == data_db[1]:
                    achado = True

                    if data_site[2] != data_db[3]:
                        outdated_site.append(
                            (str(data_db[0]),) + data_site[0:3] + (self.variacao(data_site[2], data_db[3]),) + data_site[3:]
                        )
                    # continue

            if achado == False: unfound_site.append(data_site)

        if unfound_site != []:
            self.db.insert(unfound_site)
            self.report.is_new(unfound_site)

        if outdated_site != []:
            self.db.update(outdated_site)
            self.report.is_updated(outdated_site)

        return outdated_site + unfound_site
    
    def variacao(self, new_value: str, old_value: str, ):
        values = []
        for data in [old_value, new_value]:
            values.append(float(re.sub(r"[A-Z !+%]", "", data.replace(',','.'), 0, re.IGNORECASE)))

        result = ((values[1] - values[0]) / values[0]) * 100

        return f'{
            result:,.2f}% {self.sign_up if result > 0 else self.sign_down
                }'.replace('.',',') 
    
    def init_db(self):
        self.db.init(Browser().search())

if __name__ == '__main__':
    Main().hard_work()