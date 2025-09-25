AVAILABLE_EVOLVE_OBJ_TRAINERS = {
    "GYM_PLATEADA" : [],
    "GYM_CELESTE": ["moon-stone"],
    "GYM_CARMIN": [],
    "GYM_AZULONA": ["thunder-stone", "fire-stone", "water-stone", "leaf-stone"],
    "GIOVANNI_AZULONA": [],
    "GIOVANNI_AZAFRAN": [],
    "GYM_FUCSIA": [],
    "GYM_AZAFRAN": [],
    "GYM_CANELA": [],
    "GYM_VERDE": [],
    "ALTO_MANDO_LORELEI": [],
    "ALTO_MANDO_BRUNO": [],
    "ALTO_MANDO_AGATHA": [],
    "ALTO_MANDO_LANCE": []
}

accumulated = {}
prev_moves = []

for gym, moves in AVAILABLE_EVOLVE_OBJ_TRAINERS.items():
    prev_moves += moves
    accumulated[gym] = prev_moves.copy()

AVAILABLE_EVOLVE_OBJ_TRAINERS = accumulated