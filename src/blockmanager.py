import struct
import pickle
import os
import cachetools
import time
from filemanager import *
from bplustree import *
from trietree import *

MAGIC_VALUE_LOC = 4
BLOCK_ID_LOC = 8
BLOCK_SIZE_LOC = 12
OFFSET_LOC = 16
ORDER_LOC = 20
DELETED_LOC = 24
cache_size = 200

COUNTER = 1

class AbstractBlockManager:
    '''
    Classe responsável para gerenciar blocos do tipo abstrato
    '''
    magic_value = b'BMGR'
    def __init__(self,file,offset=0,block_size = 4096):
        '''
        Inicializa o gerenciador de blocos utilizando um cache do tipo LRU(Least Recently Used)
        '''
        self.block_id = 0
        self.deleted_blocks = []
        self.block_size = block_size
        self.file = file
        self.offset = offset
        self.loaded = False
        self.cache = cachetools.LRUCache(maxsize=cache_size*block_size)
        self.checkFile()
    def generateID(self):
        '''
        Geração de códigos de identificação para blocos
        '''
        if self.deleted_blocks:
            #Se houve blocos deletados, tomar o código de identificação de algum bloco deletado
            unused_id = self.deleted_blocks.pop()
            return unused_id
        #Caso contrário, gerar um novo
        new_id = self.block_id
        self.block_id += 1
        return new_id
    def delete_block(self,b_id):
        '''
        Exclusão de bloco a partir do código de identificação
        '''
        self.deleted_blocks.append(b_id)
    def write_block(self,b_id,data):
        '''
        Escrita de blocos a partir do código de identificação e um conjunto de dados
        '''
        #Correção de tamanho
        if len(data)>=self.block_size:
            data = data[:self.block_size]
        elif len(data)<self.block_size:
            data += b'\x00'*(self.block_size-len(data))
        #Atualizar cache
        old_data = self.cache.get(b_id)
        self.cache[b_id] = data
        #Escrever dados
        self.file.seek(self.offset+self.block_size*b_id)
        self.file.write(data)
    def read_block(self,b_id):
        '''
        Leitura de blocos a partir do código de identificação
        '''
        #Verificar se está no cache
        data = self.cache.get(b_id)
        if data is not None:
            #Retornar caso esteja
            return data
        else:
            #Ler arquivo caso contrário
            self.file.seek(self.offset+self.block_size*b_id)
            data = self.file.read(self.block_size)
            self.cache[b_id] = data
        return data
    def checkFile(self):
        '''
        Função responsável para verificar se o arquivo é do tipo gerenciador de blocos
        '''
        self.file.seek(MAGIC_VALUE_LOC)
        if self.file.read(4) == self.magic_value:
            #Caso seja, carregar estado
            self.load_state()
    def load_state(self):
        '''
        Carregamento do estado
        '''
        self.file.seek(BLOCK_ID_LOC)
        self.block_id = struct.unpack('i',self.file.read(4))[0]
        self.file.seek(BLOCK_SIZE_LOC)
        self.block_size = struct.unpack('i',self.file.read(4))[0]
        self.file.seek(OFFSET_LOC)
        self.offset = struct.unpack('i',self.file.read(4))[0]
        self.file.seek(DELETED_LOC)
        deleted_count = struct.unpack('i',self.file.read(4))[0]
        for i in range(deleted_count):
            self.deleted_blocks.append(struct.unpack('i',self.file.read(4))[0])
        self.loaded = True
    def save_state(self):
        '''
        Armazenamento do estado(persistência)
        '''
        self.file.seek(MAGIC_VALUE_LOC)
        self.file.write(self.magic_value)
        self.file.seek(BLOCK_ID_LOC)
        self.file.write(struct.pack('i',self.block_id))
        self.file.seek(BLOCK_SIZE_LOC)
        self.file.write(struct.pack('i',self.block_size))
        self.file.seek(OFFSET_LOC)
        self.file.write(struct.pack('i',self.offset))
        self.file.seek(DELETED_LOC)
        self.file.write(struct.pack('i',len(self.deleted_blocks)))
        for i in range(len(self.deleted_blocks)):
            self.file.write(struct.pack('i',self.deleted_blocks[i]))

