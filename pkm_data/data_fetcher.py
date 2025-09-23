import requests
import json

def guardar_json(datos, nombre_archivo):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Datos guardados correctamente en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

def save_moves():
    moves = {}
    for i in range(1, 400):
        print(f"Obteniendo datos del movimiento {i}...")
        res = requests.get(f"https://pokeapi.co/api/v2/move/{i}")
        if res.status_code == 200:
            result = res.json()
            # Si hay alguna descripción del firered-leafgreen, guardo el movimiento, sino no
            # Si el movimiento es de estado, no lo guardo
            if(result["damage_class"]["name"] == "physical" or result["damage_class"]["name"] == "special"):
                for entry in result["flavor_text_entries"]:
                    if entry["version_group"]["name"] == "firered-leafgreen":
                        moves[result["name"]] = result["priority"]
        elif res.status_code == 404:
            print(f"Fin de búsqueda de movimientos en el número {i}")
            break
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(moves, "./pkm_data/moves_priority.json")

def save_pokedex():
    try:
        with open('./pkm_data/moves_priority.json', 'r', encoding='utf-8') as archivo:
            moves = json.load(archivo)
    except Exception as e:
        print(f"Es necesario guardar los movimientos primero: {e}")
        return

    pkdex = {}
    for i in range(1, 152):
        print(f"Obteniendo datos del Pokémon {i}...")
        pkm={}
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}")
        if res.status_code == 200:
            result = res.json()

            pkm["name"] = result["species"]["name"].capitalize()
            pkm["types"] = [t["type"]["name"] for t in result["types"]]
            pkm["abilities"] = result["abilities"][0]["ability"]["name"]
            pkm["sprite"] = result["sprites"]["front_default"]
            pkm["speed"] = result["stats"][5]["base_stat"]
            pkm["moves"] = {}

            for move in result["moves"]:
                for detail in move["version_group_details"]:
                    if detail["version_group"]["name"] == "firered-leafgreen" and detail["move_learn_method"]["name"] == "level-up" and move["move"]["name"] in moves:
                        pkm["moves"][move["move"]["name"]] = {
                            "level": detail["level_learned_at"],
                            "method": detail["move_learn_method"]["name"]

                        }
                        
                        break
            
            pkdex[i] = pkm
            
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(pkdex, "./pkm_data/pkdex.json")

def save_evolutions():
    evolutions = {}
    # Obtener las evoluciones de los pokémon de la 1ª generación
    for i in range(1, 152):
        print(f"Obteniendo datos de la evolución {i}...")
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{i}")
        if res.status_code == 200:
            result = res.json()
            chain_url = result["evolution_chain"]["url"]
            res_chain = requests.get(chain_url)
            
            def get_evolution_chain_data(evolution_data):
                """
                Procesa los datos de la cadena de evolución de la PokeAPI
                y devuelve un diccionario donde la clave es el ID del Pokémon que evoluciona
                y el valor es [id_evolucion, metodo_evolucion, nivel_objeto]
                """
                evolution_dict = {}
                
                def process_chain(chain, current_id):
                    for evolution in chain.get('evolves_to', []):
                        # Obtener el ID del Pokémon evolucionado
                        species_url = evolution['species']['url']
                        evolved_id = int(species_url.split('/')[-2])
                        
                        # Procesar los detalles de evolución
                        for detail in evolution['evolution_details']:
                            trigger_name = detail['trigger']['name']
                            
                            # Determinar el tercer valor de la tupla
                            third_value = None
                            
                            if trigger_name == 'level-up':
                                third_value = detail['min_level'] or 0
                            elif trigger_name == 'use-item':
                                third_value = detail['item']['name'] if detail['item'] else 'unknown-item'
                            elif trigger_name == 'trade':
                                third_value = 'trade'
                                if detail['trade_species']:
                                    third_value = f"trade-with-{detail['trade_species']['name']}"
                            else:
                                third_value = trigger_name
                                if detail['item']:
                                    third_value = detail['item']['name']
                            
                            # Agregar al diccionario
                            evolution_dict[current_id] = [evolved_id, trigger_name, third_value]
                        
                        # Procesar recursivamente las siguientes evoluciones
                        process_chain(evolution, evolved_id)
                
                # Obtener el ID del Pokémon inicial
                initial_species_url = evolution_data['chain']['species']['url']
                initial_id = int(initial_species_url.split('/')[-2])
                
                # Iniciar el procesamiento
                process_chain(evolution_data['chain'], initial_id)
                
                return evolution_dict

            if res_chain.status_code == 200:
                chain_data = res_chain.json()
                evolution_chain = get_evolution_chain_data(chain_data)
                
                for pokemon_id, evolution_data in evolution_chain.items():
                    evolutions[pokemon_id] = evolution_data
                    
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(evolutions, "./pkm_data/evolutions.json")

while True:
    print("Script para obtener datos de la POKE API")
    print("Qué datos quieres guardar?")
    print("1. Pokédex 1-151 pokémon")
    print("2. Movimientos")
    print("3. Evoluciones")
    print("4. Exit")

    option = input("Selecciona una opción: ")
    if option != "1" and option != "2" and option != "3" and option != "4":
        print("Opción no válida")
        exit()

    option = int(option)

    if option == 1:
        save_pokedex()
    elif option == 2:
        save_moves()
    elif option == 3:
        save_evolutions()
    elif option == 4:
        exit()