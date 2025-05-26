from string import Template
from pathlib import Path
from re import sub

class Message:
    """
    Classe responsável por montar o corpo do e-mail em HTML com as informações dos títulos.
    """
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
        """
        Inicializa a mensagem com as movimentações recentes.
        :param moves: Lista de tuplas com movimentações.
        """
        self.moves = self._rows(moves)
        pass

    def create(self, pref: list[tuple]):
        """
        Cria o corpo do e-mail substituindo os placeholders do template HTML.
        :param pref: Lista de tuplas com preferências do usuário.
        :return: String HTML do e-mail.
        """
        with open (self.PATH, 'r', encoding='utf-8') as file:
            text_message = file.read()
            return Template(text_message)\
                    .substitute(
                        moves = ''.join(x for x in self.moves),
                        prefer = ''.join(y for y in self._rows(pref))
                    )

    def _rows(self, table: list[tuple]) -> list[str]:
        """
        Formata as linhas da tabela em HTML.
        :param table: Lista de tuplas com dados.
        :return: Lista de strings HTML.
        """
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
        """
        Aplica estilos de cor e sinal de variação à linha.
        :param item: Tupla de dados.
        :return: Tupla estilizada.
        """
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
        """
        Define a cor de fundo da linha de acordo com o tipo de título.
        :param name_row: Nome do título.
        :return: String com a cor.
        """
        for key, color in self.ref_cor.items():
            if key in name_row:
                return color
        return 'white'