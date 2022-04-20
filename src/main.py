import random
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
POKEMON_GEN = 8
POKEMON_TYPE1 = 9
POKEMON_TYPE2 = 10

MOVE_ID = 0
MOVE_PP = 1
MOVE_POW = 2
MOVE_ACC = 3
MOVE_GEN = 4
MOVE_TYPE = 5

PKMOVE_ID = 0
PKMOVE_MOVID = 1
PKMOVE_DEXID = 2

EQ_QUERY = 0
RANGE_QUERY = 1

pokemon_attrs = {'id':POKEMON_ID,'dexid':POKEMON_DEXID,'hp':POKEMON_HP,'atk':POKEMON_ATK,
                 'def':POKEMON_DEF,'spatk':POKEMON_SPATK,'spdef':POKEMON_SPDEF,'spd':POKEMON_SPD,'gen':POKEMON_GEN}

move_attrs = {'id':MOVE_ID,'pp':MOVE_PP,'pow':MOVE_POW,'acc':MOVE_ACC,'gen':MOVE_GEN}

class Query:
    def __init__(self,var,low,high,op):
        self.var = var
        self.low = low
        self.high = high
        self.op = op
        self.verifyOp()
    def verifyOp(self):
        print('test')
        return {'running':True}
    def doOp(fm):
        #do stuff
        pass

def processInt(x):
    try:
        return int(x)
    except ValueError:
        print("(*) Entrada inválida")

def insertSep():
    print('====================================================================')

def Exit(args=None):
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

def normalize(str):
    return re.sub(' +',' ',str.strip()).split()

