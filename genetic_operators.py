import random
from route_data.routes import ROUTES, ROUTES_ORDER
from route_data.trainers import TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
from individual import *
import copy

def get_permutation_indices(lists):
    base = lists[0]
    pos = {v: i+1 for i, v in enumerate(base)}
    return [[pos[v] for v in l] for l in lists]

def apply_permutations(base, perms):
    return [[base[i-1] for i in p] for p in perms]

def mutate_individual_hard_feasibility(individual: list, prob_mutate_catches=0.2, prob_mutate_team=0.2, seed=None):
    '''
    Obtain a feasible individual (pkm used had been catched)
    '''
    
    if seed is not None:
        random.seed(seed)
    
    # Crear copia profunda para no modificar el original directamente
    mutated_individual = copy.deepcopy(individual)
    catches = mutated_individual[0]
    teams = mutated_individual[1]
    
    previous_catches = catches.copy()
    
    # Permutaciones para asignar luego a los equipos de la liga
    equal_teams = [teams[16], teams[17], teams[18], teams[19], teams[20]]
    permutations = get_permutation_indices(equal_teams)

    # No mutar los últimos 4 equipos de la Liga
    excluded_keys = ["ALTO_MANDO_BRUNO", "ALTO_MANDO_AGATHA", "ALTO_MANDO_LANCE", "RIVAL_CAMPEON"]
    filtered_items = {k: v for k, v in PREVIOUS_ROUTES_TO_TRAINER.items() if k not in excluded_keys}

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
    
    # Arreglar equipos basado en los cambios de capturas
    for i in range(len(catches)):
        if catches[i] != previous_catches[i]:
            old_value = previous_catches[i]
            new_value = catches[i]
            
            # Encontrar qué entrenadores pueden usar esta captura (los que vienen DESPUÉS de la ruta i)
            for trainer_index, (trainer_name, max_route) in enumerate(filtered_items.items()):
                # El entrenador puede usar pokémon de rutas <= max_route
                if i < max_route:
                    # Actualizar en el equipo de este entrenador
                    for pkm_index in range(len(teams[trainer_index])):
                        if teams[trainer_index][pkm_index] == old_value:
                            teams[trainer_index][pkm_index] = new_value
    
    # Limpiar equipos que se hayan podido quedar con algún None y asegurar que añadan pokémon disponibles
    for trainer_index, (trainer_name, max_route) in enumerate(filtered_items.items()):
        # Pokémon disponibles para este entrenador
        available_pokemon = [pkm for pkm in catches[:max_route] if pkm is not None]
        
        # Limpiar equipo actual: quitar pokémon que ya no están disponibles
        cleaned_team = list(set(pkm for pkm in teams[trainer_index] if pkm in available_pokemon))
        
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
   
    for trainer_index, (trainer_name, max_route) in enumerate(filtered_items.items()):
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

    teams_ligue = apply_permutations(teams[16], permutations)
    teams[17] = teams_ligue[1]
    teams[18] = teams_ligue[2]
    teams[19] = teams_ligue[3]
    teams[20] = teams_ligue[4]

    # Con probabilidad prob_mutate_team, permutar alguno de equipos
    for i in range(0, 21):
        if random.random() < prob_mutate_team:
            # Permutar el equipo
            random.shuffle(teams[i])
    
    return mutated_individual




def crossover_individuals(parent1: list, parent2: list, seed=None):
    '''
    Crossover between two individuals
    Returns a feasible child
    '''
    if seed is not None:
        random.seed(seed)
    
    child = [
        [None] * len(parent1[0]),  # catches
        []  # teams
    ]
    
    teams1 = parent1[1]
    teams2 = parent2[1]
    
    num_teams = len(teams1)
    last_five = list(range(num_teams - 5, num_teams))  # [16, 17, 18, 19, 20] si hay 21 equipos
    
    # Elegir al azar de qué padre vienen los últimos 5 equipos
    league_parent = random.choice([1, 2])
    
    # Seleccionar aleatoriamente qué equipos (excepto los últimos 5) vienen de cada padre
    team_indices = list(range(num_teams - 5))  # solo los primeros
    random.shuffle(team_indices)
    half = len(team_indices) // 2
    from_parent1 = set(team_indices[:half])
    
    child_teams = []
    for i in range(num_teams):
        if i in last_five:
            # Últimos 5 equipos del mismo padre
            if league_parent == 1:
                child_teams.append(teams1[i][:])
            else:
                child_teams.append(teams2[i][:])
        else:
            # Resto de equipos cruzados normalmente
            if i in from_parent1:
                child_teams.append(teams1[i][:])
            else:
                child_teams.append(teams2[i][:])
    
    child[1] = child_teams
    
    # 2. Primero: construir catches factibles
    child_catches = build_feasible_catches(child_teams)
    child[0] = child_catches
    
    # 3. Asegurar que los equipos solo usen pokémon disponibles
    child = ensure_teams_feasibility(child)
    
    # Obligar que los últimos 5 equipos tengan los mismo enteros aunque pueden estar en distinto orden
    for i in range(17, 21):
        child[1][i] = random.sample(child[1][16], min(6, len(child[1][16])))

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