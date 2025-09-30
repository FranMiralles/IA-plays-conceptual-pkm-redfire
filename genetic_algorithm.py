from decimal import Decimal, ROUND_DOWN
from entry_data import *
from genetic_operators import *
import numpy as np

def generate_population(quantity):
    population = []
    for i in range(0, quantity):
        population.append(generate_individual())
    return population

def eval_population(population):
    population_evalued = []
    for individual in population:
        random.randint(MIN_TRAINERS_DEFEATED_TO_APROX_FITNESS, MAX_TRAINERS_DEFEATED_TO_APROX_FITNESS)
        (_, fitness_value, _) = approximate_fitness(9, individual, dataset, verbose=False)
        population_evalued.append(
            {
                "gene" : individual, 
                "fitness" : fitness_value
            }
        )
    return population_evalued

def prob_population(population_evalued):
    # Convertir a float para evitar problemas de precisión con Decimal
    fitness_values = [float(ind["fitness"]) for ind in population_evalued]
    sum_all_fitness = sum(fitness_values)
    
    # Calcular probabilidades normalizadas
    probs = [1 - (fitness / sum_all_fitness) for fitness in fitness_values]
    
    # Normalizar para que sumen exactamente 1
    total_prob = sum(probs)
    normalized_probs = [p / total_prob for p in probs]
    
    # Asignar probabilidades
    for i, ind in enumerate(population_evalued):
        ind["prob"] = normalized_probs[i]
    
    return population_evalued

def select_from_population(population_evalued, percentage):
    k = int(len(population_evalued) * percentage)
    
    # Verificar que tenemos suficientes individuos
    if k == 0:
        return [], population_evalued.copy()
    
    # Extraer probabilidades y asegurar que suman 1
    probabilities = [ind["prob"] for ind in population_evalued]
    
    # Normalizar nuevamente por si hay errores de redondeo
    total_prob = sum(probabilities)
    if total_prob == 0:
        # Si todas las probabilidades son 0, usar selección uniforme
        probabilities = [1/len(population_evalued)] * len(population_evalued)
    else:
        probabilities = [p / total_prob for p in probabilities]

    selected_idx = np.random.choice(
        len(population_evalued),
        size=k,
        replace=False,
        p=probabilities
    )

    selected_idx_set = set(selected_idx)
    
    selected = []
    non_selected = []
    
    for i, individual in enumerate(population_evalued):
        if i in selected_idx_set:
            selected.append(individual)
        else:
            non_selected.append(individual)
    
    return selected, non_selected

def pair_individuals_for_crossover(selected_individuals):
    import random
    
    individuals = selected_individuals.copy()
    
    if len(individuals) % 2 != 0:
        individuals.pop(random.randint(0, len(individuals) - 1))
    
    random.shuffle(individuals)
    
    pairs = []
    for i in range(0, len(individuals), 2):
        pairs.append((individuals[i], individuals[i + 1]))
    
    return pairs

def crossover_population_genes(pairs):
    children_genes = []
    
    for parent1, parent2 in pairs:
        gene1 = parent1["gene"]
        gene2 = parent2["gene"]
        
        child_gene = crossover_individuals(gene1, gene2)
        children_genes.append(child_gene)
    
    return children_genes

def mute_selected_genes(selected_to_mute):
    muted_genes = []
    for selected in selected_to_mute:
        muted_gene = mutate_individual_hard_feasibility(selected["gene"], PROB_MUTATE_CATCHES, PROB_MUTATE_TEAM)
        muted_genes.append(muted_gene)
    
    return muted_genes

def get_best_individuals_genes(population_evaluated, x):
    sorted_population = sorted(population_evaluated, key=lambda ind: ind["fitness"])
    return [ind["gene"] for ind in sorted_population[:x]]

# ALGORITMO GENÉTICO CORREGIDO
population = generate_population(POPULATION_NUMBER)

for generation in range(0, 10000):
    print("GENERATION: ", generation)
    
    # 1. EVALUAR POBLACIÓN ACTUAL
    population_eval = eval_population(population)
    
    # 2. CALCULAR PROBABILIDADES (para selección)
    population_with_prob = prob_population(population_eval)
    
    # 3. SELECCIÓN
    selected_to_cross_mute, non_selected = select_from_population(population_with_prob, SELECTED_PERCENTAGE)
    
    # Verificar que tenemos individuos para continuar
    if len(selected_to_cross_mute) < 2:
        # Si no hay suficientes, generar nueva población
        population = generate_population(POPULATION_NUMBER)
        continue
        
    selected_to_cross, selected_to_mute = select_from_population(selected_to_cross_mute, CROSS_PERCENTAGE)
    
    # 4. OPERADORES GENÉTICOS
    children_genes = []
    if len(selected_to_cross) >= 2:
        pairs_to_cross = pair_individuals_for_crossover(selected_to_cross)
        children_genes = crossover_population_genes(pairs_to_cross)
    
    muted_genes = []
    if selected_to_mute:
        muted_genes = mute_selected_genes(selected_to_mute)
    
    # 5. EVALUAR NUEVOS INDIVIDUOS
    new_individuals_genes = children_genes + muted_genes
    new_individuals_eval = eval_population(new_individuals_genes) if new_individuals_genes else []
    
    # 6. COMBINAR Y SELECCIONAR MEJORES
    all_individuals_eval = population_eval + new_individuals_eval
    
    # Asegurar que tenemos suficientes individuos
    if len(all_individuals_eval) < GENERATION_NUMBER:
        # Completar con nuevos aleatorios si es necesario
        missing = GENERATION_NUMBER - len(all_individuals_eval)
        additional_genes = generate_population(missing)
        additional_eval = eval_population(additional_genes)
        all_individuals_eval.extend(additional_eval)
    
    best_genes = get_best_individuals_genes(all_individuals_eval, GENERATION_NUMBER)
    
    # 7. COMPLETAR POBLACIÓN
    new_random_genes = generate_population(POPULATION_NUMBER - GENERATION_NUMBER)
    
    # 8. NUEVA POBLACIÓN
    population = best_genes + new_random_genes
    
    # 9. MOSTRAR PROGRESO
    current_fitness = [ind["fitness"] for ind in eval_population(population)]
    best_fitness = min(current_fitness)
    avg_fitness = sum(current_fitness) / len(current_fitness)
    print(f"  Mejor fitness: {best_fitness:.4f}, Promedio: {avg_fitness:.4f}")
    print(population)