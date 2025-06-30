# Yotool-NoSQL

## Como gerar as chaves de api:

Acesse: https://console.cloud.google.com/
Crie um projeto (ou use um existente).
No menu, vá em APIs e Serviços > Biblioteca.
Procure por YouTube Data API v3 e ative.
Vá em APIs e Serviços > Credenciais.
Clique em Criar credenciais > Chave de API.


## Como executar o projeto: 

1- Instale as dependências

```
pip install -r requirements.txt
```
2- Configure o .env

Crie um arquivo .env e adicione suas informações:

```
YOUTUBE_API_KEYS="chave_api1, chave_api2"
CHANNEL_URL="https://youtube.com/@<seu-canal>"
MONGO_URI="<URL de conexão do mongo>"
DB_NAME=<nome do banco>
SINCE=2024-01-01T00:00:00Z
TRANSCRIPTION_LANG=pt
TRANSCRIPTION_DIR=./transcricoes
```

