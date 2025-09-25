AVAILABLE_MT_TRAINERS = {
    "GYM_PLATEADA" : [],
    "GYM_CELESTE": ["rock-tomb", "bullet-seed", "thief", "secret-power"],
    "GYM_CARMIN": ["water-pulse", "dig", "brick-break", "cut"],
    "GYM_AZULONA": ["shock-wave", "aerial-ace", "hyper-beam", "ice-beam", "iron-tail", "thunderbolt", "shadow-ball", "flamethrower", "fly"],
    "GIOVANNI_AZULONA": ["giga-drain", "snatch"],
    "GIOVANNI_AZAFRAN": ["steel-wing", "psychic", "surf", "strength"],
    "GYM_FUCSIA": [],
    "GYM_AZAFRAN": [],
    "GYM_CANELA": ["blizzard", "solar-beam"],
    "GYM_VERDE": ["fire-blast"],
    "ALTO_MANDO_LORELEI": ["earthquake", "dragon-claw", "overheat"],
    "ALTO_MANDO_BRUNO": [],
    "ALTO_MANDO_AGATHA": [],
    "ALTO_MANDO_LANCE": []
}

accumulated = {}
prev_moves = []

for gym, moves in AVAILABLE_MT_TRAINERS.items():
    prev_moves += moves
    accumulated[gym] = prev_moves.copy()

AVAILABLE_MT_TRAINERS = accumulated