class OverflowBlockManager(AbstractBlockManager):
    '''
    Gerenciador de blocos com suporte de blocos overflow
    '''
    def write_bytes(self,cur_b_id,data):
        '''
        Escrita de bytes, gerando novos blocos dependendo do tamanho
        '''
        #0:{overflow_id : 4 bytes}
        #4:{total_size : 4 bytes}
        #8:{data: block_size - 8 bytes}
        data = struct.pack('i',-1) + struct.pack('i',-1) + data
        counter = 0
        #Enquanto o tamanho dos dados é maior que o tamanho de um bloco
        while len(data)>self.block_size:
            if counter >= MAX_SIZE:
                raise MemoryError('Block size has surpassed maximum write size')
            #Gerar novo bloco e atualizar o código de overflow
            next_b_id = self.generateID()
            data[:4] = struct.pack('i',next_b_id)
            #Escrever parcialmente no bloco atual os dados
            self.write_block(cur_b_id,bytes(data[:self.block_size]))
            data = struct.pack('i',-1) + data[self.block_size:]
            #Avançar para o próximo bloco
            cur_b_id = next_b_id
            counter += 1
        #Escrever restante no bloco final
        self.write_block(cur_b_id,bytes(data[:self.block_size]))
        counter += 1
        self.file.seek(self.offset+self.block_size*cur_b_id+4)
        self.file.write(struct.pack('i',counter))
    def insert_bytes(self,cur_b_id,data,new_data):
        '''
        Inserção de bytes, gerando novos blocos dependendo do tamanho
        '''
        #Se o tamanho dos dados mais o tamanho dos novos dados for maior que o tamanho do bloco
        if len(data)+len(new_data)>self.block_size:
            #Gerar novo bloco e inserir os dados atuais no bloco
            next_b_id = self.generateID()
            data[:4] = struct.pack('i',next_b_id)
            self.write_block(cur_b_id,bytes(data))
            #Zerar dados
            data = bytearray()
            data += struct.pack('i',-1)
            cur_b_id = next_b_id
        #Incluir novos dados
        data += new_data
        return cur_b_id,data
    def read_bytes(self,cur_b_id):
        '''
        Leitura de bytes, carregando adicionalmente os blocos de overflow se houver
        '''
        #Ler o bloco inicial
        data = self.read_block(cur_b_id)
        total_size = struct.unpack('i',data[4:8])
        if total_size >= MAX_SIZE:
            raise MemoryError('Block size has surpassed maximum read size')
        elif total_size > 1:
            #Se há overflow, obter próximo bloco
            next_b_id = struct.unpack('i',data[0:4])
            counter = 0
            while counter<total_size:
                #Adicionar dados até o último bloco overflow
                new_data = self.read_block(next_b_id)
                data += new_data
                next_b_id = struct.unpack('i',new_data[0:4])
                counter += 1
        else:
            #Caso contrário, retornar os dados da primeira leitura
            return data
    def pop_bytes(self,next_b_id,data,num):
        '''
        Obter N bytes, carregando do próximo bloco se houver overflow
        '''
        if len(data)<num:
            #Ler do próximo bloco caso nossa pilha não tenha o número de bytes pedido
            next_block_data = self.read_block(next_b_id)
            next_b_id = struct.unpack('i',bytes(next_block_data[:4]))[0]
            data = bytearray()
            data = next_block_data[4:]
        return next_b_id, data[:num], data[num:]
    def delete_blocks(self,b_id):
        '''
        Exclusão do bloco e blocos overflow associados
        '''
        cur_b_id = b_id
        #Deletar bloco atual
        self.delete_block(cur_b_id)
        data = bytearray(self.read_block(cur_b_id))
        if len(data)>0:
            #Enquanto há um código de overflow válido
            while bytes(data[:4]) != b'\xFF\xFF\xFF\xFF':
                next_b_id = struct.unpack('i',bytes(data[:4]))[0]
                data = bytearray(self.read_block(next_b_id))
                #Deletar próximo bloco
                self.delete_block(next_b_id)
    def delete_overflow_blocks(self,b_id):
        '''
        Exclusão dos blocos overflow
        '''
        cur_b_id = b_id
        data = bytearray(self.read_block(cur_b_id))
        if len(data)>0 and bytes(data[:4]) != b'\xFF\xFF\xFF\xFF':
            next_b_id = struct.unpack('i',bytes(data[:4]))[0]
            self.delete_blocks(next_b_id)

MAX_SIZE = 20000

