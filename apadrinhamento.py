import time
import random
import os
import io
import smtplib
import getpass
from email.message import EmailMessage
from database import *
from estudantes import *


def enviar_email(sender, password, recipient, subject, body):
   """
   Apenas copiei e modifiquei de https://stackoverflow.com/questions/10147455/

   Para mensagens que fogem dos caracteres ASCII, deve-se usar a string de 3
   aspas.
   """

   # Verificamos se o destinatário está em uma lista
   if type(recipient) is not list:
      recipient = [recipient]

   # Preparamos o e-mail
   message = EmailMessage()
   message['From'] = sender
   message['To'] = ", ".join(recipient)
   message['Subject'] = subject
   message.set_content(body)

   # Tentamos enviá-lo
   try:
      server = smtplib.SMTP("smtp.students.ic.unicamp.br", 587)
      server.ehlo()
      server.starttls()
      # OBSERVAÇÃO: A SENHA NÃO DEVE POSSUIR CARACTERES ESPECIAIS (apenas ASCII)
      server.login(sender, password)
      server.send_message(message)
      server.quit()
      print("E-mail enviado!")
   except:
      print("Falha ao enviar o email")
      raise


class Menu:
   """Classe de Menu, cria um loop infinito de opções a serem validadas.

   * Deve-se definir a função imprimir() e resolver_opcao(opcao).
   * A lista de opções válidas 'opcoes_validas' deve ser definida pelos
   inteiros a serem entrados pelo usuário."""

   def __init__(self, opcoes_validas):
      # Acredito que fazer um loop em __init__ não seja o mais adequado
      self.saindo = False

      # Enquanto a resposta não define a saída do menu, continuamos
      while not self.saindo:
         # Imprimimos o menu
         self.imprimir()

         # Esperamos a resposta e a validamos para um número inteiro
         opcao = input('Digite sua opção: ')
         try:
            # Ignoramos opções que não são inteiros
            opcao = int(opcao)

            # Verificamos se o número da opção é válido
            if opcao not in opcoes_validas:
               raise ValueError()

            # Resolvemos a opção que é válida
            self.resolver_opcao(opcao)
         except ValueError as exception:
            print(exception)
            print("Opção inválida. Tente novamente.")

         # Apenas pulamos linhas se não estamos saindo
         if not self.saindo:
            print("\n\n\n\n")


class MenuPrincipal(Menu):
   def __init__(self):
      super().__init__(range(-1, 9 + 1))

   def imprimir(self):
      print("1. Listar madrinha(s) ou padrinho(s)")
      print("2. Adicionar madrinha(s) ou padrinho(s)")
      print()
      print("3. Listar caloura(s) ou calouro(s)")
      print("4. Adicionar caloura(s) ou calouro(s) da CC")
      print("5. Adicionar caloura(s) ou calouro(s) da EC")
      print("6. Adicionar caloura(s) ou calouro(s) com curso")
      print()
      print("7. Listar apadrinhamentos")
      print("8. Apadrinhar automaticamente")
      print("9. Enviar e-mail de apadrinhamento")
      print()
      print(" 0. Salvar e sair")
      print("-1. Sair sem salvar")
      print()
      print('"é um negocio oval\nparece uma uva, faz bluf bluf"')
      print("\t\tT., Letícia")
      print()

   def resolver_opcao(self, opcao):
      if opcao == -1:
         self.saindo = True
      elif opcao == 0:
         database.salvar_banco()
         self.saindo = True
      elif opcao == 1:
         MenuListarEstudantes(Tipo.VETERANX)
      elif opcao == 2:
         MenuAdicionarVeteranxs()
      elif opcao == 3:
         MenuListarEstudantes(Tipo.INGRESSANTE)
      elif opcao == 4:
         MenuAdicionarIngressantesCurso(Curso.CIENCIA_DA_COMPUTACAO)
      elif opcao == 5:
         MenuAdicionarIngressantesCurso(Curso.ENGENHARIA_DE_COMPUTACAO)
      elif opcao == 6:
         MenuAdicionarIngressantes()
      elif opcao == 7:
         MenuListarApadrinhamentos()
      elif opcao == 8:
         MenuApadrinhar()
      elif opcao == 9:
         MenuEmailApadrinhamento()


