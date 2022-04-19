from filemanager import *
from scraper import *

nomes_arquivo1 = ['pokemon.dat','move.dat','pkmnmove.dat']

POKEMON_ID = 0
POKEMON_DEXID = 1
POKEMON_HP = 2
POKEMON_ATK = 3
POKEMON_DEF = 4
POKEMON_SPATK = 5
POKEMON_SPDEF = 6
POKEMON_SPD = 7

MOVE_ID = 0
MOVE_PP = 1
MOVE_POW = 2
MOVE_ACC = 3

PKMOVE_ID = 0
PKMOVE_MOVID = 1
PKMOVE_DEXID = 2

def processInt(x):
    try:
        return int(x)
    except ValueError:
        print("(*) Entrada inválida")

def insertSep():
    print('=============================')

def Exit():
    return {'running':False}

def deinitFM(fm):
    fm.destroyFile('PokemonMove')
    fm.destroyFile('Move')
    fm.destroyFile('Pokemon')
    del fm

def initFM():
    fm = IndexFileManager()
    fm.loadFile('Pokemon','pokemon.dat', Pokemon)
    fm.loadFile('Move','move.dat', Move)
    fm.loadFile('PokemonMove','pkmnmove.dat', PokemonMove)
    return fm

def QueryLoop(fm):
    input("Pressione qualquer tecla para continuar...\n")
    offsets = fm.index_tree['Pokemon'].retrieve_bptree(POKEMON_DEXID).retrieve(1)

    results = [fm.loadRegister('Pokemon',offset)['register'] for offset in offsets]

    for result in results:
        print(result)
    insertSep()

def importData():
    print("Importação dos dados".center(40))
    insertSep()
    print("Importando dados da entidade Pokémon")
    path_poke = input("Insira o nome do arquivo: ")
    if os.path.isfile(path_poke):
        print("(*) Foi encontrado os dados da entidade Pokémon")
    else:
        print("(*) Não foi encontrado os dados da entidade Pokémon")
        return 0
    insertSep()
    print("Importando dados da entidade Ataque")
    path_move = input("Insira o nome do arquivo: ")
    if os.path.isfile(path_move):
        print("(*) Foi encontrado os dados da entidade Ataque")
    else:
        print("(*) Não foi encontrado os dados da entidade Ataque")
        return 0
    insertSep()
    print("Importando dados da relação Pokémon e Ataque")
    path_pkmnmove = input("Insira o nome do arquivo: ")
    if os.path.isfile(path_pkmnmove):
        print("(*) Foi encontrado os dados da relação Pokémon e Ataque")
    else:
        print("(*) Não foi encontrado os dados da relação Pokémon e Ataque")
        return 0
    insertSep()
    print("(*) Inicializando gerador de arquivos")
    fm = IndexFileManager()
    insertSep()

    print("(*) Inserindo registros Pokémon(tempo estimado: 1-3 segundos)")
    pos = [2,9,10,1,18,19,20,21,22,23]
    fm.createFile('Pokemon','pokemon.dat',Pokemon)
    tic = time.perf_counter()
    with open(path_poke,newline='',encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        next(csv_reader)
        for row in csv_reader:
            cur_pokemon = Pokemon()
            cur_pokemon.fromCSV(pos,row)
            fm.dumpRegister('Pokemon',cur_pokemon.serialize())
        fm.insertFooter('Pokemon')
    toc = time.perf_counter()
    print(f"(*) Inserção dos registros Pokémon foi terminada em {toc-tic:.2f} segundos")
    fm.save_state('Pokemon')

    print("(*) Inserindo registros Ataque(tempo estimado: 1-3 segundos)")
    pos = [1,2,4,5,6]
    fm.createFile('Move','move.dat',Move)
    tic = time.perf_counter()
    with open('moves.csv',newline='',encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        next(csv_reader)
        for row in csv_reader:
            cur_move = Move()
            cur_move.fromCSV(pos,row)
            fm.dumpRegister('Move',cur_move.serialize())
        fm.insertFooter('Move')
    toc = time.perf_counter()
    print(f"(*) Inserção dos registros Ataque foi terminada em {toc-tic:.2f} segundos")
    fm.save_state('Move')

    print("(*) Inserindo registros da relação Pokémon e Ataque(tempo estimado: 1-2 minutos)")
    pos = [1,2]
    fm.createFile('PokemonMove','pkmnmove.dat',PokemonMove)
    tic = time.perf_counter()
    with open('movespkmn.csv',newline='',encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        next(csv_reader)
        for row in csv_reader:
            cur_entry = PokemonMove()
            cur_entry.fromCSV(pos,row)
            #print(cur_entry.move_id)
            fm.dumpRegister('PokemonMove',cur_entry.serialize())
        fm.insertFooter('PokemonMove')
    toc = time.perf_counter()
    print(f"(*) Inserção dos registros da relação Pokémon e Ataque foi terminada em {toc-tic:.2f} segundos")
    fm.save_state('PokemonMove')
    return 1,fm

def Main():
    counter = 0
    for nome in nomes_arquivo1:
        if os.path.isfile(nome):
            counter += 1
    if counter == 3:
        print("(*) Todos os arquivos essenciais foram encontrados")
        insertSep()
        fm = initFM()
        QueryLoop(fm)
        deinitFM(fm)
    else:
        print("(*) Não foi encontrado os arquivos essenciais")
        insertSep()
        ret,fm = importData()
        if ret:
            QueryLoop(fm)
        deinitFM(fm)
    return {'running':True}

def ScraperMain():
    print('test'*10)
    return {'running':True}

def show_info():
    print("Trabalho Final de CPD".center(40))
    print(
    "Equipe \"Raknat o Vewis\"\n",
    "Integrantes:\n",
    "(*) Paulo Voltaire Silveira da Luz Junior\n",
    "(*) Victor Machado Gonçalves\n",
    "Descrição: Classificação dos Pokémons existentes na Pokédex da geração 1-8 sobre seus tiers competitivos,",
    "geração, tipagem elementar e descrever qual a possibilidade melhor contra um Pokémon em especifico"
    )

def show_options(options):
    for k,v in enumerate(options.keys()):
        print(f'{k+1})'+v)

def mainLoop(options):
    state = {'running':True,'loaded':0}
    while state['running']:
        show_options(options)
        insertSep()
        selection = processInt(input("Insira sua opção: "))
        while selection not in range(1,len(options)+1):
            insertSep()
            show_options(options)
            insertSep()
            selection = processInt(input("Insira sua opção: "))
        option = list(options)[selection-1]
        handler = options[option]
        state = handler()

options = {'Sair':Exit,'Iniciar Programa':Main,'Iniciar Scraper':ScraperMain}

show_info()

mainLoop(options)
