import time
import json
import random
import os
import io
import smtplib
import getpass
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
    """
    Apenas copiei e modifiquei de https://stackoverflow.com/questions/10147455/

    Para mensagens que fogem dos caracteres ASCII, deve-se usar a string de 3
    aspas.
    """

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
    return string.replace('(', '').replace(')', '').replace(' ', '')\
    .replace('+', '')


class Database:
    """Classe que armazena todas as funções de leitura, gravação e adição de
    estudantes através de um banco de dados simples em JSON"""
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

    def salvar_banco(self, continuar=False):
        """Salva o banco de dados em um arquivo JSON, transformando estudantes
        em um dicionário com todas as informações relevantes.

        Esta função modifica o banco de dados na memória, o que significa
        que, se for utilizá-la durante a execução do programa, deverá
        transformar de volta os estudantes-dicionários para
        estudantes-objeto. Para isso, defina continuar como 'True'"""
        with open(self.FILE_NAME, 'w') as database_file:
            # Transformamos o dicionário (id, estudante objeto) em uma lista de
            # estudantes-dicionário
            estudante_para_dicionario(self.database, NOME_DICT_VETERANXS)
            estudante_para_dicionario(self.database, NOME_DICT_INGRESSANTES)

            # Transformar dicionário do banco de dados em JSON e escrever
            database_file.write(
                json.JSONEncoder(indent='    ').encode(self.database)
            )

            if continuar:
                dicionario_para_estudante(
                    self.database, NOME_DICT_VETERANXS
                )
                dicionario_para_estudante(
                    self.database, NOME_DICT_INGRESSANTES
                )

    def ler_banco(self):
        """Lê o arquivo JSON para a memória, transformando os dicionários que
        representam os estudantes em estudantes-objeto."""
        with open(self.FILE_NAME, 'r') as database_file:
            # Ler o arquivo JSON para o dicionário do banco de dados
            self.database = json.load(database_file)

            # Transformamos o dicionário de dicionários em pessoas
            dicionario_para_estudante(self.database, NOME_DICT_VETERANXS)
            dicionario_para_estudante(self.database, NOME_DICT_INGRESSANTES)

            apadrinhamentos_ = self.database.pop(NOME_DICT_APADRINHAMENTOS)
            self.database[NOME_DICT_APADRINHAMENTOS] = {}

            # Transformamos a string que representa o id em número
            for id_string, apadrinhados in apadrinhamentos_.items():
                id_ = int(id_string)
                self.database[NOME_DICT_APADRINHAMENTOS][id_] = apadrinhados

    def adicionar_estudante(self, nome_dict, estudante):
        """Adiciona um estudante ao dicionário de estudantes.
        Defini no topo o nome dos dicionários:
        NOME_DICT_VETERANXS e NOME_DICT_INGRESSANTES"""
        self.database[nome_dict][estudante.id] = estudante

    def buscar(self, nome_dict, respostas_dict):
        """Busca se há um estudante duplicado (definimos a igualdade como
        número de telefone ou e-mail, já que pessoas podem colocar apenas o
        primeiro nome) no dicionário que armazena os estudantes."""
        for estudante in self.database[nome_dict].values():
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
    """Classe de Menu, cria um loop infinito de opções a serem validadas.

    * Deve-se definir a função imprimir() e resolver_opcao(opcao).
    * A lista de opções válidas 'opcoes_validas' deve ser definida pelos
    inteiros a serem entrados pelo usuário."""

    def __init__(self, opcoes_validas):
        """Acredito que fazer um loop na __init__ não seja a melhor coisa..."""
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
        super().__init__(range(-1, 8 + 1))

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
        print("8. Enviar e-mail de apadrinhamento")
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
        elif opcao == 8:
            MenuEmailApadrinhamento()


def data_do_formulario(string):
    """Transforma a string que representa o horário no formulário do Google em
    um objeto datetime de Python, assim podemos comparar 2 datas"""
    return datetime.strptime(string, '%d/%m/%Y %H:%M:%S')


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
                ultimo_id = database.database[NOME_ID_VETERANXS] + 1
                respostas_dict['id'] = ultimo_id
                respostas_dict['emails_recebidos'] = []
                database.database[NOME_ID_VETERANXS] = ultimo_id
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
            if len(respostas) != 6:
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
                respostas_dict['emails_recebidos'] = []
                database.database[NOME_ID_INGRESSANTES] = ultimo_id
                ingressante = Ingressante(respostas_dict)
                # Adicionamos ao banco de dados
                database.adicionar_estudante(
                    NOME_DICT_INGRESSANTES, ingressante
                )
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
        super().__init__([0, 1])

    def imprimir(self):
        apadrinhamentos = database.database[NOME_DICT_APADRINHAMENTOS]
        veteranxs       = database.database[NOME_DICT_VETERANXS]
        ingressantes    = database.database[NOME_DICT_INGRESSANTES]

        # Imprimimos tudo
        for veteranx_id, ingressantes_ids in apadrinhamentos.items():
            veteranx = veteranxs[veteranx_id]
            print('\n{}\t1 a {}\t{}'.format(
                veteranx_id, veteranx.numero_ingressantes, veteranx.nome
            ))
            for ingressante_id in ingressantes_ids:
                ingressante = ingressantes[ingressante_id]
                print('\t{}\t{}'.format(ingressante_id, ingressante.nome))

        # OBS: isso pode causar um stack overflow (pois MenuApadrinhar também
        # possui uma ligação para MenuListarApadrinhamentos)
        print('\n\n')
        print('1. Apadrinhar')
        print('0. Voltar')

    def resolver_opcao(self, opcao):
        self.saindo = True
        if opcao == 1:
            MenuApadrinhar()