def obter_num_ingressantes(string):
   """Transforma em inteiro o número máximo de ingressantes que x veteranx
   quer adotar. -1 significa infinito."""
   if string == 'Até uma':
      return 1
   elif string == 'Entre uma e duas':
      return 2
   elif string == 'Entre uma e três':
      return 3
   elif string == 'Entre uma e quatro':
      return 4
   elif string == 'Quantas estiverem sem madrinha ou padrinho':
      return -1
   else:
      print('Número de ingressantes não interpretado: {}'.format(string))
      return 0


class MenuAdicionar(Menu):
   def __init__(self, numero_colunas):
      """Número de colunas no formulário, para distinguir corretamente entre
      perguntas;
      Nome do dicionário no banco de dados para distinguir entre ingressantes
      e veteranxs;
      Nome da variável identificadora para distinguir entre ingressantes e
      veteranxs."""
      self.numero_colunas = numero_colunas
      # Chamamos o loop
      super().__init__(range(0, 1 + 1))

   def transcrever_e_enviar(self, respostas):
      raise NotImplementedError('MenuAdicionar deve implementar a função que '
      'transcreve as respostas do formulário num dicionário compatível com a '
      'estrutura de estudante e retorne o estado da adição para o banco de '
      'dados.')

   def imprimir(self):
      print('Copie e cole as entradas de estudantes abaixo. Será lido linha '
     'por linha. Qualquer linha que não contenha o número de colunas '
     'esperado parará o programa.')

      adicionados = 0
      atualizados = 0

      while True:
         # Lemos uma linha de entrada. Deve estar dividida por 'tab' (\t)
         # pois é uma simples cópia da planilha.
         lido = input()
         respostas = lido.split('\t')

         # Verificamos as colunas da resposta com a planilha
         if len(respostas) != self.numero_colunas:
            while True:
               trava = input('Trava de segurança para cópia e cola, digite '
               '-1: ')

               # Apenas cancelamos se terminar com '-1', digitado pelo
               # usuário.
               if trava.endswith('-1'):
                  break

            # Avisamos o possível erro
            print('\n\nPode ter ocorrido um erro ao tentar interpretar '
            'input "{}"'.format(lido))
            break

         # Criamos o estudante e enviamos para o banco de dados
         retorno = self.transcrever_e_enviar(respostas)

         if retorno == AdicaoResultado.ADICIONADO:
            adicionados += 1
         elif retorno == AdicaoResultado.ATUALIZADO:
            atualizados += 1

      print('Foram reconhecidos {} novos estudantes e {} atualizações.'
      .format(adicionados, atualizados))
      print()
      print('1. Adicionar mais estudantes')
      print('0. Voltar')
      print()

   def resolver_opcao(self, opcao):
      if opcao == 0:
         self.saindo = True


class MenuAdicionarVeteranxs(MenuAdicionar):
   def __init__(self):
      super().__init__(9)

   def transcrever_e_enviar(self, respostas):
      return database.adicionar_estudante(Tipo.VETERANX, {
         "data_formulario": respostas[0],
         "nome": respostas[2],
         "genero": respostas[4],
         "email": respostas[1],
         "curso": respostas[5],
         "telefone": respostas[7],
         "facebook_link": respostas[8],
         "apelido": respostas[3],
         "numero_ingressantes": obter_num_ingressantes(respostas[6])
      })


class MenuAdicionarIngressantesCurso(MenuAdicionar):
   def __init__(self, curso):
      self.curso = curso
      super().__init__(6)

   def transcrever_e_enviar(self, respostas):
      return database.adicionar_estudante(Tipo.INGRESSANTE, {
         "data_formulario": respostas[0],
         "nome": respostas[2],
         "genero": respostas[3],
         "email": respostas[1],
         "telefone": respostas[4],
         "facebook_link": respostas[5],
         "curso": self.curso.value
      })


