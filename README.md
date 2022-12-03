# tweet-collector

Este repositório possui o código responsável pela coleta e armazenamento de dados de um tweet. Contém os seguintes arquivos:
- `collect.py`: funções para coleta e armazenamento de dados de um tweet no Amazon S3, incluindo uma função configurada para ser executada no AWS Lambda.
- `deploy.sh`: script de deploy da imagem do container da função Lambda que executa a coleta e o armazenamento para o Amazon ECR.
- `Dockerfile`: configura o container utilizado para deploy da função Lambda.

## Execução local do script

Para executar o script de coleta, é necessário Python 3 e instalar as dependências definidas no arquivo `requirements.txt`.

```
$ pip install -r requirements.txt
```

Também são necessárias chaves de acesso da API do Twitter, que devem ser substituídas nas constantes `consumer_key`, `consumer_secret` e `bearer_token`. 

Para escolher o tweet a ser coletado, é necessário substituir os valores de entrada das funções na execução local:
```
if __name__ == "__main__":
    tweet_data = get_tweet_data("ID_DO_TWEET")
    json.dump(tweet_data, open("tweet.json", "w"))

    retweets_data = get_retweets_data("ID_DO_TWEET")
    json.dump(retweets_data, open("retweets.json", "w"))

    same_text_tweets_data = get_same_text_tweets_data(tweet_data['full_text'], tweet_data['id'])
    json.dump(same_text_tweets_data, open("same_text_tweets.json", "w"))

    quote_tweets_data = get_quote_tweets("ID_DO_TWEET")
    json.dump(quote_tweets_data, open("quote_tweets.json", "w"))

    replies_data = get_replies("ID_DO_TWEET", tweet_data['user']['screen_name'])
    json.dump(replies_data, open("replies.json", "w"))
```

Após a configuração inicial, basta executar:
```
$ python3 collect.py
```

Os dados serão salvos em arquivos `.json` na raiz do projeto.

# Deploy do script para AWS

Requisitos:
- [Docker](https://www.docker.com/)
- [AWS CLI](https://aws.amazon.com/pt/cli/) configurada

Para subir a imagem da função lambda, basta executar na raiz do projeto:

```
$ ./deploy.sh
```
