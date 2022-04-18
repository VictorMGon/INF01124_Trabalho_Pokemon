import struct
import os
from filemanager import *

class IndexableRegister:
    data_fmt = ''

    BPTreeAttr = []
    TTreeAttr = []

    def fromCSV(self, data):
        pass
    def fromBytes(self, data_bytes):
        pass
    def serialize(self):
        pass
    def indexEntries(self):
        pass

class Pokemon(IndexableRegister):
    data_fmt = '64s16s16siiiiii'

    BPTreeAttr = [
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
        name = ''
        type1 = ''
        type2 = ''
        hp = 0
        attack = 0
        defense = 0
        spattack = 0
        spdefense = 0
        speed = 0
    def fromCSV(self,pos,data):
        #data = data_str.split(',')
        self.name = processStr(data[pos[0]])
        self.type1 = processStr(data[pos[1]])
        self.type2 = processStr(data[pos[2]])
        self.hp = processInt(data[pos[3]])
        self.attack = processInt(data[pos[4]])
        self.defense = processInt(data[pos[5]])
        self.spattack = processInt(data[pos[6]])
        self.spdefense = processInt(data[pos[7]])
        self.speed = processInt(data[pos[8]])
    def fromBytes(self,data_bytes):
        data = struct.unpack(self.data_fmt,data_bytes)
        self.name = data[0].decode('utf-8')
        self.type1 = data[1].decode('utf-8')
        self.type2 = data[2].decode('utf-8')
        self.hp = data[3]
        self.attack = data[4]
        self.defense = data[5]
        self.spattack = data[6]
        self.spdefense = data[7]
        self.speed = data[8]
    def __str__(self):
        ret_str = ""
        ret_str += "Name: " + self.name + '\n'
        ret_str += "Main Type: " + self.type1 + '\n'
        ret_str += "Secondary Type: " + processType2(self.type2) + '\n'
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
                            self.hp,
                            self.attack,
                            self.defense,
                            self.spattack,
                            self.spdefense,
                            self.speed)
    def indexEntries(self):
        BPEntries = [self.hp,self.attack,self.defense,self.spattack,self.spdefense,self.speed]
        #TTEntries = [self.name,self.type1,self.type2]
        TTEntries = []
        return BPEntries,TTEntries