class MenuAdicionarIngressantes(MenuAdicionar):
   def __init__(self):
      super().__init__(7)

   def transcrever_e_enviar(self, respostas):
      return database.adicionar_estudante(Tipo.INGRESSANTE, {
         "data_formulario": respostas[0],
         "nome": respostas[2],
         "genero": respostas[4],
         "email": respostas[1],
         "telefone": respostas[5],
         "facebook_link": respostas[6],
         "curso": respostas[3]
      })


class MenuListarEstudantes(Menu):
   def __init__(self, tipo):
      self.tipo = tipo
      super().__init__(range(0, 4 + 1))

   def imprimir(self):
      # Definimos a lista
      if self.tipo == Tipo.INGRESSANTE:
         lista = database.ingressantes()
      else:
         lista = database.veteranxs()

      # Imprimimos
      print('Id\tNome')
      for estudante in lista.values():
         print('{}\t{}'.format(estudante.id, estudante.nome))
      print('\n\n')
      print('1. Adicionar veteranas(os)')
      print('2. Adicionar calouras(os) da CC')
      print('3. Adicionar calouras(os) da EC')
      print('4. Adicionar calouras(os) com curso')
      print()
      print('0. Voltar')

   def resolver_opcao(self, opcao):
      if opcao == 0:
         self.saindo = True
      elif opcao == 1:
         MenuAdicionarVeteranxs()
      elif opcao == 2:
         MenuAdicionarIngressantesCurso(Curso.CIENCIA_DA_COMPUTACAO)
      elif opcao == 3:
         MenuAdicionarIngressantesCurso(Curso.ENGENHARIA_DE_COMPUTACAO)
      elif opcao == 4:
         MenuAdicionarIngressantes()


class MenuListarApadrinhamentos(Menu):
   def __init__(self):
      super().__init__([0, 1])

   def imprimir(self):
      # Imprimimos a legenda
      print('\n\nId\tNúmero desejado de afiladxs\tNome dx veteranx')
      print('\tId dx afilhadx\tNome dx afilhadx')

      # Imprimimos a lista
      for veteranx in database.veteranxs().values():
         # Imprimimos x veteranx
         print('{}\t1 a {}\t{}'.format(
            veteranx.id, veteranx.numero_ingressantes, veteranx.nome
         ))

         # Fazemos a lista de ingressantes
         afilhaxs = veteranx.afilhadxs()

         if len(afilhaxs) > 0:
            for ingressante_id in afilhaxs:
               ingressante = database.ingressante(ingressante_id)
               print('\t{}\t{}'.format(ingressante_id, ingressante.nome))
         else:
            print('\tNão possui afilhadxs')

      # OBS: isso pode causar um stack overflow (pois MenuApadrinhar também
      # possui uma ligação para MenuListarApadrinhamentos)
      print('\n\n')
      print('1. Apadrinhar')
      print('0. Voltar')

   def resolver_opcao(self, opcao):
      self.saindo = True
      if opcao == 1:
         MenuApadrinhar()


