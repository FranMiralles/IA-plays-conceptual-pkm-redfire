import random
from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
from individual import *


def mutate_individual_hard_feasibility(individual: list, prob_mutate_catches=0.2, prob_mutate_team=0.2, seed=None):
    '''
    Obtain a feasible individual (pkm used had been catched)
    '''
    import copy
    
    if seed is not None:
        random.seed(seed)
    
    # Crear copia profunda para no modificar el original directamente
    mutated_individual = copy.deepcopy(individual)
    catches = mutated_individual[0]
    teams = mutated_individual[1]
    
    previous_catches = catches.copy()
    
    # Mutate catches
    for i in range(0, len(catches)):
        if random.random() < prob_mutate_catches:
            # Mutate from possible pkm in route that has not been catched yet
            catched_yet = catches[:i]
            available = [x for x in ROUTES[ROUTES_ORDER[i]] if x != catches[i] and x not in catched_yet]
            if len(available) != 0:
                catches[i] = random.choice(available)
                
                # Arreglar posibles duplicados en capturas futuras
                for j in range(i + 1, len(catches)):
                    if catches[j] == catches[i]:
                        available_j = [x for x in ROUTES[ROUTES_ORDER[j]] if x not in catches]
                        if len(available_j) == 0:
                            catches[j] = None
                        else:
                            catches[j] = random.choice(available_j)
    
    # CORREGIDO: Actualizar equipos basado en los cambios de capturas
    for i in range(len(catches)):
        if catches[i] != previous_catches[i]:
            old_value = previous_catches[i]
            new_value = catches[i]
            
            # Encontrar qué entrenadores pueden usar esta captura (los que vienen DESPUÉS de la ruta i)
            for trainer_index, (trainer_name, max_route) in enumerate(PREVIOUS_ROUTES_TO_TRAINER.items()):
                # El entrenador puede usar pokémon de rutas <= max_route
                if i < max_route:
                    # Actualizar en el equipo de este entrenador
                    for pkm_index in range(len(teams[trainer_index])):
                        if teams[trainer_index][pkm_index] == old_value:
                            teams[trainer_index][pkm_index] = new_value
    
    # CORREGIDO: Limpiar equipos y asegurar que solo usen pokémon disponibles
    for trainer_index, (trainer_name, max_route) in enumerate(PREVIOUS_ROUTES_TO_TRAINER.items()):
        # Pokémon disponibles para este entrenador
        available_pokemon = [pkm for pkm in catches[:max_route] if pkm is not None]
        
        # Limpiar equipo actual: quitar pokémon que ya no están disponibles
        cleaned_team = [pkm for pkm in teams[trainer_index] if pkm in available_pokemon]
        
        # Si el equipo tiene menos de 6 pokémon, completar con disponibles
        if len(cleaned_team) < 6:
            # Pokémon disponibles que no están en el equipo
            remaining_available = [pkm for pkm in available_pokemon if pkm not in cleaned_team]
            # Añadir pokémon aleatorios hasta completar 6
            needed = 6 - len(cleaned_team)
            if len(remaining_available) >= needed:
                additional = random.sample(remaining_available, needed)
                cleaned_team.extend(additional)
            else:
                # Si no hay suficientes, usar todos los disponibles
                cleaned_team.extend(remaining_available)
        
        # Si el equipo tiene más de 6 pokémon, recortar
        if len(cleaned_team) > 6:
            cleaned_team = cleaned_team[:6]
            
        teams[trainer_index] = cleaned_team

    
    # Mutate teams
    for trainer_index, (trainer_name, max_route) in enumerate(PREVIOUS_ROUTES_TO_TRAINER.items()):
        # Pokémon disponibles para este entrenador
        available_pokemon = [pkm for pkm in catches[:max_route] if pkm is not None]
        
        # Si no hay pokémon disponibles, saltar este entrenador
        if not available_pokemon:
            continue
            
        for pkm_index in range(len(teams[trainer_index])):
            if random.random() < prob_mutate_team:
                current_pkm = teams[trainer_index][pkm_index]
                
                # Opciones disponibles (excluyendo el actual y los que ya están en el equipo)
                team_without_current = [pkm for i, pkm in enumerate(teams[trainer_index]) if i != pkm_index]
                available_options = [pkm for pkm in available_pokemon 
                                if pkm != current_pkm and pkm not in team_without_current]
                
                if available_options:
                    # Elegir nuevo pokémon
                    new_pkm = random.choice(available_options)
                    teams[trainer_index][pkm_index] = new_pkm
                else:
                    # Si no hay opciones, mantener el actual
                    pass

    return mutated_individual

def crossover_individuals(parent1: list, parent2: list, seed=None):
    '''
    Crossover between two individuals
    Returns a feasible child
    '''
    import random
    import copy
    if seed is not None:
        random.seed(seed)
    
    # Crear estructura básica del hijo
    child = [
        [None] * len(parent1[0]),  # catches
        []  # teams
    ]
    
    # 1. Combinar equipos (mitad de cada padre)
    teams1 = parent1[1]
    teams2 = parent2[1]
    
    # Seleccionar aleatoriamente qué equipos vienen de cada padre
    team_indices = list(range(len(teams1)))
    random.shuffle(team_indices)
    
    half = len(team_indices) // 2
    from_parent1 = team_indices[:half]
    from_parent2 = team_indices[half:]
    
    # Construir equipos del hijo
    child_teams = []
    for i in range(len(teams1)):
        if i in from_parent1:
            child_teams.append(teams1[i][:])  # copia
        else:
            child_teams.append(teams2[i][:])  # copia
    
    child[1] = child_teams
    
    # 2. Primero: construir catches factibles
    child_catches = build_feasible_catches(child_teams)
    child[0] = child_catches
    
    # 3. Asegurar que los equipos solo usen pokémon disponibles
    child = ensure_teams_feasibility(child)
    
    return child

