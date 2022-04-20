import struct
import os
from pokemon import *

class Move(IndexableRegister):
    '''
    Entidade Ataque no modelo ER, registro do tipo indexável
    '''
    data_fmt = '64s16siiii'

    BPTreeAttr = [
    'BPPP',
    'BPPOWER',
    'BPACC',
    'BPGEN',
    'BPTYPE'
    ]
    """
    TTreeAttr = [
    'TTNAME',
    'TTTYPE'
    ]
    """

    def __init__(self):
        self.name = ''
        self.type = ''
        self.pp = 0
        self.power = 0
        self.accuracy = 0
        self.generation = 0
        self.typeint = 0
    def fromCSV(self,pos,data):
        self.name = processStr(data[pos[0]])
        self.type = processStr(data[pos[1]])
        self.pp = processInt(data[pos[2]])
        self.power = processInt(data[pos[3]])
        self.accuracy = processInt(data[pos[4]])
        self.generation = processInt(data[pos[5]])
        self.typeint = Type2Int(self.type)
    def fromBytes(self,data_bytes):
        data = struct.unpack(self.data_fmt,data_bytes)
        self.name = data[0].decode('utf-8').rstrip('\0')
        self.type = data[1].decode('utf-8').rstrip('\0')
        self.pp = data[2]
        self.power = data[3]
        self.accuracy = data[4]
        self.generation = data[5]
        self.typeint = Type2Int(self.type)
    def __str__(self):
        ret_str = ""
        ret_str += "Move name: " + self.name + '\n'
        ret_str += "Move type: " + self.type + '\n'
        ret_str += "PP: " + str(self.pp) + '\n'
        ret_str += "Power: " + str(self.power) + '\n'
        ret_str += "Accuracy: " + str(self.accuracy) + '\n'
        ret_str += "Generation: " + str(self.generation)
        return ret_str
    def serialize(self):
        nameBytes = bytes(self.name,'utf-8')
        typeBytes = bytes(self.type,'utf-8')
        return struct.pack(self.data_fmt,
                            nameBytes,
                            typeBytes,
                            self.pp,
                            self.power,
                            self.accuracy,
                            self.generation)
    def indexEntries(self):
        BPEntries = [self.pp,self.power,self.accuracy,self.typeint]
        #TTEntries = [self.name,self.type]
        TTEntries = []
        return BPEntries,TTEntries