class BPlusBlockManager(OverflowBlockManager):
    '''
    Gerenciador de blocos para árvore B+
    '''
    def delete_block(self,b_id):
        if b_id == 0:
            #Nunca deve acontecer, mas caso aconteça, temos um problema
            raise RuntimeError('Forbidden deletion: block id is the root id')
        super().delete_block(b_id)
    def delete_node(self,node):
        '''
        Exclusão de nodos
        '''
        cur_b_id = node.block_id
        self.delete_blocks(cur_b_id)
    def delete_overflow_nodes(self,node):
        '''
        Exclusão de blocos de overflow do nodo associado
        '''
        cur_b_id = node.block_id
        self.delete_overflow_blocks(cur_b_id)
    def write_node(self,node,delete_overflow=True):
        '''
        Serialização e escrita de nodos
        '''
        #0:{overflow_id : 4 bytes}
        #4:{total_size : 4 bytes}
        #8:{leaf : 1 byte}
        #9:{next : 4 bytes}
        #13:{previous : 4 bytes}
        #17:{key_count : 4 bytes}
        #21:{value_count : 4 bytes}
        #25:{first_key : 4 bytes}
        #{second_key : 4 bytes}
        #...
        #{first_value : variable}
        #{second_value : variable}
        #...
        #tic = time.perf_counter()
        if delete_overflow:
            self.delete_overflow_nodes(node)
        cur_b_id = node.block_id
        data = bytearray()
        next_b_id = struct.pack('i',-1)
        total_size = struct.pack('i',-1)
        leaf = int.to_bytes(node.leaf,1,'little')
        if node.next != None:
            next = struct.pack('i',node.next)
        else:
            next = struct.pack('i',-1)
        if node.previous != None:
            previous = struct.pack('i',node.previous)
        else:
            previous = struct.pack('i',-1)
        key_count = struct.pack('i',len(node.keys))
        value_count = struct.pack('i',len(node.values))
        data += next_b_id + total_size + leaf + next + previous + key_count + value_count
        counter = 1
        for i in range(len(node.keys)):
            if len(data)+4>self.block_size:
                counter += 1
            cur_b_id, data = self.insert_bytes(cur_b_id,data,struct.pack('i',node.keys[i]))
        if node.leaf:
            for i in range(len(node.values)):
                if len(data)+4>self.block_size:
                    counter += 1
                cur_b_id, data = self.insert_bytes(cur_b_id,data,struct.pack('i',len(node.values[i])))
                for j in range(len(node.values[i])):
                    if len(data)+4>self.block_size:
                        counter += 1
                    cur_b_id, data = self.insert_bytes(cur_b_id,data,struct.pack('i',node.values[i][j]))
        else:
            for i in range(len(node.values)):
                if len(data)+4>self.block_size:
                    counter += 1
                cur_b_id, data = self.insert_bytes(cur_b_id,data,struct.pack('i',node.values[i]))
        if len(data)<self.block_size:
            data += b'\x00'*(self.block_size-len(data))
        self.write_block(cur_b_id,bytes(data))
        self.file.seek(self.offset+self.block_size*node.block_id+4)
        self.file.write(struct.pack('i',counter))
        #toc = time.perf_counter()
        #print('write_node: ',toc-tic)
    def read_node(self,b_id):
        '''
        Deserialização e leitura de nodos
        '''
        data = bytearray(self.read_block(b_id))
        next_b_id = struct.unpack('i',bytes(data[:4]))[0]
        total_size = struct.unpack('i',bytes(data[4:8]))[0]
        leaf = bool(data[8])
        next = struct.unpack('i',bytes(data[9:13]))[0]
        previous = struct.unpack('i',bytes(data[13:17]))[0]
        key_count = struct.unpack('i',bytes(data[17:21]))[0]
        value_count = struct.unpack('i',bytes(data[21:25]))[0]
        data = data[25:]
        keys = []
        for i in range(key_count):
            next_b_id, new_bytes, data = self.pop_bytes(next_b_id,data,4)
            key = struct.unpack('i',new_bytes)[0]
            keys.append(key)
        values = []
        if leaf:
            #tic = time.perf_counter()
            for i in range(value_count):
                next_b_id, new_bytes, data = self.pop_bytes(next_b_id,data,4)
                sub_value_count = struct.unpack('i',new_bytes)[0]
                sub_values = []
                for j in range(sub_value_count):
                    next_b_id, new_bytes, data = self.pop_bytes(next_b_id,data,4)
                    value = struct.unpack('i',new_bytes)[0]
                    sub_values.append(value)
                values.append(sub_values)
            #toc = time.perf_counter()
            #print('read_node: ',toc-tic,'\n','value_count:',value_count,'\n','sub_value_count:',sub_value_count)
        else:
            for i in range(value_count):
                next_b_id, new_bytes, data = self.pop_bytes(next_b_id,data,4)
                value = struct.unpack('i',new_bytes)[0]
                values.append(value)
        node = BNode(self.order)
        node.keys = keys
        node.values = values
        node.leaf = leaf
        node.bm = self
        node.next = next
        node.previous = previous
        node.block_id = b_id
        return node
    def setOrder(self,order):
        '''
        Modificar ordem do gerenciador de blocos para árvore B+
        '''
        self.order = order
    def load_state(self):
        super().load_state()
        self.file.seek(ORDER_LOC)
        self.order = struct.unpack('i',self.file.read(4))[0]
    def save_state(self):
        super().save_state()
        self.file.seek(ORDER_LOC)
        self.file.write(struct.pack('i',self.order))

