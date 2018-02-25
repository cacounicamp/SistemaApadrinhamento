import os
import json
import shutil
from estudantes import *
from enum import Enum, auto
from datetime import datetime


def limpar_telefone(string):
   """Substitui caracteres comuns na string que representa um telefone"""
   return string.replace('(', '').replace(')', '').replace(' ', '') \
   .replace('+', '').replace('-', '')


def dict_to_lista(dict):
   # Criamos uma nova dict
   nova_lista = []

   # Para cada estudante..
   for estudante in dict.values():
      # Transformamos em dicionário, sem perder informações para o futuro
      # construtor
      nova_lista.append(estudante.to_dict())

   # Retornamos a lista
   return nova_lista


def lista_to_dict(tipo, lista):
   # Criamos um novo dicionário
   novo_dict = {}

   # Para cada dicionário de estudante..
   for dict_estudante in lista:
      estudante = None

      # Verificamos se trata-se de um(a) veteranx
      if tipo == Tipo.VETERANX:
         # Criamos um(a) veteranx
         estudante = Veteranx(dict_estudante)
      else:
         # Criamos um(a) ingressante
         estudante = Ingressante(dict_estudante)

      # Adicionamos ao dicionário na forma de pares (identificador, estudante)
      novo_dict[estudante.id] = estudante

   # Retornamos o dicionário
   return novo_dict


def data_a_partir_formulario(string):
    """Transforma a string que representa o horário no formulário do Google em
    um objeto datetime de Python, assim podemos comparar 2 datas"""
    return datetime.strptime(string, '%d/%m/%Y %H:%M:%S')


def deve_atualizar_estudante(dicionario, estudante):
   """Função compara a data do dicionário que representa o estudante que já
   está no banco de dados.
   Retorna 'True' no caso do dicionário ser mais novo que os dados do
   estudante."""
   return data_a_partir_formulario(dicionario['data_formulario']) > \
      data_a_partir_formulario(estudante.data_formulario)


class AdicaoResultado(Enum):
   """Classe para informar o resultado da adição de um estudante ao banco de
   dados"""
   ADICIONADO  = auto()
   ATUALIZADO  = auto()
   MANTIDO     = auto()


