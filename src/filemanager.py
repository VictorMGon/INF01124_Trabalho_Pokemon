import struct
import os
import csv
from pokemonformat import *
from blockmanager import *

FILE_DOESNT_EXIST = "File doesn't exist"
FILE_ALREADY_EXISTS = "File already exists"
FILE_NOT_COMPATIBLE = "File is not compatible"
example_footer_data = 'AQUI DEVE SER INSERIDO A ARVORE DE INDEXACAO'

def processStr(str):
    return str

def processInt(str):
    return int(str)

def processType2(str):
    if str == '':
        return "None"
    return str

def alert_info(str):
    print(str)

class AbstractFileManager:
    #header:
    #{magic value: 4 bytes} = b'AAAA'
    files = {}
    magic_value = b'AFMG'
    def prepareHeader(self,tag):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_file.seek(0)
            cur_file.write(self.magic_value)
    def createFile(self,tag,name):
        f = open(name,'w+b')
        if tag in self.files:
            alert_info(FILE_ALREADY_EXISTS)
            return
        else:
            self.files[tag] = f
        self.prepareHeader(tag)
        return 1
    def loadFile(self,tag,name):
        f = open(name,'r+b')
        if tag in self.files:
            alert_info(FILE_ALREADY_EXISTS)
            return
        elif f.read(4) != self.magic_value:
            alert_info(FILE_NOT_COMPATIBLE)
            return
        else:
            self.files[tag] = f
        return 1
    def deleteFile(self,name):
        if os.path.exists(name):
            f = open(name,'rb')
            if self.magic_value == f.read(4):
                f.close()
                os.remove(name)
                return 1
            f.close()
            return 0
    def renameFile(self,old_name,new_name):
        if os.path.exists(old_name):
            f = open(old_name,'rb')
            if self.magic_value == f.read(4):
                f.close()
                os.rename(old_name,new_name)
                return 1
            f.close()
            return 0
    def getFile(self,tag):
        try:
            return self.files[tag]
        except KeyError:
            alert_info(FILE_DOESNT_EXIST)
            return
    def destroyFile(self,tag):
        try:
            self.files[tag].close()
            del self.files[tag]
            return 1
        except KeyError:
            alert_info(FILE_DOESNT_EXIST)
            return

FOOTER_LOC = 4
NEXT_REGISTER = 8
NEXTID = 12
LAST_REGISTER = 16
FIRST_REGISTER = 20