class TrieBlockManager(OverflowBlockManager):
    '''
    Gerenciador de blocos para árvore trie
    '''
    def write_node(self,b_id,node):
        #TODO
        pass
    def read_node(self,b_id):
        #TODO
        pass

def test_bplus1():
    abfm = AbstractFileManager()
    abfm.createFile('test','test.dat')
    file = abfm.getFile('test')
    order = 8
    bmgr = BPlusBlockManager(file,offset=4096,block_size = 4096)
    bmgr.setOrder(order)

    node = BNode(order)
    node.keys = []
    node.values = []
    node.leaf = True
    node.bm = bmgr
    node.next = None
    node.previous = None
    node.block_id = bmgr.generateID()
    bmgr.write_node(node)
    abfm.destroyFile('test')

def test_bplus2():
    abfm = AbstractFileManager()
    abfm.createFile('test','test.dat')
    file = abfm.getFile('test')
    order = 8
    bmgr = BPlusBlockManager(file,offset=4096,block_size = 4096)
    bmgr.setOrder(order)

    node = BNode(order)
    node.keys = [3,4,5]
    node.values = [1,2,3,4]
    node.leaf = False
    node.bm = bmgr
    node.next = None
    node.previous = None
    node.block_id = bmgr.generateID()

    bmgr.write_node(node)
    abfm.destroyFile('test')

def test_bplus3():
    abfm = AbstractFileManager()
    abfm.createFile('test','test.dat')
    file = abfm.getFile('test')
    order = 8
    bmgr = BPlusBlockManager(file,offset=4096,block_size = 4096)
    bmgr.setOrder(order)

    id = bmgr.generateID()

    node = BNode(order)
    node.keys = [i for i in range(1,600+1)]
    node.values = [i for i in range(1,601+1)]
    node.leaf = False
    node.bm = bmgr
    node.next = None
    node.previous = None
    node.block_id = id

    bmgr.write_node(node)

    read_node = bmgr.read_node(id)

    print(len(read_node.keys),'|',read_node.keys)
    print(len(read_node.keys),'|',read_node.values)

    abfm.destroyFile('test')

def test_bplus4():
    abfm = AbstractFileManager()
    abfm.createFile('test','test.dat')
    file = abfm.getFile('test')
    order = 8
    bmgr = BPlusBlockManager(file,offset=4096,block_size = 4096)
    bmgr.setOrder(order)

    id = bmgr.generateID()

    node = BNode(order)
    node.keys = [3,4,5]
    node.values = [[1,2],[2,3],[3,4],[4,5]]
    node.leaf = True
    node.bm = bmgr
    node.next = None
    node.previous = None
    node.block_id = id

    bmgr.write_node(node)

    read_node = bmgr.read_node(id)

    print(len(read_node.keys),'|',read_node.keys)
    print(len(read_node.values),'|',read_node.values)

    abfm.destroyFile('test')

def test_bplus5():
    abfm = AbstractFileManager()
    abfm.createFile('test','test.dat')
    file = abfm.getFile('test')
    order = 8
    bmgr = BPlusBlockManager(file,offset=4096,block_size = 4096)
    bmgr.setOrder(order)

    id = bmgr.generateID()

    node = BNode(order)
    node.keys = [i+1 for i in range(600)]
    node.values = [[i+1 for i in range(j,j+100)] for j in range(1201)]
    node.leaf = True
    node.bm = bmgr
    node.next = None
    node.previous = None
    node.block_id = id

    bmgr.write_node(node)


    read_node = bmgr.read_node(id)

    #print(len(read_node.keys),'|',read_node.keys)
    print(len(read_node.values),'|',read_node.values)

    bmgr.save_state()


    abfm.destroyFile('test')

def test_bplus6():
    abfm = AbstractFileManager()
    abfm.loadFile('test','test.dat')
    file = abfm.getFile('test')
    bmgr = BPlusBlockManager(file)

    print(bmgr.order)

    node = bmgr.read_node(0)

    print(len(node.keys),'|',node.keys)
    print(len(node.values),'|',node.values)

    abfm.destroyFile('test')
if __name__ == '__main__':
    #test_bplus1()
    #test_bplus2()
    #test_bplus3()
    #test_bplus4()
    #test_bplus5()
    #test_bplus6()
    pass
