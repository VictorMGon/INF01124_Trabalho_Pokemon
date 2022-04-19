import struct
import os
from register import *

def processStr(str):
    return str

def processInt(str):
    return int(str)

def processType2(str):
    if str == '':
        return "None"
    return str

class Pokemon(IndexableRegister):
    data_fmt = '64s16s16siiiiiii'

    BPTreeAttr = [
    'BPDEX',
    'BPHP',
    'BPATK',
    'BPDEF',
    'BPSPATK',
    'BPSPDEF',
    'BPSPD'
    ]
    """
    TTreeAttr = [
    'TTNAME',
    'TTTYPE1',
    'TTTYPE2',
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
        ret_str += "Speed: " + str(self.speed)
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
                            self.speed)
    def indexEntries(self):
        BPEntries = [self.pokedex_id,self.hp,self.attack,self.defense,self.spattack,self.spdefense,self.speed]
        #TTEntries = [self.name,self.type1,self.type2]
        TTEntries = []
        return BPEntries,TTEntries
