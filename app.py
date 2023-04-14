##importar as bibliotecas
import os
import requests
import gspread
import pandas as pd
import numpy as np
from flask import Flask, request, render_template
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
from pandas import DataFrame

from funcoes_g1 import bot1, bot2, bot3, prefeitura, policia, forcas, superior
mensagem1 = bot1()
mensagem2 = bot2()
mensagem3 = bot3()
mensagem4 = prefeitura()
mensagem5 = policia()
mensagem6 = forcas()
mensagem7 = superior()

## preparando a integração com o telegram
TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

##configurando o flask e preparando o site
app = Flask(__name__)

menu = """
<center><a href="/">Volte ao menu</a> | <a href="/concursos">Concursos Abertos</a> | <a href="/reserva">Cadastro Reserva</a> | <a href="/estagio">Vagas de Estágio</a>    </center>
"""

@app.route("/")
def index():
  titulo = 'Concursos públicos'
  texto = 'Veja as opções de editais com vagas abertas hoje:'
  return render_template('inicio.html', titulo=titulo, texto=texto)


@app.route("/concursos")
def concursos():
  texto_site = automatiza_site()
  return menu + render_template('concursos.html', dados=texto_site, titulo='Concursos Abertos')

@app.route("/reserva")
def reserva():
  texto_reserva = automatiza_reserva()
  return menu + render_template('concursos.html', dados=texto_reserva, titulo='Cadastro Reserva')

@app.route("/estagio")
def estagio():
  texto_estagio = automatiza_estagio()
  return menu + render_template('concursos.html', dados=texto_estagio, titulo='Vagas de estágio')

## telegram

## Criar a resposta do Telegram
@app.route("/telegram-bot", methods=["POST"])

def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  nome = update["message"]["from"]["first_name"]
  message = update["message"]["text"]
  lista_entrada = ["/start", "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]
  lista_saida = ["obrigado", "obrigada", "valeu", "muito obrigado", "muito obrigada", "opa", "legal", "show", "bacana"]
  
  nova_mensagem = ' '
  
  if message.lower().strip() in lista_entrada:
    texto_mensagem = f"""
    Oi, {nome} seja muito bem-vindo(a) ao Bot de Concursos Públicos do g1! 
    \n {chr(0x1F4DA)}Escolha uma das opções abaixo:
    <ul>
      <li>Digite 1 para saber quantos concursos e quantas vagas estão abertos hoje;</li>
      <li>Digite 2 para saber quantos editais estão publicados, mas as inscrições ainda não abriram;</li>
      <li>Digite 3 para ver os concursos que já foram anunciados, mas ainda não têm editais;</li>
    </ul>
    """
 
  elif message == "1":
    texto_mensagem = '''Ótimo, temos uma lista com todos os concursos abertos, mas também uma divisão por categorias. 
    \n Digite qual das opções você prefere:
    <ul>
      <li>lista inteira</li>
      <li>categorias</li>
    </ul>
    '''
 
  elif message == "\lista inteira":
    texto_mensagem = f'{mensagem1} \n Se quiser fazer outras consultas, é só digitar menu'

  elif message == "\categorias":
    texto_mensagem = '''
    Beleza, então essas são as categorias disponíveis. Digite qual delas quer acessar: \n
     <ul>
      <li>polícia</li>
      <li>forças armadas</li>
      <li>prefeituras</li>
      <li>ensino superior</li>
     </ul>
    '''
    
    
  elif message == "prefeituras":
     texto_mensagem = f' {mensagem4} \n Se quiser fazer outras consultas, é só digitar menu'

  elif message == "forças armadas":
     texto_mensagem = f'  {mensagem6} \n Se quiser fazer outras consultas, é só digitar menu' 

  elif message == "polícia":
    texto_mensagem = f'  {mensagem5} \n Se quiser fazer outras consultas, é só digitar menu'

  elif message == "ensino superior":
    texto_mensagem = f' {mensagem7} \n Se quiser fazer outras consultas, é só digitar menu'
  
  elif message == "2":
    texto_mensagem = f'{mensagem2} \n Se quiser fazer outras consultas, é só digitar menu'
  
  elif message == "3":
    texto_mensagem = f'{mensagem3} \n Se quiser fazer outras consultas, é só digitar menu'
  
  elif message.lower().strip() in lista_saida:
    texto_mensagem = "Que isso! Até a próxima :)"
    
  else:
    texto_mensagem = "Não entendi. Aperte o botão \menu para voltar e ver as instruções."
    
  nova_mensagem = {"chat_id" : chat_id, "text" : texto_mensagem,  "parse_mode" : 'HTML'}
  
  resposta = requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  
  print(resposta.text)
  return "ok"