class MenuApadrinhar(Menu):
   def __init__(self):
      super().__init__([0, 1])

   def imprimir(self):
      # Criamos as listas de pessoas para veteranos
      vet_gen_masc = []
      vet_gen_fem = []
      vet_gen_outros = []

      # E para ingressantes
      ing_gen_masc = []
      ing_gen_fem = []
      ing_gen_outros = []

      # Separamos veteranxs por gênero
      for veteranx in database.veteranxs().values():
         # Atualizamos a lista
         if veteranx.genero == Genero.MASCULINO:
            vet_gen_masc.append(veteranx)
         elif veteranx.genero == Genero.FEMININO:
            vet_gen_fem.append(veteranx)
         elif veteranx.genero == Genero.OUTRO:
            vet_gen_outros.append(veteranx)
         else:
            print('Algo de estranho aconteceu com o gênero dx '
            'veteranx {}'.format(veteranx.nome))
            continue

      print('Há {} veteranos, {} veteranas e {} veteranxs'.format(
         len(vet_gen_masc), len(vet_gen_fem), len(vet_gen_outros))
      )

      # Separamos ingressantes por gênero
      for ingressante in database.ingressantes().values():
         # Atualizamos a lista
         if ingressante.genero == Genero.MASCULINO:
            ing_gen_masc.append(ingressante)
         elif ingressante.genero == Genero.FEMININO:
            ing_gen_fem.append(ingressante)
         elif ingressante.genero == Genero.OUTRO:
            ing_gen_outros.append(ingressante)
         else:
            print('Algo de estranho aconteceu com o gênero dx '
            'ingressante {}'.format(ingressante.nome))
            continue

      print('Há {} calouros, {} calouras e {} calourxs'.format(
         len(ing_gen_masc), len(ing_gen_fem), len(ing_gen_outros))
      )

      # Misturamos as listas
      random.shuffle(vet_gen_masc)
      random.shuffle(vet_gen_fem)
      random.shuffle(vet_gen_outros)
      random.shuffle(ing_gen_masc)
      random.shuffle(ing_gen_fem)
      random.shuffle(ing_gen_outros)

      # Para cada lista, fazemos o apadrinhamento
      numero_apadrinhado = 0
      numero_apadrinhado += MenuApadrinhar.apadrinhar(
         vet_gen_masc, ing_gen_masc
      )
      numero_apadrinhado += MenuApadrinhar.apadrinhar(
         vet_gen_fem, ing_gen_fem
      )
      numero_apadrinhado += MenuApadrinhar.apadrinhar(
         vet_gen_outros, ing_gen_outros
      )

      print('\n\n{} ingressantes foram apadrinhados!\n\n'.format(
         numero_apadrinhado
      ))
      print('1. Ver lista de apadrinhamento')
      print('0. Voltar')

   def resolver_opcao(self, opcao):
      self.saindo = True
      if opcao == 1:
         MenuListarApadrinhamentos()

   def apadrinhar(lista_vet, lista_ing):
      # Fazemos listas para cada curso
      vet_ec = []
      vet_cc = []

      ing_ec = []
      ing_cc = []

      # Separamos veteranxs por curso
      for veteranx in lista_vet:
         # Conferimos se x veteranx já tem muitas(os) afilhadas(os)
         if veteranx.numero_ingressantes > 0:
            atual = len(veteranx.afilhadxs())
            limite = veteranx.numero_ingressantes
            if atual > limite:
               print('{} ({}) possui muitos afilhados'.format(
                  veteranx.nome, veteranx.id
               ))
               # Pulamos
               continue
            elif atual == limite:
               # Pulamos sem avisar
               continue

         # Colocamos na lista
         if veteranx.curso == Curso.CIENCIA_DA_COMPUTACAO:
            vet_cc.append(veteranx)
         elif veteranx.curso == Curso.ENGENHARIA_DE_COMPUTACAO:
            vet_ec.append(veteranx)
         else:
            print('Algo inesperado aconteceu com o curso para x '
            'veteranx {}'.format(veteranx.nome))
            continue

      # Separamos ingressantes por curso
      for ingressante in lista_ing:
         # Conferimos se x ingressante já tem madrinha ou padrinho
         possui = False
         for apadrinhadxs in database.apadrinhamentos().values():
            # Se o id está em alguma lista de pessoas apadrinhadas, marcamos
            if ingressante.id in apadrinhadxs:
               possui = True
               break

         # Pulamos os que já possuem madrinha ou padrinho
         if possui:
            continue

         # Tentamos procurar o curso
         if ingressante.curso == Curso.CIENCIA_DA_COMPUTACAO:
            ing_cc.append(ingressante)
         elif ingressante.curso == Curso.ENGENHARIA_DE_COMPUTACAO:
            ing_ec.append(ingressante)
         else:
            print('Algo inesperado aconteceu com o curso para x '
            'ingressante {}'.format(ingressante.nome))
            continue

      # Apadrinhamos cada curso
      numero_apadrinhado = 0
      numero_apadrinhado += MenuApadrinhar.apadrinhar_curso(vet_cc, ing_cc)
      numero_apadrinhado += MenuApadrinhar.apadrinhar_curso(vet_ec, ing_ec)
      return numero_apadrinhado

   # Seja para CC ou EC
   def apadrinhar_curso(veteranxs, ingressantes):
      numero_apadrinhado = 0

      # Conferimos se é possível fazer pares (se não, deixamos para o
      # usuário)
      if (len(veteranxs) == 0 and len(ingressantes) > 0):
         print('Não há veteranxs disponíveis para:')
         for ingressante in ingressantes:
            print('{}\t{}'.format(ingressante.id, ingressante.nome))
         print('\n')
         return 0

      # Fazemos os pares
      for ingressante in ingressantes:
         # Pegamos x veteranx que quer possuir um(a) afilhado(a) mas possui a
         # menor quantidade de afilhadas(os) na lista
         # Dessa forma, a distribuição fica igualitária
         # OBS: 'veteranxs' foi desorganizada no passado
         veteranx = None
         menor_quantidade = None
         for veteranx_ in veteranxs:
            quantidade = len(veteranx_.afilhadxs())
            if (menor_quantidade is None or quantidade < menor_quantidade):
               menor_quantidade = quantidade
               veteranx = veteranx_

         # Se veteranx é nulo, significa que não há veteranxs suficientes
         if veteranx is None:
            print('Pessoa sem apadrinhamento: {}'.format(ingressante.nome))
            continue

         # Agora que temos um(a) veteranx, temos que removê-la(o) da lista
         veteranxs.remove(veteranx)

         # Adicionamos x ingressante como afilhadx
         veteranx.afilhar(ingressante.id)
         numero_apadrinhado += 1

         # Verificamos se o veteranx ainda pode possuir mais afilhadas(os)
         if (veteranx.numero_ingressantes < 0 or
            veteranx.numero_ingressantes > len(veteranx.afilhadxs())):
            # Adicionamos e reorganizamos
            veteranxs.append(veteranx)
            random.shuffle(veteranxs)

      return numero_apadrinhado


