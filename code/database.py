from pathlib import Path
from sqlite3 import connect

class DataBase:
    """
    Classe responsável pelo gerenciamento do banco de dados SQLite dos títulos.
    """
    FOLDER_DB = Path(__file__).parent / 'src'/'db'/ 'tesouro_db.sqlite3'
    TABLE_LATE = 'Infos_Late'
    TABLE_OLD = 'Infos_Const'

    def __init__(self) -> None:
        """
        Inicializa a conexão e os comandos SQL.
        """
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

        pass

    def open(self):
        """
        Abre a conexão com o banco de dados
        """
        self.connection = connect(self.FOLDER_DB)
        self.cursor = self.connection.cursor()

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.cursor.close()
        self.connection.close()

    def init(self, infos_site: list[tuple]):
        """
        Inicializa o banco de dados com os dados extraídos do site.
        :param infos_site: Lista de tuplas com dados do site.
        """
        for item in infos_site:
            self.cursor.execute(
                self.insert_late,
                (item[0], item[1], item[2], item[3], item[4], item[5])
            )
        self.connection.commit()

    def query(self) -> list[tuple]:
        """
        Consulta os dados atuais do banco.
        :return: Lista de tuplas com os dados.
        """
        self.cursor.execute(
            self.query_late
        )
        return self.cursor.fetchall()
    
    def insert(self, data_site) -> None:
        """
        Insere novos dados no banco.
        :param data_site: Lista de tuplas a serem inseridas.
        """
        for item in data_site:
            self.cursor.execute(
                self.insert_late,
                (item[0], item[1], item[2], item[4], item[5], item[6])
            )
            self.connection.commit()
    
    def update(self, move: dict[str,tuple]):
        """
        Atualiza dados existentes no banco.
        :param move: Dicionário {id: tupla de dados atualizados}
        """
        for id, item in move.items():
            self.cursor.execute(
                self.update_late,
                (item[0], item[1], item[2], item[4], item[5], item[6], id)
            )
            self.connection.commit()