class RegisterFileManager(AbstractFileManager):
    #header:
    #{magic value: 4 bytes} = b'REGF'
    #{footer_loc: 4 bytes} = [offset to footer location]@@NOT DONE YET
    #{next_register: 4 bytes}
    #{nextID: 4 bytes}
    #{last_register: 4 bytes}
    #body:
    #{first_register: [register_bytes]}
    #{second_register: [register_bytes]}
    #{third_register: [register_bytes]}
    #...
    #footer:
    #{footer_data: [footer_bytes]}
    magic_value = b'REGF'
    files = {}
    last_register = {}
    next_register = {}
    nextID = {}
    def prepareHeader(self,tag):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_file.seek(0)
            cur_file.write(self.magic_value)
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            self.next_register[tag] = FIRST_REGISTER
    def loadFile(self,tag,name):
        f = open(name,'r+b')
        if tag in self.files:
            alert_info(FILE_ALREADY_EXISTS)
            return 0
        elif f.read(4) != self.magic_value:
            alert_info(FILE_NOT_COMPATIBLE)
            return 0
        else:
            self.files[tag] = f
            f.seek(NEXT_REGISTER)
            self.next_register[tag] = struct.unpack('i',f.read(4))[0]
            f.seek(NEXTID)
            self.nextID[tag] = struct.unpack('i',f.read(4))[0]
            f.seek(LAST_REGISTER)
            self.last_register[tag] = struct.unpack('i',f.read(4))[0]
        return 1
    def destroyFile(self,tag):
        try:
            self.files[tag].close()
            if tag in self.files:
                del self.files[tag]
            if tag in self.last_register:
                del self.last_register[tag]
            if tag in self.next_register:
                del self.next_register[tag]
            if tag in self.nextID:
                del self.nextID[tag]
            return 1
        except KeyError:
            alert_info(FILE_DOESNT_EXIST)
            return
    def saveState(self,tag):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_file.seek(NEXT_REGISTER)
            cur_file.write(struct.pack('i',self.next_register[tag]))
            cur_file.seek(NEXTID)
            cur_file.write(struct.pack('i',self.nextID[tag]))
            cur_file.seek(LAST_REGISTER)
            cur_file.write(struct.pack('i',self.last_register[tag]))
    def updateNextRegister(self,tag,new_pos):
        self.next_register[tag] = new_pos
    def getNextRegister(self,tag):
        return self.next_register[tag]
    def updateFooterLoc(self,tag,new_pos):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_file.seek(FOOTER_LOC)
            cur_file.write(struct.pack('i',new_pos))
    def dumpRegister(self,tag,data):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_pos = self.getNextRegister(tag)
            if tag in self.last_register:
                cur_file.seek(self.last_register[tag]+4)
                cur_file.write(struct.pack('i',cur_pos))
                cur_file.seek(cur_pos)
                cur_file.write(struct.pack('i',self.last_register[tag]))
            else:
                self.nextID[tag] = 0
                cur_file.write(struct.pack('i',-1))
            cur_file.write(struct.pack('i',-1))
            self.last_register[tag] = cur_pos
            cur_id = self.generateID(tag)
            cur_file.write(cur_id)
            cur_file.write(data)
            self.updateNextRegister(tag,cur_file.tell())
    def insertFooter(self,tag,data):
        cur_file = self.getFile(tag)
        if cur_file:
            footer_pos = self.getNextRegister(tag)
            self.updateFooterLoc(tag,footer_pos)
            cur_file.seek(footer_pos)
            cur_file.write(data)
    def generateID(self,tag):
        id = self.nextID[tag]
        self.nextID[tag] += 1
        return struct.pack('i',id)
    def deleteRegisters(self,file_name,id_array):
        res = self.loadFile(file_name,file_name)
        if res:
            if min(id_array) >= self.nextID[file_name]:
                self.destroyFile(file_name)
                return
            cur_file = self.getFile(file_name)
            self.createFile(file_name+'AUX',file_name+'.aux')
            cur_file.seek(FIRST_REGISTER)
            cur_pos = cur_file.tell()
            aux_reg_header_size = 12
            prev_reg_pos,next_reg_pos,cur_id = struct.unpack('iii',cur_file.read(aux_reg_header_size))
            reg_size_data = next_reg_pos - FIRST_REGISTER - aux_reg_header_size
            while True:
                if cur_id not in id_array:
                    reg_data = struct.unpack('%ds' % (reg_size_data),cur_file.read(reg_size_data))[0]
                    self.dumpRegister(file_name+'AUX',reg_data)
                if next_reg_pos == struct.unpack('i',b'\xFF\xFF\xFF\xFF')[0]:
                    break
                cur_pos = cur_file.seek(next_reg_pos)
                prev_reg_pos,next_reg_pos,cur_id = struct.unpack('iii',cur_file.read(aux_reg_header_size))
            self.insertFooter(file_name+'AUX',struct.pack('256s',example_footer_data.encode('utf-8')))
            self.saveState(file_name+'AUX')
            self.destroyFile(file_name+'AUX')

            self.destroyFile(file_name)
            self.deleteFile(file_name)
            self.renameFile(file_name+'.aux',file_name)
        return res
    def deleteRegister(self,file_name,id):
        self.deleteRegisters(file_name,[id])

