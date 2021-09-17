## Trabalho 1 de INF1407 - Programação para a Web
Componentes do Grupo:
Paulo Vitor Libório  
Kevin Abreu  
# Sobre mooncell
Como forma de descontrair, tanto o nome do repositório quanto a nomenclatura de algumas funções presentes 
no projeto de server simples, são baseadas na série em anime Fate/EXTRA Last Encore, disponível no Netflix. 
Esperamos que isso não atrapalhe o entendimento de nenhuma parte do código.

# Configurar o Servidor

# Iniciar Servidor
Com o arquivo config.py devidamente setado.

```bash
python3 mooncell.py
```
# O que testamos
Conexão simultânea de mais de um cliente.
Como o código do mooncell possui um "time.sleep(30)", o mesmo processo é incapaz de lidar com 2 requests dentro
desse mesmo intervalo.
Dito isto um teste simples é abrir dois terminais e rodar o comando abaixo dentro do intervalo de tempo.
```bash
curl http://localhost:<PORTA_ESCOLHIDA_EM_CONFIG>/index.html
```
Caso houvesse um processo único cuidando de tudo, a resposta no segundo terminal só ocorreria após o intervalo de sleep passar.

# O que não funcionou dentro do que foi testado