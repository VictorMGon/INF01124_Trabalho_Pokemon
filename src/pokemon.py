import struct
import os
import unicodedata
from register import *

TYPES =[
'bug','dark','dragon','electric','fairy','fighting','fire','flying','ghost',
'grass','ground','ice','normal','poison','psychic','rock','steel','water']

fortes_elementar = {'normal':  ['fighting'],
                    'fighting':['flying','psychic','fairy'],
                    'flying':  ['rock','electric','ice'],
                    'poison':  ['ground','psychic'],
                    'ground':  ['water','grass'],
                    'rock':    ['fighting','ground','steel','water','grass'],
                    'bug':     ['flying','rock','fire'],
                    'ghost':   ['ghost','dark'],
                    'steel':   ['fighting','ground','fire'],
                    'fire':    ['ground','rock','water'],
                    'water':   ['grass','electric'],
                    'grass':   ['flying','poison','bug','fire','ice'],
                    'electric':['ground'],
                    'psychic': ['bug','ghost'],
                    'ice':     ['fighting','rock','steel','fire'],
                    'dragon':  ['ice','dragon','fairy'],
                    'dark':    ['fighting','bug','fairy'],
                    'fairy':   ['poison','steel']}

fracos_elementar = {'normal':  ['ghost'],
                    'fighting':['rock','bug'],
                    'flying':  ['fighting','ground','bug','grass'],
                    'poison':  ['fighting','poison','bug','grass','fairy'],
                    'ground':  ['poison','rock','electric'],
                    'rock':    ['normal','flying','poison','fire'],
                    'bug':     ['fighting','ground','grass'],
                    'ghost':   ['normal','fighting','poison','bug'],
                    'steel':   ['normal','flying','rock','bug','steel','grass','psychic','ice','dragon','fairy'],
                    'fire':    ['bug','steel','fire','grass'],
                    'water':   ['steel','fire','water','ice'],
                    'grass':   ['ground','water','grass','electric'],
                    'electric':['flying','steel','electric'],
                    'psychic': ['fighting','psychic'],
                    'ice':     ['ice'],
                    'dragon':  ['fire','water','grass','electric'],
                    'dark':    ['ghost','psychic','dark'],
                    'fairy':   ['fighting','bug','dragon','dark']}

def processStr(str):
    return str

def processInt(str):
    return int(str)

def processType2(str):
    if str == '':
        return "None"
    return str

def normalizeStr(str):
    return unicodedata.normalize('NFKD',str.lower().strip('\0'))

def Type2Int(str):
    dict = {TYPES[i]:i for i in range(len(TYPES))}
    str = normalizeStr(str)
    try:
        ret_int = dict[str]
    except:
        ret_int = -1
    return ret_int

def Int2Type(int):
    dict = {i:TYPES[i].capitalize() for i in range(len(TYPES))}
    try:
        ret_str = dict[int]
    except:
        ret_str = ''
    return ret_str


class Pokemon(IndexableRegister):
    '''
    Entidade Pokemon no modelo ER, registro do tipo indexável
    '''
    data_fmt = '64s16s16siiiiiiii'

    BPTreeAttr = [
    'BPDEX',
    'BPHP',
    'BPATK',
    'BPDEF',
    'BPSPATK',
    'BPSPDEF',
    'BPSPD',
    'BPGEN',
    'BPTYPE1',
    'BPTYPE2'
    ]
    """
    TTreeAttr = [
    'TTNAME'
    ]
    """

    def __init__(self):
        self.name = ''
        self.type1 = ''
        self.type2 = ''
        self.pokedex_id = 0
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.speed = 0
        self.generation = 0
        self.type1int = 0
        self.type2int = 0
    def fromCSV(self,pos,data):
        #data = data_str.split(',')
        self.name = processStr(data[pos[0]])
        self.type1 = processStr(data[pos[1]])
        self.type2 = processStr(data[pos[2]])
        self.pokedex_id = processInt(data[pos[3]])
        self.hp = processInt(data[pos[4]])
        self.attack = processInt(data[pos[5]])
        self.defense = processInt(data[pos[6]])
        self.spattack = processInt(data[pos[7]])
        self.spdefense = processInt(data[pos[8]])
        self.speed = processInt(data[pos[9]])
        self.generation = processInt(data[pos[10]])
        self.type1int = Type2Int(self.type1)
        self.type2int = Type2Int(self.type2)
    def fromBytes(self,data_bytes):
        data = struct.unpack(self.data_fmt,data_bytes)
        self.name = data[0].decode('utf-8').rstrip('\0')
        self.type1 = data[1].decode('utf-8').rstrip('\0')
        self.type2 = data[2].decode('utf-8').rstrip('\0')
        self.pokedex_id = data[3]
        self.hp = data[4]
        self.attack = data[5]
        self.defense = data[6]
        self.spattack = data[7]
        self.spdefense = data[8]
        self.speed = data[9]
        self.generation = data[10]
        self.type1int = Type2Int(self.type1)
        self.type2int = Type2Int(self.type2)
    def __str__(self):
        ret_str = ""
        ret_str += "Name: " + self.name + '\n'
        ret_str += "Main Type: " + self.type1 + '\n'
        ret_str += "Secondary Type: " + processType2(self.type2) + '\n'
        ret_str += "Pokedex Number: " + str(self.pokedex_id) + '\n'
        ret_str += "HP: " + str(self.hp) + '\n'
        ret_str += "Attack: " + str(self.attack) + '\n'
        ret_str += "Defense: " + str(self.defense) + '\n'
        ret_str += "SP Attack: " + str(self.spattack) + '\n'
        ret_str += "SP Defense: " + str(self.spdefense) + '\n'
        ret_str += "Speed: " + str(self.speed) + '\n'
        ret_str += "Generation: " + str(self.generation)
        return ret_str
    def serialize(self):
        nameBytes = bytes(self.name,'utf-8')
        type1Bytes = bytes(self.type1,'utf-8')
        type2Bytes = bytes(self.type2,'utf-8')
        return struct.pack(self.data_fmt,
                            nameBytes,
                            type1Bytes,
                            type2Bytes,
                            self.pokedex_id,
                            self.hp,
                            self.attack,
                            self.defense,
                            self.spattack,
                            self.spdefense,
                            self.speed,
                            self.generation)
    def indexEntries(self):
        BPEntries = [self.pokedex_id,self.hp,self.attack,self.defense,self.spattack,self.spdefense,self.speed,self.generation,self.type1int,self.type2int]
        #TTEntries = [self.name,self.type1,self.type2]
        TTEntries = []
        return BPEntries,TTEntries
