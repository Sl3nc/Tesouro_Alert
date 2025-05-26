from os import getenv
from datetime import datetime
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email:
    """
    Classe responsável pelo envio de e-mails via SMTP.
    """
    def __init__(self) -> None:
        """
        Inicializa as configurações do servidor SMTP a partir das variáveis de ambiente.
        """
        self.smtp_server = getenv("SMTP_SERVER","")
        self.smtp_port = getenv("SMTP_PORT", 0)

        self.smtp_username = getenv("EMAIL_SENDER","")
        self.smtp_password = getenv("PASSWRD_SENDER","")
        pass

    def send(self, texto_email: str, to: str) -> None:
        """
        Envia um e-mail HTML para o destinatário.
        :param texto_email: Corpo do e-mail em HTML.
        :param to: E-mail do destinatário.
        """
        mime_multipart = MIMEMultipart()
        mime_multipart['From'] = self.smtp_username
        mime_multipart['To'] = to
        mime_multipart['Subject'] = f'Atualização Tesouro Direto {datetime.strftime(datetime.now(), "%d/%m - %H:%M")}'

        mime_multipart.attach(MIMEText(texto_email, 'html', 'utf-8'))

        self._open_server(mime_multipart)

    def _open_server(self, mime_multipart: MIMEMultipart) -> None:
        """
        Realiza a conexão com o servidor SMTP e envia a mensagem.
        :param mime_multipart: Mensagem MIME a ser enviada.
        """
        with SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(mime_multipart)