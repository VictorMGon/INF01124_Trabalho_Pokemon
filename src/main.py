from filemanager import *

fm = IndexFileManager()
fm.loadFile('Pokemon','pokemon.dat', Pokemon)
fm.loadFile('Move','move.dat', Move)
fm.loadFile('PokemonMove','pkmnmove.dat', PokemonMove)

results = fm.index_tree['PokemonMove'].retrieve_bptree(2).retrieve(4)

moves = [fm.loadRegister('PokemonMove',result)['register'].move_id for result in results]

for move in moves:
    move_offset = fm.index_tree['Move'].retrieve_bptree(0).retrieve(move)[0]
    move = fm.loadRegister('Move',move_offset)['register']
    print(move,'\n')

results = fm.index_tree['PokemonMove'].retrieve_bptree(1).retrieve(0)

pokedex_ids = [fm.loadRegister('PokemonMove',result)['register'].pokedex_id for result in results]

for pokedex_id in pokedex_ids:
    pokemon_offsets = fm.index_tree['Pokemon'].retrieve_bptree(1).retrieve(pokedex_id)
    for pokemon_offset in pokemon_offsets:
        pokemon = fm.loadRegister('Pokemon',pokemon_offset)['register']
        print(pokemon,'\n')

fm.destroyFile('PokemonMove')
fm.destroyFile('Move')
fm.destroyFile('Pokemon')
