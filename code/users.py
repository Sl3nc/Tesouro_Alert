from bisect import bisect_left
from copy import deepcopy
from pathlib import Path
from json import load

class Users:
    """
    Classe responsável por gerenciar as preferências dos usuários cadastrados.
    """
    PATH = Path(__file__).parent / 'src' / 'json' / 'users.json'

    def __init__(self):
        """
        Carrega as preferências dos usuários a partir de um arquivo JSON.
        """
        with open(self.PATH, 'r') as file:
            self.data = load(file)
        pass

    def prefers(self, moves: list[tuple], infos_db: list[tuple]) -> dict[str, list[tuple]]:
        """
        Retorna um dicionário com os dados preferidos de cada usuário.
        :param moves: Lista de tuplas com movimentações recentes.
        :param infos_db: Lista de tuplas com dados do banco.
        :return: Dicionário {email: [preferências encontradas]}
        """
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
        """
        Busca um título específico nas listas fornecidas.
        :param user_data: Preferência do usuário.
        :param base_data: Lista de dados para busca.
        :return: Tupla com os dados encontrados ou None.
        """
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
