## Youtool-NoSQL

Este projeto utiliza a biblioteca `youtool` para coletar, processar e armazenar dados de canais do YouTube em um banco de dados NoSQL (MongoDB), permitindo análises sobre vídeos, estatísticas, comentários e transcrições.


### Funcionalidades

- Coleta de informações de um canal específico
- Armazenamento de dados dos vídeos (detalhes, estatísticas)
- Coleta e armazenamento de comentários dos vídeos
- Download e simplificação de transcrições (legendas)
- Exportação de estatísticas em JSON

#### Pré-requisitos

- Python 3.8+
- Conta no [Google Cloud Console](https://console.cloud.google.com/)
- MongoDB (local ou Atlas)
- Biblioteca `youtool` instalada


<details>
 <summary>
  ❔ Como gerar as chaves da API do YouTube
 </summary>

</br>

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto (ou use um existente)
3. Vá até **APIs e serviços > Biblioteca**
4. Pesquise por **YouTube Data API v3** e ative-a
5. Vá até **APIs e serviços > Credenciais**
6. Clique em **Criar credenciais > Chave de API**
7. Copie a chave gerada e adicione ao seu `.env`

</details>


### Tecnologias Utilizadas
- Python
- MongoDB (NoSQL)
- YouTube Data API v3
- youtool
- yt-dlp (para baixar transcrições)
- webvtt-py (para processar arquivos VTT)


</br>


<details>
 <summary>
  ⚙️ Como executar o projeto
 </summary>
 
#### 1. Clone o repositório

```bash
git clone https://github.com/pedrohenribeiro/Youtool-NoSQL.git
cd youtool-nosql
```

#### 2. Instale as dependências

```
pip install -r requirements.txt
```

Certifique-se de instalar também as bibliotecas opcionais para transcrições:
```
pip install yt-dlp webvtt-py
```

#### 3. Configure o arquivo .env
Renomeie o arquivo `.env_example` para `.env` e o modifique com as suas informações

```
YOUTUBE_API_KEYS="chave_api1, chave_api2"
CHANNEL_URL="https://youtube.com/@<seu-canal>"
MONGO_URI="<URL de conexão do mongo>"
DB_NAME=<nome do banco>
SINCE=2024-01-01T00:00:00Z
TRANSCRIPTION_LANG=pt
TRANSCRIPTION_DIR=./transcricoes
```

#### 4. Execute o projeto

```
python app.py
```

</details>



<details>
 <summary>
  📋 Estrutura dos dados e observações
 </summary>

#### Estrutura dos dados no MongoDB

- channels: dados do canal (ID, título, descrição, etc.)
- videos: metadados dos vídeos (título, duração, visualizações, etc.)
- comments: comentários dos vídeos
- transcriptions: transcrições simplificadas dos vídeos

#### Observações
- As estatísticas dos vídeos são exportadas para um arquivo `estatisticas_videos.json`. Contém título, data de publicação, visualizações, likes e número de comentários.
- O script coleta no máximo 10 vídeos por execução (ajustável).
- As transcrições dependem da disponibilidade no YouTube e da linguagem escolhida.
- É possível usar múltiplas chaves de API (separadas por vírgula) para evitar limites de cota.

</details>



</br>



|Nome | GitHub|
| -------- | -------- |
|**Maria Luiza Guedes**| [![](https://bit.ly/3f9Xo0P)](https://github.com/mluizaguedes)|
|**Pedro Henrique Ribeiro**| [![](https://bit.ly/3f9Xo0P)](https://github.com/pedrohenribeiro)|
|**Sofia Matos Lessa**|[![](https://bit.ly/3f9Xo0P)](https://github.com/sofialessaa)|
