# Tesouro Alert

Tesouro Alert é um sistema automatizado para monitoramento de títulos do Tesouro Direto. Ele coleta informações do site oficial, compara com um banco de dados local, identifica variações e envia alertas personalizados por e-mail para os usuários cadastrados, de acordo com suas preferências.

## Funcionalidades

- **Coleta automática de dados** do site do Tesouro Direto utilizando Selenium.
- **Armazenamento e atualização** dos dados em um banco SQLite.
- **Comparação de variações** de rentabilidade dos títulos.
- **Envio de e-mails automáticos** para usuários cadastrados, com informações relevantes e personalizadas.
- **Registro de logs** de operações, erros e envios.

## Estrutura do Projeto

- `code/index.py`: Código principal do sistema.
- `src/drivers/chromedriver.exe`: Driver do Chrome para automação Selenium.
- `src/json/users.json`: Preferências dos usuários.
- `src/db/tesouro_db.sqlite3`: Banco de dados SQLite.
- `src/doc/base_message.html`: Template HTML do e-mail.
- `src/doc/relatório_emails.txt`: Log de operações.
- `src/env/.env`: Variáveis de ambiente (credenciais SMTP, etc).

## Como funciona

1. O sistema acessa o site do Tesouro Direto e extrai as informações dos títulos.
2. Compara os dados extraídos com o banco local, identificando novos títulos ou variações.
3. Atualiza o banco de dados conforme necessário.
4. Para cada usuário cadastrado, monta um e-mail personalizado com base em suas preferências.
5. Envia os e-mails utilizando as credenciais SMTP configuradas.
6. Registra logs de todas as operações realizadas.

## Como usar

### Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- Instalar dependências:
  ```
  pip install selenium python-dotenv
  ```
- Baixar o `chromedriver.exe` compatível com sua versão do Chrome e colocar em `src/drivers/`.

### Configuração

1. Configure as variáveis de ambiente no arquivo `src/env/.env`:
    ```
    SMTP_SERVER=smtp.seuServidor.com
    SMTP_PORT=porta do seu serviço SMTP
    EMAIL_SENDER=seu@email.com
    PASSWRD_SENDER=suaSenha
    ```
2. Cadastre os usuários e suas preferências em `src/json/users.json`.

### Execução

Execute o programa principal:
```
python code/index.py
```

### Inicialização do banco de dados

Para inicializar o banco de dados com os dados atuais do site, utilize o método `init_db()` da classe `Main`.

## Observações

- O envio de e-mails depende de um servidor SMTP válido.
- O sistema utiliza Selenium, portanto o Chrome e o chromedriver devem estar corretamente instalados.
- Os logs de operação são salvos em `src/doc/relatório_emails.txt`.

## Licença

Este projeto é de uso pessoal e educacional.