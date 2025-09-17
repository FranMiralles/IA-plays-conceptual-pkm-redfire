# Dictionary of pokemon per route
ROUTES = {
    "PUEBLO PALETA": ["Bulbasaur", "Squirtle", "Charmander"],
    "RUTA 1": ["Pidgey", "Rattata"],
    "RUTA 22": ["Rattata", "Mankey", "Spearow"],
    "RUTA 2": ["Pidgey", "Rattata", "Caterpie", "Weedle"],
    "BOSQUE VERDE": ["Caterpie", "Weedle", "Pikachu"],
    # COMBATE CON EL RIVAL RUTA 22
    # COMBATE CON LÍDER PLATEADA
    "RUTA 3": ["Pidgey", "Spearow", "Nidoran-m", "Nidoran-f", "Jigglypuff", "Mankey"],
    "RUTA 4": ["Rattata", "Spearow", "Ekans", "Sandshrew", "Mankey"],
    "MONTE MOON": ["Clefairy", "Paras", "Geodude", "Zubat"],
    # COMBATE CON EL RIVAL CELESTE
    "RUTA 24": ["Caterpie", "Weedle", "Pidgey", "Oddish", "Abra", "Bellsprout"],
    "RUTA 25": ["Caterpie", "Weedle", "Pidgey", "Oddish", "Abra", "Bellsprout"],
    # COMBATE CON LÍDER CELESTE
    "RUTA 5": ["Pidgey", "Oddish", "Bellsprout", "Meowth"],
    "RUTA 6": ["Pidgey", "Oddish", "Bellsprout", "Meowth"],
    "RUTA 11": ["Ekans", "Sandshrew", "Spearow", "Drowzee", "Magikarp"],
    "CUEVA DIGLETT": ["Diglett"],
    # COMBATE CON EL RIVAL CARMÍN
    # COMBATE CON LÍDER CARMÍN
    "RUTA 9": ["Spearow", "Ekans", "Rattata", "Sandshrew"],
    "RUTA 10": ["Voltorb", "Spearow", "Ekans", "Sandshrew", "Mankey"],
    "TUNEL ROCA": ["Machop", "Onix", "Geodude", "Zubat", "Mankey"],
    "RUTA 8": ["Pidgey", "Meowth", "Ekans", "Sandshrew", "Growlithe", "Vulpix"],
    "RUTA 7": ["Pidgey", "Meowth", "Oddish", "Bellsprout", "Growlithe", "Vulpix"],
    "RUTA 16": ["Spearow", "Doduo", "Rattata", "Raticate"],
    # COMBATE CON EL RIVAL LAVANDA
    "TORRE POKEMON": ["Gastly", "Cubone"],
    # COMBATE CON LÍDER AZULONA
    # COMBATE CON GIOVANNI AZULONA
}

import random

def generar_combinaciones(routes, x):
    resultados = []  # Guardará las x combinaciones
    usados = set()   # Pokémon ya seleccionados
    todos = {poke for lista in routes.values() for poke in lista}  # Conjunto con todos los Pokémon posibles

    for _ in range(x):
        eleccion = {}
        for ruta, pokes in routes.items():
            # Filtramos los Pokémon que aún no se han usado
            disponibles = [p for p in pokes if p not in usados]
            if disponibles:
                elegido = random.choice(disponibles)
                eleccion[ruta] = elegido
                usados.add(elegido)
            else:
                eleccion[ruta] = None  # No queda opción válida en esta ruta
        resultados.append(eleccion)

    # Pokémon que nunca fueron elegidos
    no_elegidos = list(todos - usados)

    return resultados, sorted(no_elegidos)


res, no_usados = generar_combinaciones(ROUTES, 3)

for i, comb in enumerate(res, 1):
    print(f"\nCombinación {i}:")
    for ruta, elegido in comb.items():
        print(f"  {ruta}: {elegido}")
        
print("\nPokémon que nunca fueron elegidos:", no_usados)