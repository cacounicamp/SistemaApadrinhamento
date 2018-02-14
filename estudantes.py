
class Estudante:
    """Estudante é a estrutura básica de veteranx ou ingressante"""
    def __init__(self, dict_json):
        # Recebemos o dicionário que representa apenas uma pessoa
        self.id = dict_json['id']
        self.atualizar(dict_json)

    def atualizar(self, dict_atualizado):
        # Essas características não devem mudar entre respostas.. eu acho?
        # Vou deixar aqui para aqueles que clicaram ou digitaram errado
        self.nome = dict_atualizado['nome']
        self.genero = dict_atualizado['genero']
        self.curso = dict_atualizado['curso']
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
            "genero": self.genero,
            "email": self.email,
            "curso": self.curso,
            "telefone": self.telefone,
            "facebook_link": self.facebook_link
        }


class Veteranx(Estudante):
    """Veteranx é a estrutura Estudante com a variável do número de
    ingressantes que deseja apadrinhar e apelido"""

    def __init__(self, dict_json):
        super().__init__(dict_json)

    def atualizar(self, dict_atualizado):
        super().atualizar(dict_atualizado)
        # Apenas para madrinhas e padrinhos:
        self.apelido = dict_atualizado['apelido']
        self.numero_ingressantes = dict_atualizado['numero_ingressantes']

    def to_dict(self):
        dict_json = super().to_dict()
        dict_json['apelido'] = self.apelido
        dict_json['numero_ingressantes'] = self.numero_ingressantes
        return dict_json


class Ingressante(Estudante):
    """Ingressante é a estrutura Estudante que atualiza a variável de último
    id"""

    def __init__(self, dict_json):
        super().__init__(dict_json)