class Database:
   """Classe que armazena todas as funções de leitura, gravação e adição de
   estudantes através de um banco de dados simples em JSON"""

   # Definimos o nome do arquivo do banco de dados
   NOME_ARQUIVO = 'sist_apadrinhamento.json'
   # Nome das estruturas no arquivo
   DICT_VETERANXS = 'veteranxs'
   DICT_INGRESSANTES = 'ingressantes'
   DICT_APADRINHAMENTOS = 'apadrinhamentos'
   ID_VETERANXS = 'ultimo_id_veteranxs'
   ID_INGRESSANTES = 'ultimo_id_ingressantes'

   def __init__(self):
      # Definimos o banco de dados padrão
      # Em JSON, serão lidos como listas; em Python, como dicionários.
      self.dados = {
         Database.DICT_VETERANXS: {},
         Database.ID_VETERANXS: 0,
         Database.DICT_INGRESSANTES: {},
         Database.ID_INGRESSANTES: 0,
         # Chave: identificador dx veteranx, valor: lista de identificadores de
         # ingressantes
         Database.DICT_APADRINHAMENTOS: {}
      }

      # Verificamos se o banco de dados existe
      if os.path.exists(Database.NOME_ARQUIVO):
         # Lemos o estado atual do banco de dados
         self.ler_banco()

      # Adicionamos essa instance para uma variável estática em Estudante
      Estudante.database = self

   def ingressantes(self):
      """Pares (id de ingressante, estrutura Ingressante)"""
      return self.dados.get(Database.DICT_INGRESSANTES)

   def veteranxs(self):
      """Pares (id de veteranx, estrutura Veteranx)"""
      return self.dados.get(Database.DICT_VETERANXS)

   def apadrinhamentos(self):
      """Pares (id de veteranx, lista de ids de ingressantes)"""
      return self.dados.get(Database.DICT_APADRINHAMENTOS)

   def veteranx(self, id_):
      """Procura no banco de dados x veteranxs com id dado"""
      return self.veteranxs().get(id_)

   def afilhadxs(self, veteranx):
      """Busca todxs xs afilhadxs dx veteranx. Caso não possua, uma lista vazia
      é devolvida"""
      return self.apadrinhamentos().get(veteranx.id, [])

   def afilhar(self, veteranx, id_afilhadx):
      """Adiciona x ingressante como afilhadx de veteranx dado"""
      afilhadxs = self.afilhadxs(veteranx)
      afilhadxs.append(id_afilhadx)
      self.apadrinhamentos()[veteranx.id] = afilhadxs

   def ingressante(self, id_):
      """Procura no banco de dados x ingressante com id dado"""
      return self.ingressantes().get(id_)

   def salvar_banco(self):
      """Salva o banco de dados em um arquivo JSON, transformando os
      estudantes-objeto em dicionários para o construtor."""
      # Verificamos se o banco de dados existe
      if os.path.exists(Database.NOME_ARQUIVO):
         # Fazemos o backup se o banco de dados existe
         shutil.copy2(Database.NOME_ARQUIVO, Database.NOME_ARQUIVO + '.backup')

      # Abrimos o arquivo para escrita
      with open(Database.NOME_ARQUIVO, 'w') as arquivo:
            # Construímos o dicionário para JSON (passamos os estudantes-objeto
            # para simples dicionários)
            dados_json = {
               Database.DICT_VETERANXS: \
                  dict_to_lista(self.veteranxs()),
               Database.DICT_INGRESSANTES: \
                  dict_to_lista(self.ingressantes()),
               Database.DICT_APADRINHAMENTOS: self.apadrinhamentos(),
               Database.ID_VETERANXS: \
                  self.dados.get(Database.ID_VETERANXS),
               Database.ID_INGRESSANTES: \
                  self.dados.get(Database.ID_INGRESSANTES),
            }

            # Transformar dicionário do banco de dados em JSON e escrever
            arquivo.write(json.JSONEncoder(indent='   ').encode(dados_json))

   def ler_banco(self):
      """Lê o arquivo JSON para a memória, transformando os dicionários que
      representam os estudantes em estudantes-objeto."""
      # Abrimos o arquivo
      with open(Database.NOME_ARQUIVO, 'r') as arquivo:
         # Ler o arquivo JSON para um dicionário
         dados_json = json.load(arquivo)

         # Copiamos os dados
         self.dados[Database.ID_VETERANXS] = \
            dados_json.get(Database.ID_VETERANXS)
         self.dados[Database.ID_INGRESSANTES] = \
            dados_json.get(Database.ID_INGRESSANTES)

         # Transformamos as listas em dicionários de estudantes
         self.veteranxs().update(lista_to_dict(
            Tipo.VETERANX, dados_json.get(Database.DICT_VETERANXS)
         ))
         self.ingressantes().update(lista_to_dict(
            Tipo.INGRESSANTE, dados_json.get(Database.DICT_INGRESSANTES)
         ))

         # Problema: JSON irá guardar o id dx veteranx no apadrinhamento na
         # forma de string

         # Para cada par de apadrinhamento..
         apadrinhamentos = dados_json.get(Database.DICT_APADRINHAMENTOS)
         for id_string, afilhadxs in apadrinhamentos.items():
            # Transformamos a string que representa o identificador em número
            self.apadrinhamentos()[int(id_string)] = afilhadxs

   def adicionar_estudante(self, tipo, dicionario):
      """Adiciona um(a) estudante ao dicionário de estudantes, verificando
      duplicates.
      Retorna o estado da adição com 'AdicaoResultado'"""
      estudante = self.buscar_estudante(tipo, dicionario)

      # Verificamos se existe
      if estudante is None:
         # Definimos a chave a buscar e atualizar
         if tipo == Tipo.INGRESSANTE:
            chave = Database.ID_INGRESSANTES
         else:
            chave = Database.ID_VETERANXS

         # Definimos o seu identificador
         id_ = self.dados[chave]
         id_ += 1
         dicionario['id'] = id_

         # Definimos os e-mails que já recebeu
         dicionario['emails_recebidos'] = []

         # Criamos x veteranx
         if tipo == Tipo.INGRESSANTE:
            estudante = Ingressante(dicionario)
         else:
            # Definimos a lista de afilhadxs dxs quais x veteranx está ciente
            dicionario['ciente_de'] = []
            estudante = Veteranx(dicionario)

         # Adicionamos a lista
         if tipo == Tipo.INGRESSANTE:
            self.ingressantes()[id_] = estudante
         else:
            self.veteranxs()[id_] = estudante

         # Salvamos o identificador
         self.dados[chave] = id_

         return AdicaoResultado.ADICIONADO
      elif deve_atualizar_estudante(dicionario, estudante):
         # Como x veteranx já existe, atualizamos
         estudante.atualizar(dicionario)
         return AdicaoResultado.ATUALIZADO
      else:
         return AdicaoResultado.MANTIDO

   def buscar_estudante(self, tipo, dicionario):
      """Busca no banco de dados por algum(a) estudante com mesmas informações
      que as do dicionário dado.
      O critério de igualdade é possuir mesmo endereço de e-mail ou mesmo
      telefone."""
      # Definimos a lista
      if tipo == Tipo.INGRESSANTE:
         lista = self.ingressantes().values()
      else:
         lista = self.veteranxs().values()

      # Para cada estudante..
      for estudante in lista:
         # Conferimos se possui mesmo e-mail ou mesmo telefone (se houver,
         # simplificado)
         if (estudante.email.lower() == dicionario['email'] or
            (len(estudante.telefone) > 0 and
            limpar_telefone(estudante.telefone).lower() ==
            limpar_telefone(dicionario['telefone']).lower())
         ):
            return estudante

      # Não retorna se não encontrou estudante com dados iguais
      return None
