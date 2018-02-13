import json
import random
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from estudantes import *


NOME_DICT_VETERANXS = 'veteranxs'
NOME_DICT_INGRESSANTES = 'ingressantes'
NOME_DICT_APADRINHAMENTOS = 'apadrinhamentos'

NOME_ID_VETERANXS = 'ultimo_id_veteranxs'
NOME_ID_INGRESSANTES = 'ultimo_id_ingressantes'

NOME_CURSO_CC = 'Ciência de computação'
# CC, na verdade, é 'dA computação', eu errei no formulário
NOME_CURSO_EC = 'Engenharia de computação'

NOME_GENERO_MASC = 'Masculino'
NOME_GENERO_FEM = 'Feminino'
NOME_GENERO_OUTROS = 'Outro'


def enviar_email(sender, password, recipient, subject, body):
    """Apenas copiei e modifiquei de
    https://stackoverflow.com/questions/10147455/ """

    # Preparamos o e-mail
    if type(recipient) is not list:
        recipient = [recipient]

    message = EmailMessage()
    message['From'] = sender
    message['To'] = ", ".join(recipient)
    message['Subject'] = subject
    message.set_content(body)

    # Tentar enviá-lo
    try:
        server = smtplib.SMTP("smtp.students.ic.unicamp.br", 587)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.send_message(message)
        server.close()
        print("E-mail enviado!")
    except:
        print("Falha ao enviar o email")
        raise


def estudante_para_dicionario(database, nome_lista):
    """Função que transforma a lista de estudantes em uma estrutura compatível
    com JSON: uma lista de simples dicionários"""
    # OBS: estamos alterando o conteúdo de database, o que é interpretado como
    # passagem por referência

    # Removemos o dicionário de objetos
    estudantes = database.pop(nome_lista)
    # Substituímos por uma lista vazia
    database[nome_lista] = []

    while len(estudantes) > 0:
        # Transfornamos o estudante-objeto em dicionários simples para JSON
        id_, estudante = estudantes.popitem()
        # Adicionamos o dicionário a lista
        database[nome_lista].append(estudante.to_dict())


def dicionario_para_estudante(database, nome_lista):
    """Função que transforma a lista de dicionários em uma lista de
    estudantes"""

    # Removemos a lista de dicionários
    dict_estudantes = database.pop(nome_lista)
    # Substituímos por uma lista vazia
    database[nome_lista] = {}

    while len(dict_estudantes) > 0:
        dicionario = dict_estudantes.pop()
        estudante = None

        # Transfornamos o estudante-dicionário em objetos
        if nome_lista == NOME_DICT_VETERANXS:
            estudante = Veteranx(dicionario)
        else:
            estudante = Ingressante(dicionario)

        # Adicionamos o objeto a lista
        database[nome_lista][estudante.id] = estudante


def limpar_telefone(string):
    return string.replace('(', '').replace(')', '').replace(' ', '')


