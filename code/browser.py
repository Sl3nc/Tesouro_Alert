from pathlib import Path
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import chain

class Browser:
    """
    Classe responsável por automatizar a navegação e extração de dados do site do Tesouro Direto usando Selenium.
    """
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    SELECTOR_TABLE = '#td-precos_taxas-tab_{0} > div > div.td-mercado-titulos__content > table'
    button_resgatar = 'body > main > div.td-precosTaxas > div:nth-child(2) > div > div > ul > li:nth-child(2)'
    LINK = 'https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm'
    selector_table = '#td-precos_taxas-tab_{0} > div'

    def __init__(self) -> None:
        """
        Inicializa o navegador Chrome e acessa a página do Tesouro Direto.
        :param hide: Se True, oculta a janela do navegador.
        """
        self.driver = self.make_chrome_browser()
        self.driver.get(self.LINK)
        pass

    def make_chrome_browser(self) -> webdriver.Chrome:
        """
        Cria uma instância do navegador Chrome com opções customizadas.
        :param options: Argumentos adicionais para o Chrome.
        :return: Instância do webdriver.Chrome.
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--window-size=1920x1080")

        chrome_service = Service(
            executable_path=str(self.CHROME_DRIVER_PATH),
        )

        browser = webdriver.Chrome(
            service=chrome_service,
            options=chrome_options
        )

        # browser.set_window_position(-10000,0)
        return browser
    
    def search(self) -> list[tuple]:
        """
        Realiza a extração dos dados das tabelas de títulos do Tesouro Direto.
        :return: Lista de tuplas com os dados extraídos.
        """
        wait = WebDriverWait(self.driver, 10)
        self.driver.execute_script("window.scrollTo(0, 550)")

        btn_switch = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#switchVerTabelas')
        ))
        btn_switch.click()

        table_rows1 = self.table_rows(1)
        # table_rows1 = self.card_rows(1)

        btn_resgate = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, self.button_resgatar)
        ))
        btn_resgate.click()
        
        table_rows2 = self.table_rows(2)
        # table_rows2 = self.card_rows(2)

        table_rows = list(chain(table_rows1, table_rows2))
        
        self.driver.quit()
        table_rows.sort(key= lambda x: x[0])
        return table_rows
    
    def card_rows(self, table_id) -> list[list[str]]:
        try:
            cards = self.driver.find_element(
                By.CSS_SELECTOR, self.selector_table.format(table_id)
            )
            
            h3 = cards.find_elements(By.TAG_NAME, 'h3')
            titles = [i.text.replace('\n', ' ').replace(' +', '+') for i in h3]

            span = cards.find_elements(By.TAG_NAME, 'span')
            filter_span = [x.text for x in span if x.text != '']

            content = self.content(filter_span)

            for index, x in enumerate(content):
                x.insert(0, titles[index]) 

            return content

        except Exception as exp:
            print("Exception occured", exp)

    def content(self, filter_span) -> list[list[str]]:
        step = 0
        content = []
        start_index = 0 if filter_span[0].isnumeric() == True else 1
        total_content = len(filter_span)

        for index in range(4, total_content, 4):
            end_index = index + step
            data = filter_span[start_index:end_index]
            if data != []:
                content.append(data)
            start_index = end_index
                
            if start_index < total_content\
                and filter_span[start_index].isnumeric() == False:
                start_index = start_index + 1
                step = step + 1
        return content

    def table_rows(self, table_index):
        """
        Extrai os dados de uma tabela específica da página.
        :param table_index: Índice da tabela a ser extraída.
        :return: Lista de tuplas com os dados da tabela.
        """
        temp_lines = []
        tabela = self.driver.find_element(By.CSS_SELECTOR, self.SELECTOR_TABLE.format(table_index))
        linhas = tabela.find_elements(By.TAG_NAME, 'tbody')

        sleep(2)
        for linha in linhas:
            # tr = linha.find_element(By.TAG_NAME, 'tr')
            # td = tr.find_elements(By.TAG_NAME, 'td')
            # span = td[0].find_element(By.TAG_NAME, 'span')
         
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