def build_feasible_catches(teams):
    '''
    Build catches that satisfy all team requirements
    '''
    catches = [None] * len(ROUTES_ORDER)
    
    # Primero: identificar todos los pokémon requeridos por los equipos
    required_pokemon = set()
    for team in teams:
        for pkm in team:
            if pkm is not None:
                required_pokemon.add(pkm)
    
    # Para cada pokémon requerido, asignarlo a la primera ruta disponible donde aparece
    for pkm in required_pokemon:
        assigned = False
        # Buscar rutas donde puede aparecer este pokémon
        possible_routes = []
        for route_idx, route_name in enumerate(ROUTES_ORDER):
            if pkm in ROUTES[route_name] and catches[route_idx] is None:
                possible_routes.append(route_idx)
        
        if possible_routes:
            # Asignar a la ruta más temprana posible
            catches[min(possible_routes)] = pkm
            assigned = True
    
    # Completar rutas vacías con pokémon disponibles
    for route_idx, route_name in enumerate(ROUTES_ORDER):
        if catches[route_idx] is None:
            available_pokemon = [pkm for pkm in ROUTES[route_name] 
                               if pkm not in catches]
            if available_pokemon:
                catches[route_idx] = random.choice(available_pokemon)
            else:
                # Si no hay disponibles, elegir cualquiera de la ruta
                catches[route_idx] = random.choice(ROUTES[route_name])
    
    return catches

def ensure_teams_feasibility(individual):
    '''
    Ensure that each team only uses pokémon caught before that battle
    '''
    catches = individual[0]
    teams = individual[1]
    
    for trainer_idx, team in enumerate(teams):
        trainer_name = TRAINERS_ORDER[trainer_idx]
        max_route = PREVIOUS_ROUTES_TO_TRAINER[trainer_name]
        
        # Pokémon disponibles para este entrenador
        available_pokemon = [pkm for pkm in catches[:max_route] if pkm is not None]
        
        # Curar el equipo: reemplazar pokémon no disponibles
        healed_team = []
        for pkm in team:
            if pkm in available_pokemon and pkm not in healed_team:
                healed_team.append(pkm)
            else:
                # Buscar reemplazo disponible
                possible_replacements = [pkm for pkm in available_pokemon 
                                       if pkm not in healed_team]
                if possible_replacements:
                    healed_team.append(random.choice(possible_replacements))
                # Si no hay reemplazos, simplemente no añadir (el equipo será más pequeño)
        
        # Asegurar que el equipo tenga exactamente 6 pokémon
        while len(healed_team) < 6 and available_pokemon:
            # Añadir pokémon disponibles que no estén en el equipo
            remaining = [pkm for pkm in available_pokemon if pkm not in healed_team]
            if remaining:
                healed_team.append(random.choice(remaining))
            else:
                break
        
        # Si tiene más de 6, recortar
        if len(healed_team) > 6:
            healed_team = healed_team[:6]
            
        teams[trainer_idx] = healed_team
    
    return individual

def is_feasible(individual: list) -> bool:
    '''
    Check if an individual is feasible
    '''
    catches = individual[0]
    teams = individual[1]
    
    # Verificar que no hay pokémon repetidos en catches (excluyendo None)
    non_none_catches = [pkm for pkm in catches if pkm is not None]
    if len(non_none_catches) != len(set(non_none_catches)):
        return False
    
    # Verificar que todos los pokémon en equipos están disponibles para ese entrenador
    for trainer_idx, team in enumerate(teams):
        trainer_name = TRAINERS_ORDER[trainer_idx]
        max_route = PREVIOUS_ROUTES_TO_TRAINER[trainer_name]
        available_pokemon = set([pkm for pkm in catches[:max_route] if pkm is not None])
        
        for pkm in team:
            if pkm is not None and pkm not in available_pokemon:
                return False
    
    return True


for i in range(0, 0):

    '''
    individual = generate_individual()
    print("INDIVIDUAL")
    individual_mutated = mutate_individual_hard_feasibility(individual, 0.1, 1)
    print("INDIVIDUAL MUTATED")
    print(individual_mutated)


    (pasa, fitness_value, log) = calculate_fitness(individual_mutated, dataset=dataset, verbose=False)

    if fitness_value == float("inf"):
        print("SALIENDO POR IMPOSIBLE")
        exit()
    print((pasa, fitness_value, log[:10]))
    '''

    parent1 = generate_individual()
    print(parent1)
    parent2 = generate_individual()
    print(parent2)
    individual_son = crossover_individuals(parent1, parent2)

    (pasa, fitness_value, log) = calculate_fitness(individual_son, dataset=dataset, verbose=False)

    if fitness_value == float("inf"):
        print("SALIENDO POR IMPOSIBLE")
        exit()
    print((pasa, fitness_value, log[:10]))