class Database:
    """Classe que armazena todas as funções de leitura, gravação, adição e
    remoção de estudantes"""
    # Definimos o nome do arquivo do banco de dados
    FILE_NAME = 'sist_apadrinhamento.json'

    def __init__(self):
        # Definimos o banco de dados padrão
        # Em JSON, serão lidos como listas; em Python, como dicionários.
        self.database = {
            NOME_DICT_VETERANXS: {},
            NOME_ID_VETERANXS: 0,
            NOME_DICT_INGRESSANTES: {},
            NOME_ID_INGRESSANTES: 0,
            # key: id veteranx, value: ids ingressantes
            NOME_DICT_APADRINHAMENTOS: {}
        }

        # Lemos/criamos o arquivo
        if os.path.exists(self.FILE_NAME):
            # Lemos o estado atual do banco de dados
            self.ler_banco()

    def salvar_banco(self):
        """Esta função IRÁ quebrar o banco de dados pois transforma o
        dicionário de estudantes em uma lista. Para arrumar, utilize ler_banco
        ou transforme de volta"""
        with open(self.FILE_NAME, 'w') as database_file:
            # Transformamos o dicionário (id, estudante objeto) em uma lista de
            # estudantes-dicionário
            estudante_para_dicionario(self.database, NOME_DICT_VETERANXS)
            estudante_para_dicionario(self.database, NOME_DICT_INGRESSANTES)

            # Transformar dicionário do banco de dados em JSON e escrever
            database_file.write(
                json.JSONEncoder(indent='    ').encode(self.database)
            )

    def ler_banco(self):
        with open(self.FILE_NAME, 'r') as database_file:
            # Ler o arquivo JSON para o dicionário do banco de dados
            self.database = json.load(database_file)

            # Transformamos o dicionário de dicionários em pessoas
            dicionario_para_estudante(self.database, NOME_DICT_VETERANXS)
            dicionario_para_estudante(self.database, NOME_DICT_INGRESSANTES)

    def adicionar_estudante(self, nome_lista, estudante):
        self.database[nome_lista][estudante.id] = estudante

    def buscar(self, nome_lista, respostas_dict):
        for estudante in self.database[nome_lista].values():
            # Conferimos se há alguma resposta igual (email, telefone)
            # OBS: nome não deve importa pois nem todos colocaram o nome
            # completo
            # OBS 2: conferir o tamanho da string telefone anterior a
            # comparação evita problemas como 2 pessoas que não
            # disponibilizaram o telefone serem julgadas como atualizações
            if (#estudante.nome.lower() == respostas_dict['nome'] or
                estudante.email.lower() == respostas_dict['email'] or
                (len(estudante.telefone) > 0 and
                limpar_telefone(estudante.telefone).lower() ==
                limpar_telefone(respostas_dict['telefone']).lower())):
                return estudante

        # Não retorna se não encontrou algum dado igual
        return None


class Menu:
    """
    Classe de Menu, cria um loop infinito de opções a serem validadas.

    * Deve-se definir a função imprimir() e resolver_opcao(opcao).
    * A lista de opções válidas 'opcoes_validas' deve ser definida pelos
    inteiros a serem entrados pelo usuário.
    """

    def __init__(self, opcoes_validas):
        self.saindo = False

        # Enquanto a resposta não define a saída do menu, continuamos sem parar
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
        super().__init__(range(-1, 7 + 1))

    def imprimir(self):
        print("1. Listar madrinha(s) ou padrinho(s)")
        print("2. Adicionar madrinha(s) ou padrinho(s)")
        print()
        print("3. Listar caloura(s) ou calouro(s)")
        print("4. Adicionar caloura(s) ou calouro(s) da CC")
        print("5. Adicionar caloura(s) ou calouro(s) da EC")
        print()
        print("6. Listar apadrinhamentos")
        print("7. Apadrinhar automaticamente")
        print()
        print(" 0. Salvar e sair")
        print("-1. Sair sem salvar")
        print()
        print("Obs: a senha do wi-fi da Letícia é 'judite69'")
        print()

    def resolver_opcao(self, opcao):
        if opcao == -1:
            self.saindo = True
        elif opcao == 0:
            database.salvar_banco()
            self.saindo = True
        elif opcao == 1:
            MenuListarEstudantes(NOME_DICT_VETERANXS)
        elif opcao == 2:
            MenuAdicionarVeteranxs()
        elif opcao == 3:
            MenuListarEstudantes(NOME_DICT_INGRESSANTES)
        elif opcao == 4:
            MenuAdicionarIngressantes(NOME_CURSO_CC)
        elif opcao == 5:
            MenuAdicionarIngressantes(NOME_CURSO_EC)
        elif opcao == 6:
            MenuListarApadrinhamentos()
        elif opcao == 7:
            MenuApadrinhar()


def data_do_formulario(string):
    # Transforma a string que representa o horário de registro do formulário
    # usando o formato de tempo do formulário do Google
    return datetime.strptime(string, '%d/%m/%Y %H:%M:%S')


def obter_num_ingressantes(string):
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