class IndexCollection:
    def __init__(self,type,afmgr,bptree,ttree):
        self.type = type
        self.afmgr = afmgr
        self.bptree = bptree
        self.ttree = ttree
    def retrieve_bptree(self,id):
        return self.bptree[id]['tree']
    def retrieve_bptree_name(self,id):
        return self.bptree[id]['name']
    def retrieve_ttree(self,id):
        return self.ttree[id]['tree']
    def retrieve_ttree_name(self,id):
        return self.ttree[id]['name']
    def destroyIndex(self):
        for id,_ in enumerate(self.bptree):
            self.afmgr.destroyFile(self.retrieve_bptree_name(id))
        for id,_ in enumerate(self.ttree):
            self.afmgr.destroyFile(self.retrieve_ttree_name(id))


BPTREE_ORDER = 200

class IndexFileManager(RegisterFileManager):
    #header:
    #{magic value: 4 bytes} = b'IDXF'
    #{footer_loc: 4 bytes} = [offset to footer location]@@UNDER REVIEW
    #{next_register: 4 bytes}
    #{nextID: 4 bytes}
    #{last_register: 4 bytes}
    #body:
    #{first_register: [register_bytes]}
    #{second_register: [register_bytes]}
    #{third_register: [register_bytes]}
    #...
    #external file: index tree
    magic_value = b'IDXF'
    files = {}
    last_register = {}
    next_register = {}
    nextID = {}
    index_tree = {}
    #file_size = {}
    def createFile(self,tag,name,type):
        afm = AbstractFileManager()
        bptree = []
        ttree = []
        for id,index_name in enumerate(type.BPTreeAttr):
            afm.createFile(index_name,tag+'_'+index_name+'.idx')
            bmg_index = BPlusBlockManager(afm.getFile(index_name),4096)
            bp_index = BPlusTree(BPTREE_ORDER,bmg_index)
            bptree.append({'name':index_name,'tree':bp_index})
        for id,index_name in enumerate(type.TTreeAttr):
            afm.createFile(index_name,tag+'_'+index_name+'.idx')
            tmg_index = TrieBlockManager(afm.getFile(index_name),4096)
            t_index = TrieTree(tmg_index)
            bptree.append({'name':index_name,'tree':t_index})
        new_index = IndexCollection(type,afm,bptree,ttree)
        self.index_tree[tag] = new_index
        super().createFile(tag,name)
    def destroyFile(self,tag):
        try:
            self.files[tag].close()
            if tag in self.files:
                del self.files[tag]
            if tag in self.last_register:
                del self.last_register[tag]
            if tag in self.next_register:
                del self.next_register[tag]
            if tag in self.nextID:
                del self.nextID[tag]
            if tag in self.index_tree:
                self.index_tree[tag].destroyIndex()
                del self.index_tree[tag]
            return 1
        except KeyError:
            alert_info(FILE_DOESNT_EXIST)
            return
    def prepareHeader(self,tag):
        #should include register information before initializing index tree
        cur_file = self.getFile(tag)
        if cur_file:
            cur_file.seek(0)
            cur_file.write(self.magic_value)
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            cur_file.write(struct.pack('i',0))
            self.next_register[tag] = FIRST_REGISTER
            #initiate index tree for each attribute from the register type
    def dumpRegister(self,tag,data):
        cur_file = self.getFile(tag)
        if cur_file:
            cur_pos = self.getNextRegister(tag)
            if tag in self.last_register:
                cur_file.seek(self.last_register[tag]+4)
                cur_file.write(struct.pack('i',cur_pos))
                cur_file.seek(cur_pos)
                cur_file.write(struct.pack('i',self.last_register[tag]))
            else:
                self.nextID[tag] = 0
                cur_file.write(struct.pack('i',-1))
            cur_file.write(struct.pack('i',-1))
            self.last_register[tag] = cur_pos
            cur_id = self.generateID(tag)
            cur_file.write(cur_id)
            cur_file.write(data)
            self.updateNextRegister(tag,cur_file.tell())
            #insert each [attribute(key), file offset(value)] in the associated index tree
            idx_register = self.index_tree[tag].type()
            idx_register.fromBytes(data)
            bp_values, t_values = idx_register.indexEntries()
            for id,val in enumerate(bp_values):
                self.index_tree[tag].retrieve_bptree(id).insert(val,cur_pos)
            for id,val in enumerate(t_values):
                self.index_tree[tag].retrieve_ttree(id).insert(val,cur_pos)
            #self.index_tree[tag][2].insert(type.hp,cur_pos)
    def insertFooter(self,tag,data):
        cur_file = self.getFile(tag)
        if cur_file:
            footer_pos = self.getNextRegister(tag)
            #insert padding?
            #insert footer header as a function of the collection of index tree
            self.updateFooterLoc(tag,footer_pos)
            cur_file.seek(footer_pos)
            #merge each index tree into one big file
            cur_file.write(data)
            #update footer header with the new addresses
            #self.destroyFile(tag)
    def deleteRegisters(self,file_name,id_array):
        #TODO
        pass

