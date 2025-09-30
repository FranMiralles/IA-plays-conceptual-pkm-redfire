import random
from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
from individual import *


def mutate_individual_hard_feasibility(individual: list, prob_mutate_catches=0.2, prob_mutate_team=0.2, seed=None):
    '''
    Obtain a feasible individual (pkm used had been catched)

    individual=[
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
        [
            [1, 2, 3, 1, 2],
            [1, 2, 3, 2, 2, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 3, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 29],
        ]
    ]
    PREVIOUS_ROUTES_TO_TRAINER = {
        "GYM_PLATEADA": 5,
        "GYM_CELESTE": 10,
        "GYM_CARMIN": 14,
        "GYM_AZULONA": 21,
        "GIOVANNI_AZULONA": 21,
        "GIOVANNI_AZAFRAN": 28,
        "GYM_FUCSIA": 28,
        "GYM_AZAFRAN": 28,
        "GYM_CANELA": 34,
        "GYM_VERDE": 34,
        "ALTO_MANDO_LORELEI": 36,
        "ALTO_MANDO_BRUNO": 36,
        "ALTO_MANDO_AGATHA": 36,
        "ALTO_MANDO_LANCE": 36
    }
    '''
    # Mutate catches
    if seed is not None:
        random.seed(seed)
    
    catches = individual[0]
    for i in range(0, len(catches)): # i has the id of the route (0 to 35)
        if random.random() < prob_mutate_catches:
            # Mutate from possible pkm in route that has not been catched yet
            catched_yet = catches[:i]
            previous_value = catches[i]
            available = [x for x in ROUTES[ROUTES_ORDER[i]] if x != catches[i] and x not in catched_yet]
            if len(available) == 0:
                catches[i] = None
            else:
                chosen = random.choice(available)
                catches[i] = chosen
            
            # Due to have changed the catches, is necessary to cure the teams posterior from i
            
            teams_envolved = [trainer for trainer, quantityPkm in PREVIOUS_ROUTES_TO_TRAINER.items() if quantityPkm > i]
           
            teams = individual[1]
            for t in range(len(teams) - len(teams_envolved), len(teams)):
                teams[t] = [catches[i] if x == previous_value else x for x in teams[t]]
                teams[t] = [x for x in teams[t] if x is not None]
            
            # Después de una pasada lo que se puede hacer es ajustar si la len de los equipos no es 6 añadir de los availables
            
            for t in range(len(individual[1])):
                individual[1][t] = [catches[i] if pkmID == previous_value else pkmID 
                                for pkmID in individual[1][t]]
                
                individual[1][t] = [pkmID for pkmID in individual[1][t] if pkmID is not None]
    print("NEW CATCHES")
    print(catches)
    print("NEW TEAMS")
    print(individual[1])

    

    # Mutate pkm teams, wich are used and its order
    teams = individual[1]

    '''
    for i in range(0, len(teams)):
        for j in range(0, len(teams[i])):
            if random.random() < prob_mutate_team:
                # Mutate
                current_team = teams[i][0:j] + teams[i][j+1:]
                print("CURRENT_TEAM")
                print(current_team)
                available = [catch for catch in catches[0:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]] if catch not in current_team]
                print("AVAILABLES")
                print(available)
                chosen = random.choice(available)
                teams[i][j] = chosen
        if random.random() < prob_mutate_team:
            # Randomizar el orden del equipo
            teams[i] = random.shuffle(teams[i])
    '''

    return [
        catches,
        teams
    ]

individual = generate_individual()
print("INDIVIDUAL")
print(individual)
individual_mutated = mutate_individual_hard_feasibility(individual, 1, 1)
print("INDIVIDUAL MUTATED")
print(individual_mutated)

def mutate_individual_permisive_feasibility(individual: list):
    pass



def repair_individual(individual: list):
    pass