class MenuAdicionarVeteranxs(Menu):
    def __init__(self):
        # Chamamos o loop
        super().__init__(range(0, 1 + 1))

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
            if len(respostas) != 9:
                while True:
                    trava = input('Trava de segurança para cópia e cola, '
                    'digite -1: ')

                    # Apenas cancelamos se terminar com '-1', digitado pelo
                    # usuário.
                    if trava.endswith('-1'):
                        break

                # Avisamos o possível erro
                print('\n\nPode ter ocorrido um erro ao tentar interpretar '
                'input "{}"'.format(lido))
                break

            # Criamos o estudante-dicionário
            respostas_dict = {
                "data_formulario": respostas[0],
                "nome": respostas[2],
                "genero": respostas[4],
                "email": respostas[1],
                "curso": respostas[5],
                "telefone": respostas[7],
                "facebook_link": respostas[8],
                "apelido": respostas[3],
                "numero_ingressantes": obter_num_ingressantes(respostas[6])
            }

            # Buscamos algum estudante-objeto já existente
            veteranx = database.buscar(NOME_DICT_VETERANXS, respostas_dict)

            if veteranx == None:
                # Se não há existente, criamos
                ultimo_id = database.database[NOME_ID_INGRESSANTES] + 1
                respostas_dict['id'] = ultimo_id
                database.database[NOME_ID_INGRESSANTES] = ultimo_id
                veteranx = Veteranx(respostas_dict)
                # Adicionamos ao banco de dados
                database.adicionar_estudante(NOME_DICT_VETERANXS, veteranx)
                adicionados += 1
            else:
                # Confiamos que não é um duplicate e atualizamos se a data for
                # maior :)
                data_database = data_do_formulario(veteranx.data_formulario)
                data_atual = data_do_formulario(
                    respostas_dict['data_formulario']
                )

                # Vereficamos se precisamos atualizar
                if data_database < data_atual:
                    veteranx.atualizar(respostas_dict)
                    atualizados += 1

        print('Foram reconhecidos {} novos estudantes e {} atualizações.'
        .format(adicionados, atualizados))
        print()
        print('1. Adicionar mais veteranxs')
        print('0. Voltar')
        print()

    def resolver_opcao(self, opcao):
        if opcao == 0:
            self.saindo = True


class MenuAdicionarIngressantes(Menu):
    def __init__(self, curso):
        self.curso = curso
        # Chamamos o loop
        super().__init__(range(0, 1 + 1))

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
            if len(respostas) != 9:
                while True:
                    trava = input('Trava de segurança para cópia e cola, '
                    'digite -1: ')

                    # Apenas cancelamos se terminar com '-1', digitado pelo
                    # usuário.
                    if trava.endswith('-1'):
                        break

                # Avisamos o possível erro
                print('\n\nPode ter ocorrido um erro ao tentar interpretar '
                'input "{}"'.format(lido))
                break

            # Criamos o estudante-dicionário
            respostas_dict = {
                "data_formulario": respostas[0],
                "nome": respostas[2],
                "genero": respostas[3],
                "email": respostas[1],
                "telefone": respostas[4],
                "facebook_link": respostas[5],
                "curso": self.curso
            }

            # Buscamos algum estudante-objeto já existente
            ingressante = database.buscar(
                NOME_DICT_INGRESSANTES, respostas_dict
            )

            if ingressante == None:
                # Se não há existente, criamos
                ultimo_id = database.database[NOME_ID_INGRESSANTES] + 1
                respostas_dict['id'] = ultimo_id
                database.database[NOME_ID_INGRESSANTES] = ultimo_id
                ingressante = Ingressante(respostas_dict)
                # Adicionamos ao banco de dados
                database.adicionar_estudante(NOME_DICT_VETERANXS, ingressante)
                adicionados += 1
            else:
                # Confiamos que não é um duplicate e atualizamos se a data for
                # maior :)
                data_database = data_do_formulario(ingressante.data_formulario)
                data_atual = data_do_formulario(
                    respostas_dict['data_formulario']
                )

                # Vereficamos se precisamos atualizar
                if data_database < data_atual:
                    ingressante.atualizar(respostas_dict)
                    atualizados += 1

        print('Foram reconhecidos {} novos estudantes e {} atualizações.'
        .format(adicionados, atualizados))
        print()
        print('1. Adicionar mais ingressantes de mesmo curso')
        print('0. Voltar')
        print()

    def resolver_opcao(self, opcao):
        if opcao == 0:
            self.saindo = True


