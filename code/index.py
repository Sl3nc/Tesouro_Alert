from pathlib import Path
from time import sleep
from abc import abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import sys

class Browser:
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'

    def make_chrome_browser(self,*options: str, hide = True) -> webdriver.Chrome:
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

        if hide == True:
            browser.set_window_position(-10000,0)

        return browser
    
if __name__ == '__main__':
    driver = Browser().make_chrome_browser(hide=False)
    driver.get('https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm')

    tabela = driver.find_element(By.CSS_SELECTOR, '#td-precos_taxas-tab_1 > div > div.td-mercado-titulos__content > table')

    linhas = tabela.find_elements(By.TAG_NAME, 'tbody')

    conteudos = [linha.find_elements(By.TAG_NAME, 'span') for linha in linhas]

    mapa = [{}]
    for index, i in enumerate(conteudos):
        for j in i:
            mapa[index][f'a{index}'] = j.text


    # mapa = [
    #         {key: conteudo.text}
    #         for conteudo in a
    #         for key in [
    #             'Título','Rentabilidade Anual','Investimento Mínimo','Preço Unitário', 'Vencimento'
    #         ]
    # ]

    # for i in mapa:
    #     for key, value in i.items():
    #         print(value)