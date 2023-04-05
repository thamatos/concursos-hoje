#Importar bibliotecas para raspar e automatizar texto

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime 
from datetime import date

#função pra raspar os concursos

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


#função pra automatizar o texto

def automatiza_bot():
  tabela = raspa_concursos()
  tabela['Vagas'] =  tabela['Vagas'].astype(int)
  data_true_false =  tabela["Data_abertura"] == ' '
  tabela['Aberto'] = data_true_false
  df_abertos =  tabela.query(f'Aberto == True')
  concursos_abertos =len(df_abertos)
  soma_vagas = df_abertos['Vagas'].sum()
  mensagem_bot = f'Pelo menos {concursos_abertos} concursos públicos estão com inscrições abertas no site PCI Concursos. Juntos, eles oferecem {soma_vagas} vagas.'
  lista_mensagem = f'Veja mais nos links abaixo: {df_abertos["Link"]}'
  return(mensagem_bot + lista_mensagem)

 def automatiza_site():
    tabela = raspa_concursos()
    tabela['Vagas'] =  tabela['Vagas'].astype(int)
    data_true_false =  tabela["Data_abertura"] == ' '
    tabela['Aberto'] = data_true_false
    df_abertos =  tabela.query(f'Aberto == True')
    concursos_abertos =len(df_abertos)
    soma_vagas = df_abertos['Vagas'].sum()
    lista = df_abertos["Link"].tolist()
    html = ''
    for elemento in lista:
      html += '<a href="' + elemento + '">' + elemento + '</a><br>'
    mensagem_site = f'''
    <h1>Bot dos concursos</h1>
    <p>
    Pelo menos {concursos_abertos} concursos públicos estão com inscrições abertas no site PCI Concursos. Juntos, eles oferecem {soma_vagas} vagas. Veja mais nos links abaixo:.
    <br>
    {html}   
    </p>
    '''
    return(mensagem_site)

