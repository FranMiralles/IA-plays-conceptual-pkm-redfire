# Dictionary of pokemon per route
ROUTES = {
    "PUEBLO PALETA": [1, 7, 4],
    "RUTA 1": [16, 19],
    "RUTA 22": [19, 56, 21],
    "RUTA 2": [16, 19, 10, 13],
    "BOSQUE VERDE": [10, 13, 25],
    # COMBATE CON EL RIVAL RUTA 22
    # COMBATE CON LÍDER PLATEADA
    "RUTA 3": [16, 21, 32, 29, 39, 56],
    "RUTA 4": [19, 21, 23, 27, 56],
    "MONTE MOON": [35, 46, 74, 41],
    # COMBATE CON EL RIVAL CELESTE
    "RUTA 24": [10, 13, 16, 43, 63, 69],
    "RUTA 25": [10, 13, 16, 43, 63, 69],
    # COMBATE CON LÍDER CELESTE
    "RUTA 5": [16, 43, 69, 52],
    "RUTA 6": [16, 43, 69, 52],
    "RUTA 11": [23, 27, 21, 96, 129],
    "CUEVA DIGLETT": [50],
    # COMBATE CON EL RIVAL CARMÍN
    # COMBATE CON LÍDER CARMÍN
    "RUTA 9": [21, 23, 19, 27],
    "RUTA 10": [100, 21, 23, 27, 56],
    "TUNEL ROCA": [66, 95, 74, 41, 56],
    "RUTA 8": [16, 52, 23, 27, 58, 37],
    "RUTA 7": [16, 52, 43, 69, 58, 37],
    "RUTA 16": [21, 84, 19, 19],
    # COMBATE CON EL RIVAL LAVANDA
    "TORRE POKEMON": [92, 104],
    # COMBATE CON LÍDER AZULONA
    # COMBATE CON GIOVANNI AZULONA
    "RUTA 12": [16, 43, 48, 69, 129, 54, 98, 79, 116],
    "RUTA 13": [16, 43, 48, 69, 129, 54, 98, 79, 116],
    "RUTA 14": [16, 43, 48, 69],
    "RUTA 15": [16, 43, 48, 69],
    "ZONA SAFARI": [32, 29, 102, 111, 48, 46, 123, 127, 113, 129, 118, 60, 147, 54, 79, 84, 115, 128],
    "RUTA 18": [19, 21, 84],
    "RUTA 17": [19, 21, 84],
    # COMBATE CON GIOVANNI AZAFRAN
    # COMBATE CON LÍDER FUCSIA
    # COMBATE CON LÍDER AZAFRAN
    "RUTA 19": [72, 129, 98, 116, 54, 79],
    "RUTA 20": [72, 129, 98, 116, 54, 79],
    "RUTA 21": [72, 129, 98, 116, 54, 79, 114],
    "ISLAS ESPUMA": [54, 79, 41, 86, 98, 129, 116],
    "MANSION PKM": [19, 109, 88, 58, 37],
    "CENTRAL ENERGIA": [81, 100, 25, 125],
    # COMBATE CON LÍDER CANDELA
    # COMBATE CON LÍDER VERDE
    "RUTA 23": [21, 23, 27, 56, 54, 79, 129, 60, 118],
    "CALLE VICTORIA": [95, 66, 74, 41, 23, 27, 104, 56]
}

ROUTES_ORDER = [
    "PUEBLO PALETA",
    "RUTA 1",
    "RUTA 22",
    "RUTA 2",
    "BOSQUE VERDE",
    "RUTA 3",
    "RUTA 4",
    "MONTE MOON",
    "RUTA 24",
    "RUTA 25",
    "RUTA 5",
    "RUTA 6",
    "RUTA 11",
    "CUEVA DIGLETT",
    "RUTA 9",
    "RUTA 10",
    "TUNEL ROCA",
    "RUTA 8",
    "RUTA 7",
    "RUTA 16",
    "TORRE POKEMON",
    "RUTA 12",
    "RUTA 13",
    "RUTA 14",
    "RUTA 15",
    "ZONA SAFARI",
    "RUTA 18",
    "RUTA 17",
    "RUTA 19",
    "RUTA 20",
    "RUTA 21",
    "ISLAS ESPUMA",
    "MANSION PKM",
    "CENTRAL ENERGIA",
    "RUTA 23",
    "CALLE VICTORIA"
]

print(list(ROUTES.keys()))
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


res, no_usados = generar_combinaciones(ROUTES, 1)

for i, comb in enumerate(res, 1):
    print(f"\nCombinación {i}:")
    for ruta, elegido in comb.items():
        print(f"  {ruta}: {elegido}")
        
print("\nPokémon que nunca fueron elegidos:", no_usados)