import struct
import os
from src.register import *

def processInt(str):
    return int(str)

class PokemonMove(IndexableRegister):
    '''
    Modelagem da conexão da entidade Pokémon e entidade Ataque, registro do tipo indexável
    '''
    data_fmt = 'ii'

    BPTreeAttr = [
    'BPMOVID',
    'BPDEX'
    ]

    def __init__(self):
        self.move_id = 0
        self.pokedex_id = 0
    def fromCSV(self,pos,data):
        #data = data_str.split(',')
        self.move_id = processInt(data[pos[0]])
        self.pokedex_id = processInt(data[pos[1]])
    def fromBytes(self,data_bytes):
        data = struct.unpack(self.data_fmt,data_bytes)
        self.move_id = data[0]
        self.pokedex_id = data[1]
    def serialize(self):
        return struct.pack(self.data_fmt,
                            self.move_id,
                            self.pokedex_id)
    def indexEntries(self):
        BPEntries = [self.move_id,self.pokedex_id]
        TTEntries = []
        return BPEntries,TTEntries
