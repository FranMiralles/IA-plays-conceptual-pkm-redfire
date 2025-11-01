from decimal import Decimal, ROUND_DOWN
from entry_data import *
from genetic_operators import *
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os
from itertools import permutations
import math

def simulated_annealing(
        initial_individual,
        T_init=100,
        T_min=1,
        max_iter=200
        ):
    
    neighbors_yet_visited = []

    # Estado inicial
    current = initial_individual
    current_fitness = calculate_fitness(current, dataset, verbose=False)[1]
    best = current
    best_fitness = current_fitness

    # Parámetros de control
    iteration = 0
    mode = "exploration"    # empieza explorando
    no_improve_count = 0    # contador de iteraciones sin mejora

    print("=== INICIO ENFRIAMIENTO SIMULADO ===")

    while iteration < max_iter:
        neighbors_yet_visited.append(current)
        # Temperatura base (descenso lineal)
        T_base = T_init - (iteration / max_iter) * (T_init - T_min)

        

        # Ajuste dinámico según modo
        if mode == "exploration":
            T = T_base * 2  # exploración -> temperatura más alta
        else:
            T = T_base * 0.9  # explotación -> temperatura más baja

        # --- Generación de vecinos (siempre las tres listas) ---
        neighbors = (
            generate_neighbors_team_entry_pkm(current, neighbors_yet_visited)
            + generate_neighbors_team_permutation(current, neighbors_yet_visited)
            #generate_neighbors_capture_change(current, neighbors_yet_visited)
        )
        random.shuffle(neighbors)

        # Evaluar fitness de los vecinos
        neighbors_fitness = [calculate_fitness(n, dataset, verbose=False)[1] for n in neighbors]
        #print(np.(neighbors_fitness))
        print(len(neighbors_fitness))
        print(len([fitness for fitness in neighbors_fitness if fitness == 1864]))

        # Seleccionar el mejor vecino (minimización)
        selected, selected_fit = min(
            zip(neighbors, neighbors_fitness), key=lambda x: x[1]
        )

        # Calcular diferencia de fitness a minimizar
        delta = selected_fit - current_fitness

        # Aceptar movimiento
        if delta < 0:  # mejora
            current, current_fitness = selected, selected_fit

            # actualizar mejor global
            if current_fitness < best_fitness:
                best, best_fitness = current, current_fitness

            no_improve_count = 0  # reiniciar contador

            # si estamos explorando y mejora → pasa a explotación (baja T)
            if mode == "exploration":
                mode = "exploitation"
                print(f"[Iter {iteration}] Mejora detectada -> Cambio a EXPLOTACIÓN")

        else:
            for neighbor, neighbor_fit in zip(neighbors, neighbors_fitness):
                print("NEIG FIT", neighbor_fit)
                if neighbor_fit == current_fitness:
                    # No hay mejora, hay movimiento lateral con 1 / len de probabilidad
                    # Factor de temperatura (mayor T = más exploración)
                    temp_factor = T / T_init

                    # Factor de diversidad Normalizado 0-1
                    diversity_factor = math.log1p(len(neighbors)) / math.log1p(50)

                    # Probabilidad lateral reducida ~60% menos
                    lateral_prob = 0.05 + 0.08 * temp_factor + 0.04 * diversity_factor
                    print("LATERAL PROB", lateral_prob)
                    if random.random() < lateral_prob:
                        print("COGIDO")
                        current, current_fitness = neighbor, neighbor_fit
                        break
                else:
                    # Aceptación probabilística
                    delta = neighbor_fit - current_fitness
                    prob = min(1, math.exp(-delta / T))
                    print("DELTA:", delta)
                    print("DELTA/T:", str(-delta / T))
                    print("EXP:", math.exp(-delta / T))
                    print("PROBABILIDAD:", prob)
                    if random.random() < prob:
                        print("RECOGEMOS CABLE")
                        current, current_fitness = neighbor, neighbor_fit
                        break

            # Si no hay mejora
            no_improve_count += 1

            # Si llevamos 10 iteraciones sin mejora en explotación → pasar a exploración (subir T)
            if mode == "exploitation" and no_improve_count >= 10:
                mode = "exploration"
                no_improve_count = 0
                print(f"[Iter {iteration}] Sin mejora -> Cambio a EXPLORACIÓN")

        iteration += 1


        print(f"Iter {iteration:4d} | T={T:7.3f} | Delta={delta:.8f} | f_global_best={best_fitness:.4f} | f_local={current_fitness:.4f} | modo={mode} | individuo{current}")

    print("=== FIN ENFRIAMIENTO SIMULADO ===")
    print(f"Mejor fitness encontrado: {best_fitness:.4f}")
    return best, best_fitness

