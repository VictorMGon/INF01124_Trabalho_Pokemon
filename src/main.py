from filemanager import *

fm = IndexFileManager()
fm.loadFile('Pokemon','pokemon.dat', Pokemon)
fm.loadFile('Move','move.dat', Move)
fm.loadFile('PokemonMove','pkmnmove.dat', PokemonMove)

results = fm.index_tree['PokemonMove'].retrieve_bptree(2).retrieve(1)

moves = [fm.loadRegister('PokemonMove',result)['register'].move_id for result in results]

for move in moves:
    move_offset = fm.index_tree['Move'].retrieve_bptree(0).retrieve(move)[0]
    move = fm.loadRegister('Move',move_offset)['register']
    print(move)

fm.destroyFile('Pokemon')
