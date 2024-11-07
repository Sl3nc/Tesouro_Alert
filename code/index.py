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
            p.append((*[data for data in info if data != ''],))
        return p
    
    def close(self):
        self.driver.quit()

class Email:
    PATH_MESSAGE = Path(__file__).parent / 'src' / 'base_message.html'

    def __init__(self) -> None:
        self.smtp_server = 'smtp.google.com'
        self.smtp_port = 587
        self.smtp_username = os.getenv("EMAIL_SENDER","")
        self.smtp_password = os.getenv("PASSWRD_SENDER","")
        pass

    def create_message(self, data: list[tuple]) -> str:
        format_data = []
        for item in data:
            format_data.append(' - '.join(item))

        with open (self.PATH_MESSAGE, 'r') as file:
            text_message = file.read()
            return Template(text_message)\
                .substitute(infos = format_data)

    def send(self, texto_email: str, to: str) -> bool:
        mime_multipart = MIMEMultipart()
        mime_multipart['from'] = self.smtp_username
        mime_multipart['to'] = to
        mime_multipart['subject'] = f'Atualização Tesouro Direto {datetime.strftime(datetime.now(), '%d/%m - %H:%M')}'

        corpo_email = MIMEText(texto_email, 'html', 'utf-8')
        mime_multipart.attach(corpo_email)

        self._open_server(mime_multipart)
        return True

    def _open_server(self, mime_multipart) -> None:
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            print('oi')
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(mime_multipart)
        
        print('Email enviado com sucesso')

class DataBase:
    NOME_DB = 'tesouro_db.sqlite3'
    FOLDER_DB = resource_path(f'src\\db\\{NOME_DB}')
    TABLE_LATE = 'Infos_Late'
    TABLE_CONST = 'Infos_Const'

    def __init__(self) -> None:
        self.query_columns = (
            'PRAGMA table_info({0});'
        )

        self.query_late = (
            'SELECT * FROM {0}'
        )

        self.update_late = (
            'UPDATE {0} SET '
            'Titulo = ?, Ano = ?, Rentabilidade_Anual = ?, Investimento_Minimo = ?, Preco_Unitario = ?, Vencimento = ? '
            'WHERE id_late = ?; '
        )

        self.insert_const = (
            f'INSERT INTO {self.TABLE_CONST}'
            '* VALUES '
            '(:titulo, :rentabilidade_anual)'
        )

        self.connection = sqlite3.connect(self.FOLDER_DB)
        self.cursor = self.connection.cursor()
        pass

    def filter_moveless(self, contents: list[tuple]):
        self.cursor.execute(
            self.query_late.format(self.TABLE_LATE)
        )
        lates_moves = self.cursor.fetchall()

        filtred_moves = []
        for move in lates_moves:
            # print(f'{move} - movimento db')
            for content in contents:
                # print(f'{content} - opção do site')
                if content[0] == move[1]\
                    and content[3] != move[4]:
                    filtred_moves.append((str(move[0]),) + content)
        # print(f'{filtred_moves} - resultado final')
        return filtred_moves

    def update(self, move: list[tuple]):
        for item in move:
            self.cursor.execute(
                self.update_late.format(
                    self.TABLE_LATE,
                ),
                (item[1], item[2], item[3], item[4], item[5], item[6], item[0])
            )
            self.connection.commit()

    def exit(self):
        self.cursor.close()
        self.connection.close()

if __name__ == '__main__':
    try:
        browser = Browser()
        email = Email()
        db = DataBase()
        
        content = browser.search()
        browser.close()


        move = db.filter_moveless(content)

        if move != []:
            message = email.create_message(move)
            for person in json.loads(os.environ['ADDRESSE']):
              print(person)
              email.send(message, person)
            
            # db.update(move)
        db.exit()
    # except Exception as err:
    finally:
        db.exit()
        browser.close()

