import json
import os
from datetime import datetime
from estudantes import *


NOME_LISTA_VETERANXS = 'veteranxs'
NOME_LISTA_INGRESSANTES = 'ingressantes'
NOME_LISTA_APADRINHAMENTOS = 'apadrinhamentos'


def estudante_para_dicionario(database, nome_lista):
    """Função que transforma a lista de estudantes em uma estrutura compatível
    com JSON: uma lista de simples dicionários"""
    # OBS: estamos alterando o conteúdo de database, o que é interpretado como
    # passagem por referência

    # Removemos a lista de objetos
    estudantes = database.pop(nome_lista)
    # Substituímos por uma lista vazia
    database[nome_lista] = []

    while len(estudantes) > 0:
        # Transfornamos o estudante-objeto em dicionários simples para JSON
        estudante = estudantes.pop()
        # Adicionamos o dicionário a lista
        database[nome_lista].append(estudante.to_dict())

def dicionario_para_estudante(database, nome_lista):
    """Função que transforma a lista de dicionários em uma lista de
    estudantes"""

    # Removemos a lista de dicionários
    dict_estudantes = database.pop(nome_lista)
    # Substituímos por uma lista vazia
    database[nome_lista] = []

    while len(dict_estudantes) > 0:
        dicionario = dict_estudantes.pop()
        estudante = None

        # Transfornamos o estudante-dicionário em objetos
        if nome_lista == NOME_LISTA_VETERANXS:
            estudante = Veteranx(dicionario)
        else:
            estudante = Ingressante(dicionario)

        # Adicionamos o objeto a lista
        database[nome_lista].append(estudante)


def limpar_telefone(string):
    return string.replace('(', '').replace(')', '').replace(' ', '')


class Database:
    """Classe que armazena todas as funções de leitura, gravação, adição e
    remoção de estudantes"""
    # Definimos o nome do arquivo do banco de dados
    FILE_NAME = 'sist_apadrinhamento.json'

    def __init__(self):
        # Definimos o banco de dados padrão
        self.database = {
            NOME_LISTA_VETERANXS: [],
            NOME_LISTA_INGRESSANTES: [],
            NOME_LISTA_APADRINHAMENTOS: []
        }

        # Lemos/criamos o arquivo
        if os.path.exists(self.FILE_NAME):
            # Lemos o estado atual do banco de dados
            self.ler_banco()
        else:
            # Salvamos o banco de dados padrão
            self.salvar_banco()

    def salvar_banco(self):
        with open(self.FILE_NAME, 'w') as database_file:
            # Transformar as listas de pessoas em listas de dicinários
            estudante_para_dicionario(self.database, NOME_LISTA_VETERANXS)
            estudante_para_dicionario(self.database, NOME_LISTA_INGRESSANTES)

            # Transformar dicionário do banco de dados em JSON e escrever
            database_file.write(
                json.JSONEncoder(indent='    ').encode(self.database)
            )

    def ler_banco(self):
        with open(self.FILE_NAME, 'r') as database_file:
            # Ler o arquivo JSON para o dicionário do banco de dados
            self.database = json.load(database_file)

            # Transformar a lista de dicionários em lista de pessoas
            dicionario_para_estudante(self.database, NOME_LISTA_VETERANXS)
            dicionario_para_estudante(self.database, NOME_LISTA_INGRESSANTES)

    def adicionar_estudante(self, nome_lista, estudante):
        self.database[nome_lista].append(estudante)

    def buscar(self, nome_lista, respostas_dict):
        for estudante in self.database[nome_lista]:
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
        super().__init__(range(-1, 9))

    def imprimir(self):
        print("1. Listar madrinha(s) ou padrinho(s)")
        print("2. Adicionar madrinha(s) ou padrinho(s)")
        print("3. Remover madrinha(s) ou padrinho(s)")
        print()
        print("4. Listar caloura(s) ou calouro(s)")
        print("5. Adicionar caloura(s) ou calouro(s)")
        print("6. Remover caloura(s) ou calouro(s)")
        print()
        print("7. Listar apadrinhamentos")
        print("8. Apadrinhar automaticamente")
        print("9. Remover apadrinhamento(s)")
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
            MenuListarEstudantes(NOME_LISTA_VETERANXS)
        elif opcao == 2:
            MenuAdicionarVeteranxs()
        elif opcao == 4:
            MenuListarEstudantes(NOME_LISTA_INGRESSANTES)


def data_do_formulario(string):
    # Transforma a string que representa o horário de registro do formulário
    # usando o formato de tempo do formulário do Google
    return datetime.strptime(string, '%d/%m/%Y %H:%M:%S')


class MenuAdicionarVeteranxs(Menu):
    def __init__(self):
        # Chamamos o loop
        super().__init__(range(-1, 1))

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
                "numero_ingressantes":
                    MenuAdicionarVeteranxs.obter_num_ingressantes(respostas[6])
            }

            # Buscamos algum estudante-objeto já existente
            veteranx = database.buscar(NOME_LISTA_VETERANXS, respostas_dict)

            if veteranx == None:
                # Se não há existente, criamos
                respostas_dict['id'] = Veteranx.ultimo_id + 1
                veteranx = Veteranx(respostas_dict)
                # Adicionamos ao banco de dados
                database.adicionar_estudante(NOME_LISTA_VETERANXS, veteranx)
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


class MenuListarEstudantes(Menu):
    def __init__(self, nome_lista):
        self.nome_lista = nome_lista
        super().__init__(range(1, 3))

    def imprimir(self):
        print('Id\tNome')
        for estudante in database.database[self.nome_lista]:
            print('{}\t{}'.format(estudante.id, estudante.nome))
        print('\n\n')
        print('1. Voltar')
        print('2. Adicionar')
        print('3. Remover')
        print()

    def resolver_opcao(self, opcao):
        if opcao == 1:
            self.saindo = True
        elif opcao == 2:
            MenuAdicionarVeteranxs()

# Aqui começa a execução do programa
print("=== Sistema de Apadrinhamento v0.1 -- Rafael Sartori ===\n")
# Criamos o banco de dados (__init__ será chamado e o banco de dados será lido
# ou criado de acordo com o padrão)
database = Database()

# Inicializamos o menu principal, a interação com o usuário começa e o caminho
# seguido dentro do programa ocorre de forma recursiva entre os menus.
MenuPrincipal()
