from time import time
from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
import random
from battle_simulator import *

type_preferences = {
    1: ["water", "grass", "fighting"], # GYM PLATEADA
    3: ["electric", "grass", "bug"], # GYM CELESTE
    5: ["ground", "rock"], # GYM CARMIN
    7: ["psychic", "poison", "fire", "flying"], # GYM AZULONA
    11: ["psychic"], # GYM FUCSIA
    12: ["bug", "ghost"], # GYM AZAFRAN
    13: ["water", "ground", "rock"], # GYM CANELA
    14: ["water", "grass", "ground"], # GYM VERDE
}

type_not_preferences = {
    1: ["fire", "bug", "flying"], # GYM PLATEADA
    3: ["rock", "fire", "ground"], # GYM CELESTE
    5: ["flying", "water"], # GYM CARMIN
    7: ["water", "ground", "rock"], # GYM AZULONA
    11: ["grass"], # GYM FUCSIA
    12: ["poison"], # GYM AZAFRAN
    13: ["grass", "bug"], # GYM CANELA
    14: ["fire"], # GYM VERDE
}

def generate_individual(inteligent_generation=False):
    '''
    Generates a random individual that uses pkms catched on the run
    '''

    used = set()        # Not to repeat pkm
    catches = []        # Catches in routes

    for route in ROUTES_ORDER:
        options = ROUTES.get(route, [])
        # Filter available pkm to catch in each route
        available = [pkm for pkm in options if pkm not in used]
        if available:
            chosen = random.choice(available)  # Choose randomly
            used.add(chosen)
        else:
            chosen = None

        catches.append(chosen)

    # Generate 17 teams from catches
    teams = []
    if inteligent_generation:
        for i in range(0, 17):
            available =  [pkmID for pkmID in catches[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]] if pkmID is not None]
            available_weighted = []
            for available_pkmID in available:
                weight = 1
                types = dataset["pkdex"][str(available_pkmID)]["types"]
                for typing in types:
                    if typing in type_preferences.get(i, []):
                        weight *= 2
                    if typing in type_not_preferences.get(i, []):
                        weight /= 2
                available_weighted.append((available_pkmID, weight))
            if available_weighted:
                pkm_ids, weights = zip(*available_weighted)
                selected_team = set()
                while len(selected_team) < min(6, len(available)):
                    chosen = random.choices(pkm_ids, weights=weights, k=1)[0]
                    selected_team.add(chosen)
                teams.append(list(map(int, selected_team)))
            else:
                teams.append([])
    else:
        for i in range(0, 17):
            available =  [pkmID for pkmID in catches[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]] if pkmID is not None]
            teams.append(random.sample(available, min(6, len(available))))
    # Last 4 teams are permutations of the last team
    teams.append(random.sample(teams[16], min(6, len(available))))
    teams.append(random.sample(teams[16], min(6, len(available))))
    teams.append(random.sample(teams[16], min(6, len(available))))
    teams.append(random.sample(teams[16], min(6, len(available))))
    return [
        catches,
        teams
    ]