def contar_afilhadxs(estudante):
    return len(
        database.database[NOME_DICT_APADRINHAMENTOS].get(estudante.id, [])
    )


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

        # Separamos ingressantes por gênero
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

        print('{} ingressantes foram apadrinhados\n\n'.format(
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

        apadrinhamentos = database.database[NOME_DICT_APADRINHAMENTOS]

        # Separamos veteranxs por curso
        for veteranx in lista_vet:
            # Conferimos se x veteranx já tem muitas(os) afilhadas(os)
            if veteranx.numero_ingressantes > 0:
                atual = contar_afilhadxs(veteranx)
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
            possui = False
            for apadrinhados in apadrinhamentos.values():
                # Se o seu id está em alguma lista de pessoas apadrinhadas,
                # marcamos
                if ingressante.id in apadrinhados:
                    possui = True
                    break

            # Pulamos os que já possuem madrinha ou padrinho
            if possui:
                continue

            if ingressante.curso == NOME_CURSO_CC:
                ing_cc.append(ingressante)
            elif ingressante.curso == NOME_CURSO_EC:
                ing_ec.append(ingressante)
            else:
                print('Algo inesperado aconteceu com o curso para {}'.format(
                    ingressante.nome
                ))

        # Apadrinhamos cada curso
        numero_apadrinhado = 0
        numero_apadrinhado += MenuApadrinhar.apadrinhar_curso(vet_cc, ing_cc)
        numero_apadrinhado += MenuApadrinhar.apadrinhar_curso(vet_ec, ing_ec)
        return numero_apadrinhado

    def apadrinhar_curso(veteranxs, ingressantes):
        numero_apadrinhado = 0
        apadrinhamentos = database.database[NOME_DICT_APADRINHAMENTOS]
        # Seja para CC ou EC

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
            # Pegamos x veteranx que quer possuir um(a) afilhado(a) mas possui
            # a menor quantidade de afilhadas(os) na lista
            # Dessa forma, a distribuição fica igualitária
            # OBS: 'veteranxs' foi desorganizada no passado
            veteranx = None
            menor_quantidade = None
            for veteranx_ in veteranxs:
                quantidade = contar_afilhadxs(veteranx_)
                if (menor_quantidade is None or quantidade < menor_quantidade):
                    menor_quantidade = quantidade
                    veteranx = veteranx_

            # Se veteranx é nulo, significa que não há veteranxs suficientes
            if veteranx is None:
                print('Pessoa sem apadrinhamento: {}'.format(ingressante.nome))
                continue

            # Agora que temos um(a) veteranx, temos que removê-la(o) da lista
            veteranxs.remove(veteranx)

            # Adicionamos o ingressante como padrinho
            apadrinhados = apadrinhamentos.get(veteranx.id, [])
            apadrinhados.append(ingressante.id)
            apadrinhamentos[veteranx.id] = apadrinhados
            numero_apadrinhado += 1

            # Verificamos se o veteranx ainda pode possuir mais afilhadas(os)
            if (veteranx.numero_ingressantes < 0 or
                veteranx.numero_ingressantes > len(apadrinhados)):
                # Adicionamos e reorganizamos
                veteranxs.append(veteranx)
                random.shuffle(veteranxs)

        return numero_apadrinhado


class Mensagem:
    """Esta classe servirá para construir a mensagem do e-mail de maneira
    fácil. Para utilizá-la, precisará, de início, definir um estudante."""
    def __init__(self, mensagem_base):
        self.mensagem_base = mensagem_base

    def definir_estudante(self, estudante):
        self.mensagem = self.mensagem_base
        self.estudante = estudante

        # Substituímos o nome
        self.mensagem = self.mensagem.replace("{nome}", estudante.nome)

        # Verificamos se é veteranx
        self.is_veteranx = type(estudante) == Veteranx
        if self.is_veteranx:
            self.num_afilhadxs = contar_afilhadxs(estudante)

            # Pulamos xs veteranxs sem afilhadxs
            if self.num_afilhadxs == 0:
                return False

            # Criamos uma lista de apadrinhadxs
            apadrinhadxs = []

            for apadrinhadx_id in \
                database.database[NOME_DICT_APADRINHAMENTOS][estudante.id]:
                # Recebemos o objeto pelo ID
                apadrinhadx = \
                database.database[NOME_DICT_INGRESSANTES][apadrinhadx_id]
                # Adicionamos x apadrinhadx à lista
                apadrinhadxs.append(apadrinhadx)

            # Construímos informações dxs afilhadxs
            informacoes = u''
            while len(apadrinhadxs) > 0:
                apadrinhadx = apadrinhadxs.pop()
                # Adicionamos dados básicos
                dados = [apadrinhadx.nome, apadrinhadx.email]
                # Adicionamos telefone se disponível
                if len(apadrinhadx.telefone) > 0:
                    dados.append(apadrinhadx.telefone)
                # Adicionamos o facebook se disponível
                if len(apadrinhadx.facebook_link) > 0:
                    dados.append(apadrinhadx.facebook_link)

                # Juntamos toda a string com uma nova linha (isso não deve
                # ser feito para a última, pois depois de "{info_afilhada}"
                # haverá um '\n')
                if len(apadrinhadxs) == 0:
                    informacoes += u', '.join(dados)
                else:
                    informacoes += u', '.join(dados) + u'\n'

            # Substituimos as informações dxs afilhadxs
            self.mensagem = self.mensagem.replace("{info_afilhada}",
            informacoes)

        # Se é ingressante, substituímos x veteranx
        else:
            veteranx = None
            # Procuramos x veteranx
            for veteranx_id, lista_ing in \
                database.database[NOME_DICT_APADRINHAMENTOS].items():
                # Verificamos se está na lista de apadrinhamento
                if estudante.id in lista_ing:
                    # Guardamos x veteranx
                    veteranx = \
                        database.database[NOME_DICT_VETERANXS][veteranx_id]

            # Verificamos se um(a) veteranx foi definido
            if veteranx == None:
                # Pulamos o caso em que x estudante não foi apadrinhado
                return False

            # Construímos informações dxs afilhadxs
            informacoes = u''
            # Adicionamos dados básicos
            dados = [veteranx.nome, veteranx.email]
            # Adicionamos telefone se disponível
            if len(veteranx.telefone) > 0:
                dados.append(veteranx.telefone)
            # Adicionamos e-mail se disponível
            if len(veteranx.email) > 0:
                dados.append(veteranx.email)

            # Juntamos toda a string com uma nova linha
            informacoes += u', '.join(dados)

            # Substituimos as informações dxs afilhadxs
            self.mensagem = self.mensagem.replace("{info_veterana}",
            informacoes)

        # Retornamos sucesso para gênero masculino ou feminino
        return (self.estudante.genero == NOME_GENERO_MASC or
            self.estudante.genero == NOME_GENERO_FEM)

    def substituir_genero(self, keyword, subst_masc, subst_fem):
        if self.estudante.genero == NOME_GENERO_MASC:
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
        super().__init__(range(0, 2 + 1))

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
        print('2. Enviar com substituições para ingressantes (com informações '
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
            else:
                # Recebemos a mensagem como uma string UTF-8, já que temos
                # acentos rs
                with io.open(nome_arquivo, mode='r', encoding="utf-8") as \
                arquivo_mensagem:
                    mensagem_base = arquivo_mensagem.read()
                    self.mensagem = Mensagem(mensagem_base)
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
                if opcao == 1:
                    self.lista = NOME_DICT_VETERANXS
                elif opcao == 2:
                    self.lista = NOME_DICT_INGRESSANTES

                # Formatamos e enviamos os e-mails
                self.formatar_e_enviar(nome_arquivo)
                self.saindo = True

    def formatar_e_enviar(self, nome_arquivo):
        """Esta função irá criar um construtor, salvando a mensagem original e
        substituindo de acordo com cada estudante definido. Substituirá com
        base no ano de ingresso (calourx ou veteranx), no gênero e no número de
        afilhadxs se tiver."""

        # Pedimos credenciais
        sender = input('De qual e-mail em students.ic.unicamp.br você irá '
        'enviar? ')
        if not sender.endswith('@students.ic.unicamp.br'):
            sender = sender + '@students.ic.unicamp.br'

        password = getpass.getpass(prompt='Senha: ')

        # Confirmamos
        print('Irá enviar de "{}"?'.format(sender))
        confirmar = input('Digite -1 para confirmar: ')
        if not confirmar.endswith('-1'):
            return

        for estudante in database.database[self.lista].values():
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
                print('Enviado para {}. Esperando 3 '
                'segundos'.format(estudante.email))
                time.sleep(3)
            except:
                # Paramos de enviar caso ocorrer algum erro
                database.salvar_banco()
                print('Falha ao enviar para {}'.format(estudante.email))
                raise

        database.salvar_banco(continuar=True)


# Aqui começa a execução do programa
print("=== Sistema de Apadrinhamento v0.1 -- Rafael Sartori ===\n")
# Criamos o banco de dados (__init__ será chamado e o banco de dados será lido
# ou criado de acordo com o padrão)
database = Database()

# Inicializamos o menu principal, a interação com o usuário começa e o caminho
# seguido dentro do programa ocorre de forma recursiva entre os menus.
MenuPrincipal()
