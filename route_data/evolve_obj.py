AVAILABLE_EVOLVE_OBJ_TRAINERS = {
    "RIVAL_RUTA_22": [],
    "GYM_PLATEADA" : [],
    "RIVAL_CELESTE": [],
    "GYM_CELESTE": ["moon-stone"],
    "RIVAL_CARMIN": [],
    "GYM_CARMIN": [],
    "RIVAL_TORRE_PKM": [],
    "GYM_AZULONA": ["thunder-stone", "fire-stone", "water-stone", "leaf-stone"],
    "GIOVANNI_AZULONA": [],
    "RIVAL_AZAFRAN": [],
    "GIOVANNI_AZAFRAN": [],
    "GYM_FUCSIA": [],
    "GYM_AZAFRAN": [],
    "GYM_CANELA": [],
    "GYM_VERDE": [],
    "RIVAL_VERDE": [],
    "ALTO_MANDO_LORELEI": [],
    "ALTO_MANDO_BRUNO": [],
    "ALTO_MANDO_AGATHA": [],
    "ALTO_MANDO_LANCE": [],
    "RIVAL_CAMPEON": []

    
}

accumulated = {}
prev_moves = []

for gym, moves in AVAILABLE_EVOLVE_OBJ_TRAINERS.items():
    prev_moves += moves
    accumulated[gym] = prev_moves.copy()

AVAILABLE_EVOLVE_OBJ_TRAINERS = accumulated