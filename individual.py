from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
import random
from battle_simulator import *

def generate_individual(routes, order):
    '''
    Generates a random individual that uses pkms catched on the run
    '''

    used = set()        # Not to repeat pkm
    catches = []        # Catches in routes

    for route in order:
        options = routes.get(route, [])
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

INDIVIDUAL_EXAMPLE = generate_individual(ROUTES, ROUTES_ORDER)
print(INDIVIDUAL_EXAMPLE)



for i in range(0, 1000):
    start = time.perf_counter()
    print(i)
    calculate_fitness(
        individual=generate_individual(ROUTES, ROUTES_ORDER),
        dataset=dataset,
        verbose=False
    )

    end = time.perf_counter()
    elapsed_seconds = end - start
    print("TIME OF GENERATE 1000 individuals and calculate its fitness")
    print(elapsed_seconds)