class Mensagem:
   """Esta classe servirá para construir a mensagem do e-mail de maneira
   fácil. Para utilizá-la, precisará, de início, definir um estudante."""

   def __init__(self, mensagem_base, apenas_nao_ciente=False):
      self.mensagem_base = mensagem_base
      # Para xs veteranxs, substituímos "{info_afilhada}" com as informações
      # de afilhadxs que não foram ainda informados
      self.apenas_nao_ciente = apenas_nao_ciente

   def definir_estudante(self, estudante):
      self.mensagem = self.mensagem_base
      self.estudante = estudante

      # Substituímos o nome
      self.mensagem = self.mensagem.replace("{nome}", estudante.nome)

      # Verificamos se é veteranx
      self.is_veteranx = estudante.tipo == Tipo.VETERANX
      if self.is_veteranx:
         self.num_afilhadxs = len(estudante.afilhadxs())

         # No caso de divulgar apenas xs novxs afilhadxs, tiramos xs afilhadxs
         # já conhecidos
         if self.apenas_nao_ciente:
            self.num_afilhadxs -= len(estudante.ciente_de)

         # Pulamos xs veteranxs sem afilhadxs para divulgar
         if self.num_afilhadxs == 0:
            return False

         # Criamos uma lista de afilhadxs
         afilhadxs = estudante.afilhadxs()

         # Construímos informações dxs afilhadxs
         primeirx = True
         informacoes = u''
         for afilhadx_id in afilhadxs:
            afilhadx = database.ingressante(afilhadx_id)

            # Verificamos se precisamos pular xs afilhadxs já mencionados
            if (self.apenas_nao_ciente and afilhadx_id in estudante.ciente_de):
               # Continuamos para o próximo item, já que x afilhadx já
               # foi mencionado
               continue

            # Pulamos de linha entre informações, menos para x primeirx
            # ingressante
            if primeirx:
               primeirx = False
            else:
               informacoes += u'\n'

            # Adicionamos dados básicos
            dados = [
               'Nome: ' + afilhadx.nome,
               'E-mail: ' + afilhadx.email
            ]
            # Adicionamos telefone se disponível
            if len(afilhadx.telefone) > 0:
               dados.append('Telefone: ' + afilhadx.telefone)
            # Adicionamos o endereço para o Facebook se disponível
            if len(afilhadx.facebook_link) > 0:
               dados.append('Facebook: ' + afilhadx.facebook_link)

            # Juntamos todas as informações
            informacoes += u'\n'.join(dados) + u'\n'

         # Substituimos as informações dxs afilhadxs
         self.mensagem = self.mensagem.replace("{info_afilhada}",
         informacoes)

      # Se é ingressante, substituímos x veteranx
      else:
         # Procuramos x veteranx
         veteranx = estudante.padrinho_madrinha()

         # Verificamos se um(a) veteranx foi definido
         if veteranx == None:
            # Pulamos o caso em que x estudante não foi apadrinhado
            return False

         # Construímos informações dxs afilhadxs
         informacoes = u''
         # Adicionamos dados básicos
         dados = [
            'Nome: ' + veteranx.nome,
            'Apelido: ' + veteranx.apelido,
            'E-mail: ' + veteranx.email
         ]
         # Adicionamos telefone se disponível
         if len(veteranx.telefone) > 0:
            dados.append('Telefone: ' + veteranx.telefone)
         # Adicionamos endereço para o perfil no Facebook se disponível
         if len(veteranx.facebook_link) > 0:
            dados.append('Facebook: ' + veteranx.facebook_link)

         # Juntamos toda a string com uma nova linha
         informacoes += u'\n'.join(dados)

         # Substituimos as informações dxs afilhadxs
         self.mensagem = self.mensagem.replace("{info_veterana}",
         informacoes)

      # Não sei substituir texto para isso, então deixarei para o
      # apadrinhamento manual.
      # Retornamos verdadeiro apenas para os gêneros que terão a substituição
      # válida
      return (self.estudante.genero == Genero.MASCULINO or
         self.estudante.genero == Genero.FEMININO)

   def substituir_genero(self, keyword, subst_masc, subst_fem):
      if self.estudante.genero == Genero.MASCULINO:
         self.mensagem = self.mensagem.replace(keyword, subst_masc)
      else: # a outra opção é necessariamente feminino, por construção
         self.mensagem = self.mensagem.replace(keyword, subst_fem)

      # Com return self é possível criar uma estrutura fácil de repetição
      return self

   def substituir_genero_quantidade(
      self, keyword,
      subst_masc_sing, subst_masc_plur,
      subst_fem_sing, subst_fem_plur
   ):
      """Esta função está disponível apenas para estudante que é do tipo
      Veteranx. Não fará nada caso contrário."""
      if not self.is_veteranx:
         return self

      # No caso que é veteranx, contamos o número de afilhadxs
      if self.num_afilhadxs > 1:
         self.substituir_genero(keyword, subst_masc_plur, subst_fem_plur)
      else:
         self.substituir_genero(keyword, subst_masc_sing, subst_fem_sing)

      return self

   def terminar_mensagem(self):
      return self.mensagem