def pesquisaGen(args):
    if len(args) >= 2 and args[1].isdigit():
        fm = args[0]
        gen = int(args[1])
        offsets = fm.index_tree['Pokemon'].retrieve_bptree(POKEMON_GEN).retrieve(gen)
        if len(args) == 3 and args[2].isdigit():
            random.shuffle(offsets)
            limit = int(args[2])
            offsets = offsets[:limit]
        Pokemon = [fm.loadRegister('Pokemon',offset)['register'] for offset in offsets]
        for pokemon in Pokemon:
            print(pokemon,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def pesquisaFortes(args):
    if len(args) >= 2:
        fm = args[0]
        type = normalizeStr(args[1])
        if type not in TYPES:
            print("(*) Tipo elementar não reconhecido")
            return {'running':True}
        fortes = fortes_elementar[type]
        offsets = []
        for forte in fortes:
            print(forte,':',Type2Int(forte))
            offsets += fm.index_tree['Pokemon'].retrieve_bptree(POKEMON_TYPE1).retrieve(Type2Int(forte))
        if len(args) == 3 and args[2].isdigit():
            random.shuffle(offsets)
            limit = int(args[2])
            offsets = offsets[:limit]
        Pokemon = [fm.loadRegister('Pokemon',offset)['register'] for offset in offsets]
        for pokemon in Pokemon:
            print(pokemon,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def pesquisaFracos(args):
    if len(args) >= 2:
        fm = args[0]
        type = normalizeStr(args[1])
        if type not in TYPES:
            print("(*) Tipo elementar não reconhecido")
            return {'running':True}
        fracos = fracos_elementar[type]
        offsets = []
        for fraco in fracos:
            offsets += fm.index_tree['Pokemon'].retrieve_bptree(POKEMON_TYPE1).retrieve(Type2Int(fraco))
        if len(args) == 3 and args[2].isdigit():
            random.shuffle(offsets)
            limit = int(args[2])
            offsets = offsets[:limit]
        Pokemon = [fm.loadRegister('Pokemon',offset)['register'] for offset in offsets]
        for pokemon in Pokemon:
            print(pokemon,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def classificaPokemon(args):
    if len(args) >= 4 and args[2].isdigit() and args[3].isdigit():
        fm = args[0]
        attr = normalizeStr(args[1])
        if attr not in pokemon_attrs:
            print("(*) Atributo não reconhecido")
            return {'running':True}
        else:
            attr = pokemon_attrs[attr]
        low = int(args[2])
        high = int(args[3])
        ordem = True
        if len(args) >= 5:
            try:
                map = {'normal':True,'reversa':False}
                ordem = map[args[4]]
            except:
                pass
        offsets = fm.index_tree['Pokemon'].retrieve_bptree(attr).range_retrieve(low,high,ordem)
        if len(args) == 6 and args[5].isdigit():
            limit = int(args[5])
            offsets = offsets[:limit]
        Pokemon = [fm.loadRegister('Pokemon',offset)['register'] for offset in offsets]
        for pokemon in Pokemon:
            print(pokemon,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def classificaAtaque(args):
    if len(args) >= 4 and args[2].isdigit() and args[3].isdigit():
        fm = args[0]
        attr = normalizeStr(args[1])
        if attr not in move_attrs:
            print("(*) Atributo não reconhecido")
            return {'running':True}
        else:
            attr = move_attrs[attr]
        low = int(args[2])
        high = int(args[3])
        ordem = True
        if len(args) >= 5:
            try:
                map = {'normal':True,'reversa':False}
                ordem = map[args[4]]
            except:
                pass
        offsets = fm.index_tree['Move'].retrieve_bptree(attr).range_retrieve(low,high,ordem)
        if len(args) == 6 and args[5].isdigit():
            limit = int(args[5])
            offsets = offsets[:limit]
        Moves = [fm.loadRegister('Move',offset)['register'] for offset in offsets]
        for move in Moves:
            print(move,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def listarAtaques(args):
    if len(args) == 2 and args[1].isdigit():
        fm = args[0]
        poke_id = int(args[1])
        pokemon_offsets = fm.index_tree['Pokemon'].retrieve_bptree(POKEMON_ID).retrieve(poke_id)
        Pokemon = [fm.loadRegister('Pokemon',offset)['register'] for offset in pokemon_offsets]
        pokedex_ids = [pokemon.pokedex_id for pokemon in Pokemon]
        pkmove_offsets = []
        for pokedex_id in pokedex_ids:
            pkmove_offsets += fm.index_tree['PokemonMove'].retrieve_bptree(PKMOVE_DEXID).retrieve(pokedex_id)
        PKmoves = [fm.loadRegister('PokemonMove',offset)['register'] for offset in pkmove_offsets]
        move_ids = [pkmove.move_id for pkmove in PKmoves]
        move_offsets = []
        for move_id in move_ids:
            move_offsets += fm.index_tree['Move'].retrieve_bptree(MOVE_ID).retrieve(move_id)
        Moves = [fm.loadRegister('Move',offset)['register'] for offset in move_offsets]
        for move in Moves:
            print(move,'\n')
    else:
        print("(*) Comando não suportado")
    return {'running':True}

def input_command():
    print("Listando comandos disponíveis, consulte o guia de uso para mais detalhes.")
    options = {'voltar':Exit,
               'pesquisaGen':pesquisaGen,
               'pesquisaFortes':pesquisaFortes,
               'pesquisaFracos':pesquisaFracos,
               'classificaPokemon':classificaPokemon,
               'classificaAtaque':classificaAtaque,
               'listarAtaques':listarAtaques}
    args = []
    show_options(options,numbers=False)
    query = normalize(input('>'))
    insertSep()
    if len(query)>0:
        cmd = query[0]
        try:
            handler = options[cmd]
            args = query[1:]
        except:
            print("(*) Comando não reconhecido")
            handler = lambda x: {'running':True}
    else:
        print("(*) Insira um comando")
        handler = lambda x: {'running':True}
    return handler,args

def CmdLoop(fm):
    input("Pressione qualquer tecla para continuar...\n")
    state = {'running':True}
    while state['running']:
        handler,args = input_command()
        state = handler([fm]+args)
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
    pos = [2,9,10,1,18,19,20,21,22,23,5]
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
    pos = [1,2,4,5,6,7]
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
        CmdLoop(fm)
        deinitFM(fm)
    else:
        print("(*) Não foi encontrado os arquivos essenciais")
        insertSep()
        ret,fm = importData()
        if ret:
            CmdLoop(fm)
        deinitFM(fm)
    return {'running':True}

def extractData(scraper):
    scraper.extractMovesURL()
    scraper.processMovesURL()
    scraper.dumpMoves()
    scraper.dumpMovesPKMN()
    return {'running':True}

def ScraperMain():
    scraper = PokemonMovesScraper()
    state = {'running':True}
    while state['running']:
        options = {'Voltar':Exit,
                   'Extrair dados':extractData}
        handler = input_options(options)
        state = handler(scraper)
    return {'running':True}

def show_info():
    print("Trabalho Final de CPD".center(40))
    print(
    "Equipe \"Raknat o Vewis\"\n",
    "Integrantes:\n",
    "(*) Paulo Voltaire Silveira da Luz Junior, implementação da árvore trie\n",
    "(*) Victor Machado Gonçalves, implementação da árvore B+ e entidades\n",
    "Descrição: Classificação dos Pokémons existentes na Pokédex da geração 1-8 sobre seus tiers competitivos,",
    "geração, tipagem elementar e descrever qual a possibilidade melhor contra um Pokémon em especifico"
    )

def show_options(options,numbers=True):
    for k,v in enumerate(options.keys()):
        if numbers:
            print(f'{k+1})'+v)
        else:
            print('@'+v)

def input_options(options):
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
    return handler

def mainLoop(options):
    state = {'running':True,'loaded':0}
    while state['running']:
        handler = input_options(options)
        state = handler()

options = {'Sair':Exit,'Iniciar Programa':Main,'Iniciar Scraper':ScraperMain}

show_info()

mainLoop(options)
