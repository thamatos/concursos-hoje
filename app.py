##imports de bibliotecas
import os
import gspread
import requests
import pandas as pd
import numpy as np
import datetime 
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper
from bs4 import BeautifulSoup
from pandas import DataFrame
from datetime import date

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

##função pra raspar os concursos

def raspa_concursos():
  url = "https://www.pciconcursos.com.br/ultimas/"
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  concursos = soup.findAll('div', {'class':'ca'})
  lista_orgao = []
  lista_cargo = []
  lista_escolaridade = []
  lista_salario = []
  lista_vagas = []
  lista_data_abertura = []
  lista_data_encerramento = []
  lista_estado = []
  lista_link = []

  for concurso in concursos:
    orgao=concurso.find('a').text
    div_cd=concurso.find('div', {'class':'cd'})
    lista_temporaria=str(div_cd).replace("<br/>", "|").replace("<span>", "").replace("</span>", "").replace('<div class="cd">', "").replace('[<div class="cd">', "").replace(', <div class="cd">', "").replace("</div>", "").replace("\n", "|").replace("/", ",").split("|")
    vagasesal=lista_temporaria[0]
    cargo=lista_temporaria[1]
    escolaridade=lista_temporaria[2]
    salario=vagasesal.split('R$')[-1].strip().replace('.', '').replace(',','.').replace('Vagas', '0').replace('h.a', '').replace('vagas', '')
    vagas=vagasesal.split('vaga')[0].strip().split(' ')[0].replace('.', '').replace(',','.').replace('Vagas', '0')
    #data=concurso.find('div', {'class':'ce'}).text
    data_abertura = concurso.find('div', {'class':'ce'}).text.split('a')[0].replace('Prorrog', '') #Limpando algumas sujeirinhas que vieram
    data_encerramento = concurso.find('div', {'class':'ce'}).text.split('a')[-1].replace('té', '') #Limpando algumas sujeirinhas que vieram
    if data_abertura == data_encerramento: #Quando só tem uma data, porque o concurso está aberto, o split espelha a mesma data nas duas variáveis. 
      data_abertura = ' ' #Por isso, criei essa condição pra deixar a abertura vazia quando fosse igual
    div_cc = concurso.find_all("div", {"class":"cc"})
    estado = str(div_cc).replace('<div class="cc">', '').replace("</div>", "")
    link = concurso.find('a').get('href')

    lista_orgao.append(orgao)
    lista_cargo.append(cargo)
    lista_escolaridade.append(escolaridade)
    lista_salario.append(salario)
    lista_vagas.append(vagas)
    lista_estado.append(estado)
    lista_link.append(link)
    lista_data_abertura.append(data_abertura)
    lista_data_encerramento.append(data_encerramento)

  dict_tabelaconcursos = {'Órgão': lista_orgao, 'Cargo': lista_cargo, 'Data_abertura': lista_data_abertura, 'Data_encerramento': lista_data_encerramento, 'Vagas' : lista_vagas, 'Salário' : lista_salario, 'Escolaridade': lista_escolaridade, 'Estado': lista_estado, 'Link': lista_link}
  df_concursos = pd.DataFrame(data = dict_tabelaconcursos)

  df_concursos2 = df_concursos[~df_concursos["Cargo"].str.contains('Estagiário')]
  data = date.today()

  return df_concursos2

raspagem = raspa_concursos()

#função pra automatizar o texto
 def automatiza_texto():
    tabela = raspagem
    tabela['Vagas'] =  tabela['Vagas'].astype(int)
    data_true_false =  tabela["Data_abertura"] == ' '
    tabela['Aberto'] = data_true_false
    df_abertos =  tabela.query(f'Aberto == True')
    concursos_abertos =len(df_abertos)
    soma_vagas = df_abertos['Vagas'].sum()
    mensagem_bot = f'Pelo menos {concursos_abertos} concursos públicos estão com inscrições abertas no site PCI Concursos. Juntos, eles oferecem {soma_vagas} vagas. Veja mais nos links abaixo: {tabela["Link"]}'
    return mensagem_bot

mensagem_bot = automatiza_texto()

@app.route("/concuros")
def concursos():
  tabela = raspagem
  tabela['Vagas'] =  tabela['Vagas'].astype(int)
  data_true_false =  tabela["Data_abertura"] == ' '
  tabela['Aberto'] = data_true_false
  df_abertos =  tabela.query(f'Aberto == True')
  concursos_abertos =len(df_abertos)
  soma_vagas = df_abertos['Vagas'].sum()
  mensagem_bot = f'Pelo menos {concursos_abertos} concursos públicos estão com inscrições abertas no site PCI Concursos. Juntos, eles oferecem {soma_vagas} vagas. Veja mais nos links abaixo: {tabela["Link"]}'
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
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot}'}
  elif message.lower().strip() in lista_saida:
     nova_mensagem = {"chat_id" : chat_id, "text" : "Que isso! Até a próxima :)"}
  else:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Não entendi. Escreva 'oi' ou 'olá' para ver as instruções."}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  
  return "ok"