class MenuEmailApadrinhamento(Menu):
   def __init__(self):
      super().__init__(range(0, 3 + 1))

   def imprimir(self):
      # OBS: marquei com '#' o que eu utilizei nas mensagens que preparei

      print('Você precisa escrever um arquivo modelo para o e-mail. As '
      'seguintes palavras-chave serão substituídas, plurais de acordo com a'
      'quantidade de afilhadxs:')
      print('\tPalavra\t\tSubstituição no caso de masculino e feminino')
      print('"{info_veterana}"\t->\tLista de dados da madrinha/padrinho')
      print('"{info_afilhada}"\t->\tLista de dados de afilhadas(os)')#
      print('"{madrinha}"\t\t->\t"padrinho" ou "madrinha"')#
      print('"{afilhada}"\t\t->\t"afilhado" ou "afilhada"')
      print('"{afilhada(s)}"\t\t->\t"afilhado"/"afilhados" ou "afilhada"/'
      '"afilhadas"')#
      print('"{veterana}"\t\t->\t"veterano" ou "veterana"')
      print('"{caloura}"\t\t->\t"calouro" ou "caloura"')
      print('"{nome}"\t\t->\tnome do padrinho, madrinha, afilhado ou '
      'afilhada')#
      print('"{outra(s)}"\t\t->\t"outro"/"outros" ou "outra"/"outras"')
      print('"{nova(s)}"\t\t->\t"novo"/"novos" ou "nova"/"novas"')
      print('"{ela}"\t\t\t->\t"ele" ou "ela"')
      print('"{elas}"\t\t->\t"eles" ou "elas"')
      print('"{ela(s)}"\t\t->\t"ele"/"eles" ou "ela"/"elas"')
      print('"{sua}"\t\t\t->\t"seu" ou "sua"')
      print('"{suas}"\t\t->\t"seus" ou "suas"')
      print('"{sua(s)}"\t\t->\t"seu"/"seus" ou "sua"/"suas"')#
      print('"{uma}"\t\t\t->\t"um" ou "uma"')
      print('"{a}"\t\t\t->\t"o" ou "a"')
      print('"{ao}"\t\t\t->\t"ao" ou "à"')
      print('"{aos}"\t\t\t->\t"aos" ou "às"')
      print('"{ao(s)}"\t\t\t->\t"ao"/"aos" ou "à"/"às"')#
      print('"{as}"\t\t\t->\t"os" ou "as"')
      print('"{a(s)}"\t\t->\t"o"/"os" ou "a"/"as"')
      print('\n\n')
      print('1. Enviar com substituições para veteranxs (com informações de '
      'suas/seus afilhadas(os))')
      print('2. Enviar com substituições para veteranxs (com informações de '
      'suas/seus afilhadas(os) recentes)')
      print('3. Enviar com substituições para ingressantes (com informações '
      'de sua/seu madrinha/padrinho)')
      print()
      print('0. Voltar')

   def resolver_opcao(self, opcao):
      if opcao == 0:
         self.saindo = True
      else:
         print('\n\n')
         print('O nome da mensagem preferencialmente NÃO deve possuir '
         'espaços\n')
         print('O nome da mensagem deve ser um identificador único. Isso '
         'significa que, se alguém já recebeu a mensagem '
         '"mensagem_veteranx.txt", ao tentar enviá-la novamente, este '
         'alguém não irá receber novamente a mensagem, mesmo que ela tenha '
         'sido alterada.')
         nome_arquivo = input('Digite o nome do arquivo (com extensão): ')

         # Verificamos se a mensagem existe
         if not os.path.exists(nome_arquivo):
            print('Opção inválida, mensagem não encontrada!')
            return

         # Recebemos a mensagem como uma string UTF-8, já que temos
         # acentos rs
         with io.open(nome_arquivo, mode='r', encoding="utf-8") as \
         arquivo_mensagem:
            mensagem_base = arquivo_mensagem.read()
            self.mensagem = Mensagem(
               mensagem_base, apenas_nao_ciente=opcao == 2
            )
         print('Mensagem encontrada.')

         # Definimos o assunto do e-mail
         self.assunto = input('Digite o assunto do e-mail: ')
         print('Assunto do e-mail: "{}"'.format(self.assunto))
         print('Mensagem do e-mail:')
         print(u'"{}"'.format(self.mensagem.mensagem_base))
         print()

         # Confirmamos
         confirmacao = input('Digite "-1" para confirmar: ')
         if not confirmacao.endswith('-1'):
            print('Retornando...')
            return

         # Definimos para quem gostaríamos de enviar
         if (opcao == 1 or opcao == 2):
            lista = database.veteranxs()
         elif opcao == 3:
            lista = database.ingressantes()

         # Pedimos credenciais
         sender = input('De qual e-mail em students.ic.unicamp.br você irá '
         'enviar? (A senha deve ser em ASCII) ')
         if not sender.endswith('@students.ic.unicamp.br'):
            sender = sender + '@students.ic.unicamp.br'

         password = getpass.getpass(prompt='Senha: ')

         # Confirmamos
         print('Irá enviar de "{}"?'.format(sender))
         confirmar = input('Digite -1 para confirmar: ')
         if not confirmar.endswith('-1'):
            return

         # Para cada estudante..
         for estudante in lista.values():
            # Pulamos xs estudantes que já receberam este e-mail
            if nome_arquivo in estudante.emails_recebidos:
               print('Estudante {} ({}) ignorado por já ter recebido o '
               'e-mail'.format(estudante.nome, estudante.id))
               continue

            # Fazemos a definição inicial (nome, informações de
            # padrinho/madrinha ou afilhado(s)/afilhadas(s))
            if not self.mensagem.definir_estudante(estudante):
               print('Estudante {} ({}) ignorado por não satisfazer os '
               'requisitos'.format(estudante.nome, estudante.id))
               # Pulamos
               continue

            # Substituímos para masculino
            self.mensagem.substituir_genero(
               "{madrinha}", 'padrinho', 'madrinha'
            ).substituir_genero(
               "{afilhada}", 'afilhado', 'afilhada'
            ).substituir_genero_quantidade(
               "{afilhada(s)}",
               'afilhado', 'afilhados', 'afilhada', 'afilhadas'
            ).substituir_genero(
               "{veterana}", 'veterano', 'veterana'
            ).substituir_genero(
               "{caloura}", 'calouro', 'caloura'
            ).substituir_genero_quantidade(
               "{outra(s)}",
               'outro', 'outros', 'outra', 'outras'
            ).substituir_genero_quantidade(
               "{nova(s)}",
               'novo', 'novos', 'nova', 'novas'
            ).substituir_genero(
               "{ela}", 'ele', 'ela'
            ).substituir_genero(
               "{elas}", 'eles', 'elas'
            ).substituir_genero_quantidade(
               "{ela(s)}",
               'ele', 'eles', 'ela', 'elas'
            ).substituir_genero(
               "{sua}", 'seu', 'sua'
            ).substituir_genero(
               "{suas}", 'seus', 'suas'
            ).substituir_genero_quantidade(
               "{sua(s)}",
               'seu', 'seus', 'sua', 'suas'
            ).substituir_genero(
               "{uma}", 'um', 'uma'
            ).substituir_genero(
               "{a}", 'o', 'a'
            ).substituir_genero(
               "{ao}", 'ao', u'à'
            ).substituir_genero(
               "{aos}", 'aos', u'às'
            ).substituir_genero_quantidade(
               "{ao(s)}",
               'ao', 'aos', u'à', u'às'
            ).substituir_genero(
               "{as}", 'os', 'as'
            ).substituir_genero_quantidade(
               "{a(s)}",
                'o', 'os', 'a', 'as'
            )

            print('Mensagem preparada para {}'.format(estudante.email))

            # Agora enviamos o e-mail
            try:
               enviar_email(
                  sender, password,
                  estudante.email,
                  self.assunto,
                  self.mensagem.terminar_mensagem()
               )
               estudante.emails_recebidos.append(nome_arquivo)
               print('Enviado para {}. Esperando 4 '
               'segundos'.format(estudante.email))

               # Se tudo ocorreu bem e é um(a) veteranx...
               if self.mensagem.is_veteranx:
                  # Incluímos todxs xs afilhadxs como cientes para x veteranx
                  for afilhadx_id in estudante.afilhadxs():
                     # Adicionamos os identificadores que não estão na lista
                     if afilhadx_id not in estudante.ciente_de:
                        estudante.ciente_de.append(afilhadx_id)

               # Salvamos após cada e-mail, conservando o estado do banco de
               # dados com relação aos e-mails enviados
               database.salvar_banco()

               # Esperamos 4 segundos entre mensagens
               time.sleep(4)
            except:
               # Paramos de enviar caso ocorrer algum erro
               database.salvar_banco()
               print('Falha ao enviar para {}'.format(estudante.email))
               raise

         # Saímos
         self.saindo = True


# Aqui começa a execução do programa
print("=== Sistema de Apadrinhamento v0.1 -- Rafael Sartori ===\n")
# Criamos o banco de dados (__init__ será chamado e o banco de dados será lido
# ou criado de acordo com o padrão)
database = Database()

# Inicializamos o menu principal, a interação com o usuário começa e o caminho
# seguido dentro do programa ocorre de forma recursiva entre os menus.
MenuPrincipal()
