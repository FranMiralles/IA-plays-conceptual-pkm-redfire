import base64
import requests
import json
import os
import time
from PIL import Image, ImageSequence

def guardar_json(datos, nombre_archivo):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Datos guardados correctamente en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

def save_moves():
    moves = {}
    banned_moves = ["dream-eater", "horn-drill", "guillotine", "fissure", "skull-bash"]
    for i in range(1, 400):
        print(f"Obteniendo datos del movimiento {i}...")
        res = requests.get(f"https://pokeapi.co/api/v2/move/{i}")
        if res.status_code == 200:
            result = res.json()
            # Si hay alguna descripción del firered-leafgreen, guardo el movimiento, sino no
            # Si el movimiento es de estado, no lo guardo
            if(result["damage_class"]["name"] == "physical" or result["damage_class"]["name"] == "special") and result["name"] not in banned_moves:
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
            pkm["sprite"] = {}
            pkm["sprite"]["front"] = f"./pkm_data/normalized_sprites/{i}_front.gif"
            pkm["sprite"]["back"] = f"./pkm_data/normalized_sprites/{i}_back.gif"
            pkm["speed"] = result["stats"][5]["base_stat"]
            pkm["moves"] = {}

            for move in result["moves"]:
                for detail in move["version_group_details"]:
                    if detail["version_group"]["name"] == "firered-leafgreen" and (detail["move_learn_method"]["name"] == "level-up" or detail["move_learn_method"]["name"] == "machine") and move["move"]["name"] in moves:

                        # Correct new names to previous versions
                        move_name = move["move"]["name"]
                        if move_name == "vice-grip":
                            move_name = "vise-grip"

                        pkm["moves"][move_name] = {
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
                            if evolved_id <= 151:
                                evolution_dict[current_id] = [evolved_id, trigger_name, third_value]
                        
                        # Procesar recursivamente las siguientes evoluciones
                        process_chain(evolution, evolved_id)
                
                # Obtener el ID del Pokémon inicial
                initial_species_url = evolution_data['chain']['species']['url']
                initial_id = int(initial_species_url.split('/')[-2])
                
                # Iniciar el procesamiento
                process_chain(evolution_data['chain'], initial_id)
                # Caso concreto de gloom
                evolution_dict[44] = [
                    45,
                    "use-item",
                    "leaf-stone"
                ]
                # Caso concreto de vulpix
                evolution_dict[37] = [
                    38,
                    "use-item",
                    "fire-stone"
                ]
                # Caso concreto de vulpix
                evolution_dict[79] = [
                    80,
                    "level-up",
                    39
                ]
                # Caso concreto de sandshrew
                evolution_dict[27] = [
                    28,
                    "level-up",
                    22
                ]
                return evolution_dict

            if res_chain.status_code == 200:
                chain_data = res_chain.json()
                evolution_chain = get_evolution_chain_data(chain_data)
                
                for pokemon_id, evolution_data in evolution_chain.items():
                    evolutions[pokemon_id] = evolution_data
                    
        else:
            print("Error:", res.status_code, res.text)

    guardar_json(evolutions, "./pkm_data/evolutions.json")

def save_sprites():
    # --- Cargar la pokédex ---
    pkdex_path = "./pkm_data/pkdex.json"
    if not os.path.exists(pkdex_path):
        print("No existe el archivo de Pokédex. Ejecuta primero save_pokedex().")
        return

    with open(pkdex_path, "r", encoding="utf-8") as f:
        pkdex = json.load(f)

    # --- Carpeta sprites ---
    os.makedirs("./pkm_data/sprites", exist_ok=True)

    for i, pkm in pkdex.items():
        for orientation in ("front", "back"):
            sprite_path = pkm["sprite"][orientation]

            # Si ya existe el archivo y no está vacío → lo saltamos
            if os.path.exists(sprite_path) and os.path.getsize(sprite_path) > 0:
                continue

            # Buscar la URL desde la API (porque en el JSON solo está la ruta local)
            try:
                res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}", timeout=10)
                res.raise_for_status()
                result = res.json()
            except Exception as e:
                print(f"[{i}] Error al obtener datos del Pokémon para sprites: {e}")
                continue

            url = result["sprites"]["versions"]["generation-v"]["black-white"]["animated"].get(f"{orientation}_default")

            if not url:
                print(f"[{i}] No hay sprite {orientation}")
                continue

            try:
                print(f"[{i}] Descargando sprite {orientation}...")
                data = requests.get(url, timeout=10).content
                with open(sprite_path, "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"[{i}] Error al descargar sprite {orientation}: {e}")
                continue

            # Pequeña pausa para no saturar la API
            time.sleep(0.2)

    

def normalize_sprites():
    input_folder = "./pkm_data/sprites"
    output_folder = "./pkm_data/normalized_sprites"
    os.makedirs(output_folder, exist_ok=True)

    # Max dimensions
    max_width, max_height = 0, 0
    for file in os.listdir(input_folder):
        if file.lower().endswith(".gif"):
            with Image.open(os.path.join(input_folder, file)) as img:
                w, h = img.size
                if w > max_width:
                    max_width = w
                if h > max_height:
                    max_height = h

    print(f"Tamaño máximo encontrado: {max_width}x{max_height}")

    # Processing and redimension
    for file in os.listdir(input_folder):
        if file.lower().endswith(".gif") and not file.lower().endswith("pokeball_loading.gif"):
            path = os.path.join(input_folder, file)
            with Image.open(path) as img:
                frames = []
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert("RGBA")  # Asegurar compatibilidad

                    # Crear lienzo vacío con el tamaño máximo
                    new_frame = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))

                    # Calcular posición
                    x_offset = (max_width - frame.width) // 2
                    y_offset = max_height - frame.height

                    # Pegar el frame en la posición calculada
                    new_frame.paste(frame, (x_offset, y_offset), frame)

                    frames.append(new_frame)

                # Guardar nuevo gif
                output_path = os.path.join(output_folder, file)
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=img.info.get("duration", 100),
                    loop=img.info.get("loop", 0),
                    disposal=2,
                    transparency=0,
                )
                print(f"Procesado: {file}")

while True:
    print("Script para obtener datos de la POKE API")
    print("Qué datos quieres guardar?")
    print("1. Pokédex 1-151 pokémon")
    print("2. Sprites animados")
    print("3. Normalizar sprites")
    print("4. Movimientos")
    print("5. Evoluciones")
    print("6. Exit")

    option = input("Selecciona una opción: ")
    if option != "1" and option != "2" and option != "3" and option != "4" and option != "5" and option != "6":
        print("Opción no válida")
        exit()

    option = int(option)

    if option == 1:
        save_pokedex()
    elif option == 2:
        save_sprites()
    elif option == 3:
        normalize_sprites()
    elif option == 4:
        save_moves()
    elif option == 5:
        save_evolutions()
    elif option == 6:
        print("Saliendo del menú")
        exit()