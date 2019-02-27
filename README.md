# Sistema de apadrinhamento do CACo

Sistema utilizado pelo Centro Acadêmico da Computação (CACo) para automatizar
o apadrinhamento de ingressantes. Os formulários de inscrição do sistema de
apadrinhamentos podem ser feitos através de reverse-engineering do código ou
pedindo para alguém do CACo através da nossa página de contato do [nosso
site](www.caco.ic.unicamp.br).


## Estrutura do programa

#### estudante.py

A classe `Estudante` pode derivar em `Veteranx` ou em `Ingressante`. Ambos
possuem atributos que descrevem curso, genero e seu tipo (veteran\* ou
ingressante), além de atributos básicos como e-mail, um identificador (`id`, que
é um número único para cada estudante que incrementa com cada estudante
registrado).

Esse arquivo não possui mais nada de interessante, é apenas a descrição dessa
relação de classes.

#### database.py

Banco de dados especializado em lidar com a estrutura de estudante através de
dicionários.

Quando uma instância de estudante é adicionada mas já existe, o banco de dados
(que possui referência a tod\*s \*s estudantes) os identifica e salva
corretamente, atualizando as informações preenchidas com as da última submissão
do formulário. Ou seja, o banco de dados não aceita duplicata e mantém as
informações mais recentes.

Todas as informações são guardadas em um único arquivo JSON (legível por
humanos). Todos os atributos do arquivo podem ser renomeados alterando as
constantes da classe `Database`.

`Database` também é responsável por inicializar os valores de `Estudante` como
`id`. As funções dessa classe requerem o tipo de estudante que está sendo
lidado, isso é realizado pelo menu do programa, controlado pelo arquivo
`apadrinhamento.py`, documentado abaixo.

#### apadrinhamento.py

Inclui o código que controla menus e é o ponto de início de execução do
programa. Nesse arquivo também acontece a transcrição do formulário para
dicionários que serão usados pelo banco de dados.

A "main" cria a instância de banco de dados e abre o menu padrão.

##### Menus

Cada menu possui uma função para imprimir suas opções e uma função para
controlar a ação a partir da escolha de alguma opção.

Há vários menus para adicionarem informações do formulário de apadrinhamento
para o sistema de apadrinhamento. E outros apenas para listar estudantes ou
apadrinhamentos.

##### E-mail, mensagens

Para o e-mail, há uma classe `Mensagem` que pega as informações de estudante e
transforma para o devido gênero de cada pessoa.

##### Apadrinhamento

O apadrinhamento acontece no menu de apadrinhar, então pode-se definir, remover
ou ainda alterar regras do apadrinhamento com alguns `if-else`.


## Execução do programa

É necessário possuir `python` na versão 3 instalado no computador e executar o
script:

```
# python apadrinhamento.py
```

Agora é só mexer nos menus para fazer o que quer.

#### Inscrevendo veteran\*s e ingressantes

O formulário deve ser copiado através da planilha no navegador (que utiliza o
formato TSV -- parecido com CSV mas utiliza caractere `tab`) e colado no menu
correto.

Por exemplo, para inserir veteran\*s no sistema de apadrinhamento, abra o a
planilha de respostas do formulário de inscrição de veteran\*s, selecione tudo
(`Ctrl + A`), copie (`Ctrl + C`) e cole (`Ctrl + V`) no terminal que roda o menu
de inscrição de veteran\*.

Tome cuidado para registrar ingressantes, pois pode haver 3 tipos de formulário:

* Online (possui pergunta _"De qual curso você é?"_),
* Presencial - ciência da computação (é determinado pelo nome do formulário que
é para ser aberto na matrícula presencial da ciência da computação, assim não há pergunta _"de qual curso você é?"_, poupando \* ingressante),
* Presencial - engenharia de computação (idem);

Então você deve prestar atenção em qual está inscrevendo!

#### Apadrinhando

Após inscrever veteran\*s e ingressantes, execute o apadrinhamento pelo menu,
confira se tudo ocorreu como deveria imprimindo os apadrinhamentos.

#### Enviando e-mail a tod\*s

Confira se as mensagens estão corretas (é necessário escrever mensagens
utilizando o formato do programa -- para preencher corretamente os gêneros e
plural) antes de serem enviadas e tome cuidado com a senha do e-mail utilizado.

*Observação importante:* a conta do `students.ic.unicamp.br` para enviar o
e-mail deve possuir senha ASCII (não possuir caracteres especiais como 'ç',
'ã').

##### Configurando a mensagem de apadrinhamento

`TODO`
