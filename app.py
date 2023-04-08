##imports de bibliotecas
import os
import gspread
import requests
import pandas as pd
import numpy as np
import datetime 
from flask import Flask, request, render_template
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper
from bs4 import BeautifulSoup
from pandas import DataFrame
from datetime import date

## importar as funções de raspar os concursos e automatizar texto
from funcoes_concursos import raspa_concursos, automatiza_bot1, automatiza_bot2, automatiza_bot3, automatiza_site
mensagem_bot1 = automatiza_bot1()
mensagem_bot2 = automatiza_bot2()
mensagem_bot3 = automatiza_bot3()
mensagem_site = automatiza_site()

## preparando a integração com o telegram
TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

##preparando a integração com o google sheets
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode = "w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
planilha = api.open_by_key("1ZDyxhXlCtCjMbyKvYmMt_8jAKN5JSoZ7x3MqlnoyzAM")
sheet = planilha.worksheet("Sheet1")


##configurando o flask e preparando o site
app = Flask(__name__)

menu = """
<center><a href="/">Página inicial</a> | <a href="/concursos">Concursos Abertos</a></center>
"""

@app.route("/")
def index():
  return menu


@app.route("/concursos")
def concursos():
  concursos = concursos_abertos
  return render_template('concursos.html', df = concursos)


## Criar a resposta do Telegram

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  lista_entrada = ["/start", "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]
  lista_saida = ["obrigado", "obrigada", "valeu", "muito obrigado", "muito obrigada"]
  nova_mensagem = ' '
  if message.lower().strip() in lista_entrada:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Oi, seja muito bem-vindo(a) ao Bot do Concurso Público do site PCI Concursos! \n Escolha uma das opções abaixo: \n - Digite 1 para saber quantos concursos e quantas vagas estão abertos hoje; \n - Digite 2 para saber quantos concursos oferecem cadastro reserva; \n - Digite 3 para ver os editais de estágio abertos."}
  elif message == "1":
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot1}'}
  elif message == "2":
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot2}'}
  elif message == "3":
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot3}'}
  elif message.lower().strip() in lista_saida:
     nova_mensagem = {"chat_id" : chat_id, "text" : "Que isso! Até a próxima :)"}
  else:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Não entendi. Escreva 'oi' ou 'olá' para ver as instruções."}
  resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  print(resposta.text)
  return "ok"








