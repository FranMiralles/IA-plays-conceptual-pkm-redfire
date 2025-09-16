import requests
import json

def guardar_json(datos, nombre_archivo):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Datos guardados correctamente en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
1
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
                        move = {}
                        move["name"] = result["name"]
                        move["priority"] = result["priority"]
                        moves[i] = move
        elif res.status_code == 404:
            print(f"Fin de búsqueda de movimientos en el número {i}")
            break
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(moves, "./pkm_data/moves.json")

def save_pokedex():
    try:
        with open('./pkm_data/moves.json', 'r', encoding='utf-8') as archivo:
            moves = json.load(archivo)
    except Exception as e:
        print(f"Es necesario guardar los movimientos primero: {e}")
        return
    
    def get_key_with_value(dict, search_value):
        for key, value in dict.items():
            if value["name"] == search_value:
                return key
        return None

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
            pkm["moves"] = []

            for move in result["moves"]:
                for detail in move["version_group_details"]:
                    if detail["version_group"]["name"] == "firered-leafgreen" and detail["move_learn_method"]["name"] == "level-up" and get_key_with_value(moves, move["move"]["name"]) is not None:
                        pkm["moves"].append((
                            { "id": get_key_with_value(moves, move["move"]["name"]) },
                            { "level": detail["level_learned_at"] },
                            { "method": detail["move_learn_method"]["name"] }
                        ))
                        break
            
            pkdex[i] = pkm
            
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(pkdex, "./pkm_data/pkdex.json")

while True:
    print("Script para obtener datos de la POKE API")
    print("Qué datos quieres guardar?")
    print("1. Movimientos")
    print("2. Pokédex 1-151 pokémon")
    print("3. Evoluciones")
    print("4. Exit")

    option = input("Selecciona una opción: ")
    if option != "1" and option != "2" and option != "3" and option != "4":
        print("Opción no válida")
        exit()

    option = int(option)

    if option == 1:
        save_moves()
    elif option == 2:
        save_pokedex()
    elif option == 4:
        exit()