def test_registerfile_1():
    example_pkmn = 'Bulbasaur,Grass,Poison,45,49,49,65,65,45'.split(',')
    example_pkmn2 = 'Ivysaur,Grass,Poison,60,62,63,80,80,60'.split(',')

    pos = [0,1,2,3,4,5,6,7,8]

    test = Pokemon()
    test.fromCSV(pos,example_pkmn)
    print(test)
    test2 = Pokemon()
    test2.fromCSV(pos,example_pkmn2)
    print(test2)

    fm = RegisterFileManager()
    fm.createFile('testfile','pokemon.dat')
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test2.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test2.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test2.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test2.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test2.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.insertFooter('testfile',struct.pack('256s',example_footer_data.encode('utf-8')))
    fm.saveState('testfile')
    fm.destroyFile('testfile')

def test_registerfile_2():
    fm = RegisterFileManager()
    fm.deleteRegisters('pokemon.dat',[0,2,50])

def test_registerfile_3():
    example_pkmn = 'Bulbasaur,Grass,Poison,45,49,49,65,65,45'.split(',')
    example_pkmn2 = 'Ivysaur,Grass,Poison,60,62,63,80,80,60'.split(',')

    pos = [0,1,2,3,4,5,6,7,8]

    test = Pokemon()
    test.fromCSV(pos,example_pkmn)

    test2 = Pokemon()
    test2.fromCSV(pos,example_pkmn2)

    fm = RegisterFileManager()
    fm.loadFile('testfile','pokemon.dat')
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.dumpRegister('testfile',test.serialize())
    fm.insertFooter('testfile',struct.pack('256s',example_footer_data.encode('utf-8')))
    fm.saveState('testfile')
    fm.destroyFile('testfile')

def test_indexfile_1():
    pos = [2,9,10,18,19,20,21,22,23]

    fm = IndexFileManager()
    fm.createFile('Pokemon','pokemon.dat',Pokemon)

    with open('pokedex.csv',newline='',encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        next(csv_reader)
        for row in csv_reader:
            cur_pokemon = Pokemon()
            cur_pokemon.fromCSV(pos,row)
            fm.dumpRegister('Pokemon',cur_pokemon.serialize())
        fm.insertFooter('Pokemon',struct.pack('256s',example_footer_data.encode('utf-8')))

    fm.saveState('Pokemon')

    #print(len(fm.index_tree['Pokemon'].retrieve_bptree(5).root.keys),'|',fm.index_tree['Pokemon'].retrieve_bptree(5).root.keys)
    #print(len(fm.index_tree['Pokemon'].retrieve_bptree(5).root.values),'|',fm.index_tree['Pokemon'].retrieve_bptree(5).root.values)

    print(fm.index_tree['Pokemon'].retrieve_bptree(5).retrieve(-50))

    fm.destroyFile('Pokemon')

if __name__ == '__main__':
    #test_registerfile_1()
    #test_registerfile_2()
    #test_registerfile_3()
    test_indexfile_1()
