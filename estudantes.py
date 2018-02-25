from enum import Enum, auto


class Curso(Enum):
   # Na verdade, o curso se chama 'Ciência da computação', typo no formulário
   # perpetuado para sempre porque eu tive preguiça de corrigir a planilha
   CIENCIA_DA_COMPUTACAO      = 'Ciência de computação'
   ENGENHARIA_DE_COMPUTACAO   = 'Engenharia de computação'

   def da_string(string):
      if string == Curso.CIENCIA_DA_COMPUTACAO.value:
         return Curso.CIENCIA_DA_COMPUTACAO
      elif string == Curso.ENGENHARIA_DE_COMPUTACAO.value:
         return Curso.ENGENHARIA_DE_COMPUTACAO
      else:
         raise ValueError('String não reconhecida como curso')


class Genero(Enum):
   MASCULINO = 'Masculino'
   FEMININO  = 'Feminino'
   OUTRO     = 'Outro'

   def da_string(string):
      """Verifica a string como um gênero"""
      if string == Genero.MASCULINO.value:
         return Genero.MASCULINO
      elif string == Genero.FEMININO.value:
         return Genero.FEMININO
      elif string == Genero.OUTRO.value:
         return Genero.OUTRO
      else:
         raise ValueError('String não reconhecida como gênero')


class Tipo(Enum):
   """Classe para informar o tipo do estudante"""
   INGRESSANTE = auto()
   VETERANX    = auto()


class Estudante:
   """Estudante é a estrutura básica de veteranx ou ingressante"""
   # OBS: possui (a partir da criação de Database) uma variável estática para
   # o banco de dados

   def __init__(self, tipo, dict_json):
      # Recebemos o dicionário que representa apenas uma pessoa
      self.tipo = tipo
      self.id = dict_json['id']
      self.emails_recebidos = dict_json['emails_recebidos']
      self.atualizar(dict_json)

   def atualizar(self, dict_atualizado):
      # Essas características não devem mudar entre respostas.. eu acho?
      # Vou deixar aqui para aqueles que clicaram ou digitaram errado
      self.nome = dict_atualizado['nome']
      self.genero = Genero.da_string(dict_atualizado['genero'])
      self.curso = Curso.da_string(dict_atualizado['curso'])
      # Essas podem e/ou devem mudar
      self.data_formulario = dict_atualizado['data_formulario']
      self.email = dict_atualizado['email']
      self.telefone = dict_atualizado['telefone']
      self.facebook_link = dict_atualizado['facebook_link']

   def to_dict(self):
      # Transformamos a pessoa em dicionário
      return {
         "id": self.id,
         "data_formulario": self.data_formulario,
         "nome": self.nome,
         "genero": self.genero.value,
         "email": self.email,
         "curso": self.curso.value,
         "telefone": self.telefone,
         "facebook_link": self.facebook_link,
         "emails_recebidos": self.emails_recebidos
      }


class Veteranx(Estudante):
   """Veteranx é a estrutura Estudante com as variáveis número de ingressantes
   que deseja apadrinhar e apelido"""

   def __init__(self, dict_json):
      self.ciente_de = dict_json['ciente_de']
      super().__init__(Tipo.VETERANX, dict_json)

   def atualizar(self, dict_atualizado):
      super().atualizar(dict_atualizado)
      # Apenas para madrinhas e padrinhos:
      self.apelido = dict_atualizado['apelido']
      self.numero_ingressantes = dict_atualizado['numero_ingressantes']
      # Isto é controlado por nós, como e-mails recebidos. Portanto, não deve
      # ser atualizado
      #self.ciente_de = dict_atualizado['ciente_de']

   def to_dict(self):
      dict_json = super().to_dict()
      dict_json['apelido'] = self.apelido
      dict_json['numero_ingressantes'] = self.numero_ingressantes
      dict_json['ciente_de'] = self.ciente_de
      return dict_json

   def afilhadxs(self):
      return Estudante.database.afilhadxs(self)

   def afilhar(self, id_):
      return Estudante.database.afilhar(self, id_)


class Ingressante(Estudante):
   """Ingressante é a estrutura Estudante, coloquei apenas para
   diferenciar(?)"""

   def __init__(self, dict_json):
      super().__init__(Tipo.INGRESSANTE, dict_json)

   def padrinho_madrinha(self):
      apadrinhamentos = Estudante.database.apadrinhamentos()
      # Procuramos x veteranx
      for veteranx_id, afilhadxs_ids in apadrinhamentos.items():
         if self.id in afilhadxs_ids:
            return Estudante.database.veteranx(veteranx_id)

      # Retorna nada se não encontramos
      return None
