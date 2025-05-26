from datetime import datetime
from pathlib import Path

class Report:
    """
    Classe responsável por registrar logs de operações, erros e envios de e-mails.
    """
    path = Path(__file__).parent / 'src' /'doc' / 'relatório_emails.txt'
    
    def __init__(self) -> None:
        pass

    def is_error(self, message):
        """
        Registra um erro ocorrido.
        :param message: Mensagem de erro.
        """
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write(f'Erro ocorrido: {message}')
            file.write('\n')

    def is_send(self, email: str):
        """
        Registra o envio de um e-mail.
        :param email: E-mail do destinatário.
        """
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Email enviado às ' + datetime.strftime(datetime.now(), '%d/%m - %H:%M') + '\n'
            )
            file.write(f'- {email} \n')
            file.write('\n')

    def is_new(self, unfound: list[tuple]):
        """
        Registra linhas adicionadas ao banco.
        :param unfound: Lista de tuplas adicionadas.
        """
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Linhas Adcionadas:\n')
            for row in unfound:
                file.write(row[0])
            file.write('\n')

    def is_updated(self, outdated: dict[str, tuple]):
        """
        Registra linhas atualizadas no banco.
        :param outdated: Dicionário de linhas atualizadas.
        """
        with open(self.path, 'a', encoding= 'utf-8') as file:
            file.write('\n' + '#'*10 + '\n')
            file.write('Linhas Atualizadas:\n')
            for row in outdated.values():
                file.write(row[0])
            file.write('\n')