class MenuListarEstudantes(Menu):
    def __init__(self, nome_lista):
        self.nome_lista = nome_lista
        super().__init__(range(1, 4 + 1))

    def imprimir(self):
        print('Id\tNome')
        for id_, estudante in database.database[self.nome_lista].items():
            print('{}\t{}'.format(id_, estudante.nome))
        print('\n\n')
        print('1. Voltar')
        print('2. Adicionar veteranas(os)')
        print('3. Adicionar calouras(os) da CC')
        print('4. Adicionar calouras(os) da EC')
        print()

    def resolver_opcao(self, opcao):
        if opcao == 1:
            self.saindo = True
        elif opcao == 2:
            MenuAdicionarVeteranxs()
        elif opcao == 3:
            MenuAdicionarIngressantes(NOME_CURSO_CC)
        elif opcao == 4:
            MenuAdicionarIngressantes(NOME_CURSO_EC)


class MenuListarApadrinhamentos(Menu):
    def __init__(self):
        super().__init__([0])

    def imprimir(self):
        print('Digite "0" para sair.')

    def resolver_opcao(self, opcao):
        self.saindo = True


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

        for veteranx in database.database[NOME_DICT_VETERANXS].values():
            if veteranx.genero == NOME_GENERO_MASC:
                vet_gen_masc.append(veteranx)
            elif veteranx.genero == NOME_GENERO_FEM:
                vet_gen_fem.append(veteranx)
            elif veteranx.genero == NOME_GENERO_OUTROS:
                vet_gen_outros.append(veteranx)
            else:
                print('Algo inesperado aconteceu com o gênero de {}'.format(
                    veteranx.nome
                ))

        print('Há {} veteranos, {} veteranas e {} veteranxs'.format(
            len(vet_gen_masc), len(vet_gen_fem), len(vet_gen_outros))
        )

        for ingressante in database.database[NOME_DICT_INGRESSANTES].values():
            if ingressante.genero == NOME_GENERO_MASC:
                ing_gen_masc.append(ingressante)
            elif ingressante.genero == NOME_GENERO_FEM:
                ing_gen_fem.append(ingressante)
            elif ingressante.genero == NOME_GENERO_OUTROS:
                ing_gen_outros.append(ingressante)
            else:
                print('Algo inesperado aconteceu com o gênero de {}'.format(
                    ingressante.nome
                ))

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
        MenuListarApadrinhamentos.apadrinhar(vet_gen_masc, ing_gen_masc)
        MenuListarApadrinhamentos.apadrinhar(vet_gen_fem, ing_gen_fem)
        MenuListarApadrinhamentos.apadrinhar(vet_gen_outros, ing_gen_outros)

        print('\n\nDigite "0" para sair.')
        print('Digite "1" para ver a lista de apadrinhamentos.')

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


            if veteranx.curso == NOME_CURSO_CC:
                vet_cc.append(veteranx)
            elif veteranx.curso == NOME_CURSO_EC:
                vet_ec.append(veteranx)
            else:
                print('Algo inesperado aconteceu com o curso para {}'.format(
                    veteranx.nome
                ))

        # Separamos ingressantes por curso
        for ingressante in lista_ing:
            # Conferimos se x ingressante já tem madrinha ou padrinho


            if ingressante.curso == NOME_CURSO_CC:
                ing_cc.append(ingressante)
            elif ingressante.curso == NOME_CURSO_EC:
                ing_ec.append(ingressante)
            else:
                print('Algo inesperado aconteceu com o curso para {}'.format(
                    ingressante.nome
                ))

        # Apadrinhamos cada curso
        MenuApadrinhar.apadrinhar_curso(vet_cc, ing_cc)
        MenuApadrinhar.apadrinhar_curso(vet_ec, ing_ec)

    def apadrinhar_curso(vet, ing):
        # Seja para CC ou EC

        # Conferimos se é possível fazer pares (se não, deixamos para o
        # usuário)
        if (len(vet) == 0 and len(ing) > 0):
            print('Não há veteranxs disponíveis para:')
            for ingressante in ing:
                print('{}\t{}'.format(ingressante.id, ingressante.nome))
            print('\n')
            return

        # Fazemos os pares


# Aqui começa a execução do programa
print("=== Sistema de Apadrinhamento v0.1 -- Rafael Sartori ===\n")
# Criamos o banco de dados (__init__ será chamado e o banco de dados será lido
# ou criado de acordo com o padrão)
database = Database()

# Inicializamos o menu principal, a interação com o usuário começa e o caminho
# seguido dentro do programa ocorre de forma recursiva entre os menus.
MenuPrincipal()
