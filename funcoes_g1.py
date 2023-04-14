import os
import gspread
import requests
import pandas as pd
from pandas import DataFrame
from oauth2client.service_account import ServiceAccountCredentials

## integração com o sheets
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
tabela = api.open_by_key("1iJivj5y2pbfHpMR9C2CuPXIqNT9Wxa6Q06VjDxuRraA").worksheet("opa")
dados = tabela.get_all_values()
planilha = pd.DataFrame(dados[1:], columns=dados[0])

## tratar colunas vagas e salário pra transformar em valores numéricos
planilha['vagas'] = planilha['vagas'].replace('', 0)
planilha['vagas'] = planilha['vagas'].astype(int)
planilha['salario'] = planilha['salario'].replace('^R\$ |^R4 +|(?<= )R\$|(?<= )R4|/hora aula|/hora', '', regex=True)
planilha['salario'] = planilha['salario'].replace('', 0)
planilha['salario'] = planilha['salario'].str.replace('.', '')
planilha['salario'] = planilha['salario'].str.replace(',', '.')
planilha['salario'] = planilha['salario'].astype(float)


### criar queries e filtros

# filtros
aberto = planilha.query('tipo == "aberto"')
aguardando = planilha.query('tipo == "aguardando"')
publicado = planilha.query('tipo == "publicado"')
prefeituras = planilha.query("instituicao.str.lower().str.contains('prefeitura')")
forcas_armadas = planilha.query("instituicao.str.lower().str.contains('exército|marinha|aeronáutica')")
policia = planilha.query("instituicao.str.lower().str.contains('polícia')")
superior = planilha.query("escolaridade.str.lower().str.contains('superior')")

# soma das vagas
vagas_aberto = aberto['vagas'].sum() 
vagas_aguardando = aguardando['vagas'].sum()
vagas_publicado = publicado['vagas'].sum()
vagas_prefeituras = prefeituras['vagas'].sum()
vagas_forcas = forcas_armadas['vagas'].sum()
vagas_policia = policia['vagas'].sum()
vagas_superior = superior['vagas'].sum()

# número de concursos
num_aberto = len(aberto)
num_aguardando = len(aguardando)
num_publicado = len(publicado)
num_prefeituras = len(prefeituras)
num_forcas = len(forcas_armadas)
num_policia = len(policia)
num_superior = len(superior)

# amostra de links
links_aberto = aberto.sample(n=5, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_aguardando = aguardando.sample(n=2, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_publicado = publicado.sample(n=5, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_prefeituras = prefeituras.sample(n=2, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_forcas = forcas_armadas.sample(n=2, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_policia = policia.sample(n=2, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)
links_superior = superior.sample(n=2, replace=False).sort_values(by='vagas', ascending=False)['link'].reset_index(drop=True)

# concursos abertos com o maior salário e o maior número de vagas
maior_salario = planilha['salario'].max()
mais_vagas = planilha['vagas'].max()


## funcoes de resposta do telegram

def bot1():
  mensagem_bot = f'Pelo menos <b>{num_aberto}</b> concursos públicos estão com inscrições abertas hoje. \nJuntos, eles oferecem <b>{vagas_aberto}</b> vagas.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os maiores nos links abaixo: {links_aberto}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def bot2():
  mensagem_bot = f'Pelo menos <b>{num_aguardando}</b> concursos públicos foram anunciados, mas ainda aguardam edital.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os principais nos links abaixo: {links_aguardando}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def bot3(): 
  mensagem_bot = f'Pelo menos <b>{num_publicado}</b> ceditais estão estão publicados, mas as inscrições ainda não começaram. \nJuntos, eles oferecem <b>{vagas_publicado}</b> vagas.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os maiores nos links abaixo: {links_publicado}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def prefeitura():
  mensagem_bot = f'Pelo menos <b>{num_prefeituras}</b> editais estão com inscrições abertas para <u>prefeituras</u> em todo o Brasil. \nJuntos, eles oferecem <b>{vagas_prefeituras}</b> vagas.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os concursos abertos nos links abaixo: {links_prefeituras}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def policia():
  mensagem_bot = f'Pelo menos <b>{num_policia}</b> concursos públicos estão com inscrições abertas para a <u>polícia</u> em todo o Brasil. \nJuntos, eles oferecem <b>{vagas_policia}</b> vagas.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os maiores nos links abaixo: {links_policia}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def forcas():
  mensagem_bot = f'Pelo menos <b>{num_forcas}</b> concursos públicos estão com inscrições abertas para as <u>Forças Armadas<u/>. \nJuntos, eles oferecem <b>{vagas_forcas}</b> vagas.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os maiores nos links abaixo: {links_forcas}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)

def superior():
  mensagem_bot = f'Pelo menos <b>{num_superior}</b> concursos públicos estão com inscrições abertas para <b>{vagas_superior}</b> vagas de <u>ensino superior</u>.'
  lista_mensagem = f'{chr(0x1F4DA)} Veja os cmaiores nos links abaixo: {links_superior}'
  g1 = f'{chr(0x1F4A1)} Para saber mais e ver todos os concursos abertos, é só entrar na <a href="https://especiais.g1.globo.com/economia/concursos-e-emprego/lista-de-concursos-publicos-e-vagas-de-emprego/">página especial do g1</a>.'
  return (mensagem_bot + '\n' + lista_mensagem + '\n' + g1)