def generate_neighbors_capture_change(individual, neighbors_yet_visited):
    catches = individual[0]
    neighbors = []
    for route in range(len(catches)):
        previous_value = catches[route]
        catched_yet = catches[:route] + catches[route+1:]
        available = [x for x in ROUTES[ROUTES_ORDER[route]] if x != catches[route] and x not in catched_yet]
        for capture_available in available:
            new_catches = catches[:route] + [capture_available] + catches[route+1:]
            new_value = capture_available
            # Fix the teams
            new_teams = copy.deepcopy(individual[1])
            for teamPos in range(len(new_teams)):
                for pkmIDPos in range(len(new_teams[teamPos])):
                    if new_teams[teamPos][pkmIDPos] == previous_value:
                        new_teams[teamPos][pkmIDPos] = new_value
            if [new_catches, new_teams] not in neighbors_yet_visited:
                neighbors.append([new_catches, new_teams])
    return neighbors

def generate_neighbors_team_permutation(individual, neighbors_yet_visited):
    teams = individual[1]
    neighbors = []
    for teamPos in range(len(teams)):
        team = teams[teamPos]
        permutation_list = list(permutations(team))
        for permutation in permutation_list:
            list(permutation)
            # New neighbor
            new_catches = copy.deepcopy(individual[0])
            new_teams = copy.deepcopy(individual[1])
            new_teams[teamPos] = list(permutation)
            if [new_catches, new_teams] not in neighbors_yet_visited:
                neighbors.append([new_catches, new_teams])
    return neighbors

def generate_neighbors_team_entry_pkm(individual, neighbors_yet_visited):
    catches = individual[0]
    teams = individual[1]
    neighbors = []
    # Los últimos 4 son casos especiales
    for i in range(0, 17):
        available = [pkmID for pkmID in catches[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]] if pkmID is not None and pkmID not in teams[i]]
        for pkmIDPos in range(len(teams[i])-5):
            # Coger uno de los availables y crear un vecino
            for available_pkm in available:
                new_catches = copy.deepcopy(individual[0])
                new_teams = copy.deepcopy(individual[1])
                previous_pkm = new_teams[i][pkmIDPos]
                new_teams[i][pkmIDPos] = available_pkm
                # Cambiar los pkm de los equipos de la liga
                if i == 16:
                    for j in range(17, 21):
                        for pkmIDPos_ligue in range(len(teams[i])):
                            if new_teams[j][pkmIDPos_ligue] == previous_pkm:
                                new_teams[j][pkmIDPos_ligue] = available_pkm
                if [new_catches, new_teams] not in neighbors_yet_visited:
                    neighbors.append([new_catches, new_teams])
    return neighbors

'''
for i in range(100):
    if not is_feasible(generate_neighbors_capture_change(individual=generate_individual())):
        print("TE EQUIVOCASTE")
'''



# Individuo a iteración 235 de genetic_1000_1
individual = [[7, 16, 19, 10, 13, 21, 23, 35, 43, 63, 52, 69, 129, 50, 27, 56, 41, 37, 58, 84, 92, 48, 79, 43, 43, 128, 19, 19, 72, 116, 54, 86, 88, 125, 118, 74], [[7, 16, 19, 13, 10], [7, 10, 13, 16, 19], [7, 16, 13, 19, 21, 23], [43, 7, 16, 19, 13, 35], [16, 129, 10, 50, 52, 21], [35, 52, 7, 13, 21, 63], [129, 63, 41, 50, 19, 10], [37, 10, 56, 58, 63, 35], [13, 56, 58, 50, 37, 52], [37, 52, 84, 92, 129, 58], [92, 129, 50, 16, 19, 56], [129, 37, 50, 56, 27, 63], [129, 37, 84, 10, 48, 56], [72, 58, 7, 84, 86, 129], [7, 54, 16, 50, 116, 41], [79, 52, 86, 88, 58, 63], [72, 84, 52, 116, 27, 63], [63, 27, 84, 52, 72, 116], [63, 116, 27, 52, 72, 84], [27, 63, 84, 116, 72, 52], [72, 63, 52, 84, 27, 116]]]

