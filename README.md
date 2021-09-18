# mooncell

## Trabalho 1 de INF1407 - Programação para a Web
Componentes do Grupo:

* Paulo Vitor Libório  
* Kevin Abreu  

## Sobre mooncell
Como forma de descontrair, tanto o nome do repositório quanto a nomenclatura de algumas funções presentes 
no projeto de webserver são baseadas na série em anime fate/EXTRA Last Encore disponível no Netflix. 
Esperamos que isso não atrapalhe o entendimento de nenhuma parte do código.

## Configurar o Servidor

Opções de configuração:

* SERVER_PORT: Porta que irá escutar as requisições ao servidor

* ROOT_DIR: Diretório raiz de onde serão servidos os arquivos

* ERROR_PAGE: Página default para o erro 404 - página não encontrada

* DEFAULT_FILES: Arquivos padrão para servir requisições sem extensão de arquivo

* MESSAGE_NOT_SUPPORTED: Mensagem para requisições de arquivos não suportados pelo servidor

## Iniciar Servidor
Com o arquivo config.py devidamente configurado.

```bash
python3 mooncell.py
```
## O que testamos

Conexão simultânea de mais de um cliente.
Como o código do mooncell possui um "time.sleep(30)", o mesmo processo é incapaz de lidar com 2 requests dentro
desse mesmo intervalo.
Dito isto um teste simples é abrir dois terminais e rodar o comando abaixo dentro do intervalo de tempo.
```bash
curl http://localhost:<PORTA_ESCOLHIDA_EM_CONFIG>/index.html
```
Caso houvesse um processo único cuidando de tudo, a resposta no segundo terminal só ocorreria após o intervalo de sleep passar.

## O que não funcionou dentro do que foi testado

Não foi possível rodar o webserver em ambiente Windows.