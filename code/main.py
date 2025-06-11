from datetime import time, datetime
from dotenv import load_dotenv
from email_delta import Email
from database import DataBase
from browser import Browser
from message import Message
from report import Report
from pathlib import Path
from users import Users
from re import sub, I
from time import sleep

load_dotenv(Path(__file__).parent / 'src' / 'env' / '.env')

class Main:
    """
    Classe principal que orquestra a execução do programa.
    """
    def __init__(self) -> None:
        """
        Inicializa as instâncias de Email, DataBase e Report.
        """
        self.email = Email()
        self.db = DataBase()
        self.report = Report()
        pass

    def hard_work(self):
        """
        Executa o fluxo principal: coleta dados, compara, atualiza banco, envia e-mails e registra logs.
        """
        try:
            self.db.open()
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
            self.db.close()

    def filter(self, infos_db: list[tuple], infos_site: list[tuple]):
        """
        Compara os dados do site com o banco e identifica atualizações e novos títulos.
        :param infos_db: Dados do banco.
        :param infos_site: Dados do site.
        :return: (dicionário de atualizações, lista de novos títulos)
        """
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
        """
        Calcula a variação percentual entre dois valores.
        :param new_value: Valor novo.
        :param old_value: Valor antigo.
        :return: Variação percentual.
        """
        new_value = float(sub(r'[A-Z !+%]', '', new_value.replace(',','.'), flags= I))
        old_value = float(sub(r'[A-Z !+%]', '', old_value.replace(',','.'), flags= I))

        return round((new_value - old_value), 2) 
    
    def init_db(self):
        """
        Inicializa o banco de dados com os dados atuais do site.
        """
        self.db.init(Browser().search())

if __name__ == '__main__':
    current_time = datetime.now()
    start_time = time(0, 30, 0, 0)
    stop_time = time(18, 0, 0, 0)
    main = Main()

    while current_time.time() < stop_time:
        if current_time.time() > start_time:
            main.hard_work()

        sleep(300)
        current_time = datetime.now()