# Individuo a primera iteración de genetic_1000_1
individual = [[7, 16, 21, 19, 13, 29, 23, 74, 10, 43, 52, 69, 96, 50, 27, 56, 95, 37, 58, 84, 104, 48, 129, None, None, 54, None, None, 72, 116, 79, 86, 109, 81, 60, 66], [[21, 19, 13, 16, 7], [16, 7, 21, 13, 19], [19, 21, 7, 13, 29, 74], [13, 29, 10, 43, 19, 23], [29, 52, 10, 96, 7, 69], [29, 19, 74, 96, 7, 52], [95, 74, 16, 52, 21, 29], [58, 19, 74, 69, 27, 104], [21, 10, 52, 13, 50, 84], [19, 48, 52, 16, 7, 54], [27, 54, 37, 16, 69, 56], [27, 7, 21, 50, 69, 95], [58, 27, 104, 50, 69, 52], [7, 50, 79, 19, 81, 69], [58, 104, 54, 48, 16, 109], [54, 19, 109, 13, 116, 74], [7, 86, 13, 52, 21, 116], [52, 21, 7, 116, 86, 13], [116, 7, 86, 13, 21, 52], [86, 13, 7, 52, 116, 21], [52, 116, 21, 86, 7, 13]]]

# Individuo a iteración 300
individual = [[7, 16, 19, 10, 13, 21, 23, 35, 43, 63, 69, 52, 129, 50, 27, 56, 41, 37, 58, 84, 92, 48, 54, 69, 16, 147, 19, 21, 72, 116, 79, 86, 109, 25, 60, 104], [[7, 16, 19, 13, 10], [7, 10, 13, 16, 19], [7, 10, 23, 16, 21, 35], [43, 10, 16, 21, 23, 35], [129, 43, 16, 50, 19, 35], [69, 43, 16, 50, 19, 63], [129, 10, 37, 43, 19, 84], [37, 10, 56, 58, 63, 35], [37, 41, 10, 19, 84, 21], [35, 50, 16, 84, 69, 58], [92, 129, 50, 16, 19, 56], [129, 37, 50, 56, 27, 63], [129, 37, 84, 10, 48, 56], [72, 58, 7, 84, 86, 129], [7, 13, 54, 56, 92, 116], [129, 54, 41, 84, 13, 63], [72, 109, 147, 21, 25, 58], [147, 72, 25, 21, 109, 58], [147, 58, 109, 25, 72, 21], [109, 58, 72, 147, 21, 25], [21, 147, 58, 25, 109, 72]]]

#Testing

individual = [[7, 16, 19, 13, 25, 21, 23, 35, 43, 63, 52, 69, 129, 50, 27, 56, 41, 37, 58, 84, 92, 48, 79, 43, 43, 128, 19, 19, 72, 116, 54, 86, 88, 125, 118, 74], [[19, 16, 7, 25, 13], [7, 13, 25, 16, 19], [19, 16, 7, 25, 21, 23], [43, 7, 16, 19, 25, 35], [129, 16, 13, 50, 52, 21], [52, 35, 7, 25, 21, 63], [129, 21, 41, 50, 19, 13], [58, 37, 13, 56, 63, 35], [56, 25, 58, 50, 37, 52], [25, 58, 37, 52, 84, 129], [92, 129, 50, 16, 19, 56], [92, 37, 50, 56, 27, 63], [129, 79, 84, 13, 48, 56], [72, 58, 7, 84, 86, 129], [63, 54, 16, 50, 116, 41], [129, 58, 52, 86, 88, 63], [72, 56, 52, 116, 27, 63], [63, 27, 56, 52, 72, 116], [63, 27, 116, 52, 72, 56], [27, 72, 116, 63, 56, 52], [72, 52, 56, 63, 27, 116]]]



# Mejor individuo de AG
individual = [[7, 16, 21, 19, 13, 29, 23, 74, 10, 43, 52, 69, 96, 50, 27, 56, 95, 37, 58, 84, 104, 48, 129, None, None, 54, None, None, 72, 116, 79, 86, 109, 81, 60, 66], [[21, 19, 13, 16, 7], [16, 7, 21, 13, 19], [19, 21, 7, 13, 29, 74], [13, 29, 10, 43, 19, 23], [29, 52, 10, 96, 7, 69], [29, 19, 74, 96, 7, 52], [95, 74, 16, 52, 21, 29], [58, 19, 74, 69, 27, 104], [21, 10, 52, 13, 50, 84], [19, 48, 52, 16, 7, 54], [27, 54, 37, 16, 69, 56], [27, 7, 21, 50, 69, 95], [58, 27, 104, 50, 69, 52], [7, 50, 79, 19, 81, 69], [58, 104, 54, 48, 16, 109], [54, 19, 109, 13, 116, 74], [7, 86, 13, 52, 21, 116], [52, 21, 7, 116, 86, 13], [116, 7, 86, 13, 21, 52], [86, 13, 7, 52, 116, 21], [116, 52, 21, 86, 7, 13]]]
simulated_annealing(individual, T_0, T_min)