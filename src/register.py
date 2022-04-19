import struct
import os

class IndexableRegister:
    '''
    Registro abstrato do tipo indexável
    '''
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
