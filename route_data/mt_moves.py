AVAILABLE_MT_TRAINERS = {
    "RIVAL_RUTA_22": [], # 1
    "GYM_PLATEADA" : [],
    "RIVAL_CELESTE": [],
    "GYM_CELESTE": ["rock-tomb", "bullet-seed", "thief", "secret-power"],
    "RIVAL_CARMIN": [],
    "GYM_CARMIN": ["water-pulse", "dig", "brick-break", "cut"],
    "RIVAL_TORRE_PKM": [],
    "GYM_AZULONA": ["shock-wave", "aerial-ace", "hyper-beam", "ice-beam", "iron-tail", "thunderbolt", "shadow-ball", "flamethrower", "fly"],
    "GIOVANNI_AZULONA": ["giga-drain", "snatch"],
    "RIVAL_AZAFRAN": [],
    "GIOVANNI_AZAFRAN": ["steel-wing", "psychic", "surf", "strength"],
    "GYM_FUCSIA": [],
    "GYM_AZAFRAN": [],
    "GYM_CANELA": ["blizzard", "solar-beam"],
    "GYM_VERDE": ["fire-blast"],
    "RIVAL_VERDE": [],
    "ALTO_MANDO_LORELEI": ["earthquake", "dragon-claw", "overheat"],
    "ALTO_MANDO_BRUNO": [],
    "ALTO_MANDO_AGATHA": [],
    "ALTO_MANDO_LANCE": [],
    "RIVAL_CAMPEON": []
}

accumulated = {}
prev_moves = []

for gym, moves in AVAILABLE_MT_TRAINERS.items():
    prev_moves += moves
    accumulated[gym] = prev_moves.copy()

AVAILABLE_MT_TRAINERS = accumulated