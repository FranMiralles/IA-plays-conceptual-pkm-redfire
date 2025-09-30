from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
import random
from battle_simulator import *

def generate_individual():
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

    # Generate 14 teams from catches
    teams = []
    for i in range(0, 14):
        available =  [pkmID for pkmID in catches[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]] if pkmID is not None]
        teams.append(random.sample(available, min(6, len(available))))

    return [
        catches,
        teams
    ]

INDIVIDUAL_EXAMPLE = generate_individual()