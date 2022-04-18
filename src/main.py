from filemanager import *

fm = IndexFileManager()
fm.loadFile('Pokemon','pokemon.dat', Pokemon)

results = fm.index_tree['Pokemon'].retrieve_bptree(1).retrieve(3)

for result in results:
    print(fm.loadRegister('Pokemon',result)['register'],'\n')

fm.destroyFile('Pokemon')
