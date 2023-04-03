##imports de bibliotecas
import os
import gspread
import requests
import funcoes_concursos
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper

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
<center><a href="/">Página inicial</a> |  <a href="/concursos">Concursos Abertos</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a></center>
"""

@app.route("/")
def index():
  return menu

@app.route("/sobre")
def sobre():
  return menu + "Site desenvolvido para a disciplina de Algoritmos de Automação do Master de Jornalismo de Dados, Automação e Data storytelling do Insper. "

@app.route("/contato")
def contato():
  return menu + "Para me contatar, pode acessar meu github: https://github.com/thamatos ou chamar no e-mail: thais.matos.pinheiro@alumni.usp.br"

@app.route("/concuros")
def concursos():
  return menu + mensagem_bot


#Resposta telegram

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  lista_entrada = ["/start", "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]
  lista_saida = ["obrigado", "obrigada", "valeu", "muito obrigado", "muito obrigada"]
  
  if message.lower().strip() in lista_entrada:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Oi, seja muito bem-vindo(a) ao Bot do Concurso Público do site PCI Concursos! \n Se você quiser saber quantos concursos e quantas vagas estão abertos hoje, digite 1"}
  elif message == "1":
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot}'
  elif message.lower().strip() in lista_saida:
     nova_mensagem = {"chat_id" : chat_id, "text" : "Que isso! Até a próxima :)"}
  else:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Não entendi. Escreva 'oi' ou 'olá' para ver as instruções."}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  return "ok"
