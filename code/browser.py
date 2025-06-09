from pathlib import Path
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class Browser:
    """
    Classe responsável por automatizar a navegação e extração de dados do site do Tesouro Direto usando Selenium.
    """
    ROOT_FOLDER = Path(__file__).parent
    CHROME_DRIVER_PATH = ROOT_FOLDER / 'src' / 'drivers' / 'chromedriver.exe'
    SELECTOR_TABLE = '#td-precos_taxas-tab_{0} > div > div.td-mercado-titulos__content > table'
    button_resgatar = 'body > main > div.td-precosTaxas > div:nth-child(2) > div > div > ul > li:nth-child(2)'
    LINK = 'https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm'

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
        chrome_options = Options()
        # chrome_options.add_argument('--headless')

        chrome_service = Service(
            executable_path=str(self.CHROME_DRIVER_PATH),
        )

        browser = webdriver.Chrome(
            service=chrome_service,
            options=chrome_options
        )

        browser.minimize_window()
        browser.set_window_position(-10000,0)
        return browser
    
    def search(self) -> list[tuple]:
        """
        Realiza a extração dos dados das tabelas de títulos do Tesouro Direto.
        :return: Lista de tuplas com os dados extraídos.
        """
        table_lines = []
        self.driver.execute_script("window.scrollTo(0, 250)")
        table_lines = self._pull_data(1)

        self.driver.find_element(By.CSS_SELECTOR, self.button_resgatar).click()
        table_lines = table_lines + self._pull_data(2)
        
        self.driver.quit()
        table_lines.sort(key= lambda x: x[0])
        return table_lines

    def _pull_data(self, table_index):
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
