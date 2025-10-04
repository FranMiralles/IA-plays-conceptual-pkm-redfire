from decimal import Decimal, ROUND_DOWN
from entry_data import *
from genetic_operators import *
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os

def generate_population(quantity):
    population = []
    for i in range(0, quantity):
        population.append({
            "gene": generate_individual(),
            "fitness": None  # Inicialmente sin calcular
        })
    return population

def eval_individual(individual, dataset):
    """Evalúa un individuo (versión para threading)"""
    # Si ya tiene fitness calculado, devolver directamente
    if individual.get("fitness") is not None:
        return individual
    
    # Calcular fitness si no está calculado
    (_, fitness_value, _) = calculate_fitness(individual["gene"], dataset, verbose=False)
    individual["fitness"] = fitness_value
    return individual

def eval_population_parallel(population, dataset, max_workers=None):
    """Evalúa la población en paralelo usando threads"""
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 4)  # Limitar para Windows
    
    # Filtrar individuos que necesitan evaluación
    individuals_to_evaluate = []
    indices_to_evaluate = []
    
    for i, ind in enumerate(population):
        if ind.get("fitness") is None:
            individuals_to_evaluate.append(ind)
            indices_to_evaluate.append(i)
    
    print(f"  Evaluando {len(individuals_to_evaluate)}/{len(population)} individuos...")
    
    # Si todos ya tienen fitness, devolver directamente
    if not individuals_to_evaluate:
        return population
    
    # Evaluar solo los que necesitan usando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear tareas
        futures = []
        for ind in individuals_to_evaluate:
            future = executor.submit(eval_individual, ind, dataset)
            futures.append(future)
        
        # Recoger resultados
        evaluated_individuals = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # Timeout de 5 minutos
                evaluated_individuals.append(result)
            except Exception as e:
                print(f"Error evaluando individuo: {e}")
                # En caso de error, asignar un fitness alto (malo)
                ind_copy = ind.copy()
                ind_copy["fitness"] = 1000.0  # Fitness muy malo
                evaluated_individuals.append(ind_copy)
    
    # Actualizar la población original
    for idx, evaluated_ind in zip(indices_to_evaluate, evaluated_individuals):
        population[idx] = evaluated_ind
    
    return population

def eval_population_sequential(population, dataset):
    """Evalúa población de forma secuencial, solo los que no tienen fitness"""
    for individual in population:
        if individual.get("fitness") is None:
            try:
                (_, fitness_value, _) = calculate_fitness(individual["gene"], dataset, verbose=False)
                individual["fitness"] = fitness_value
            except Exception as e:
                print(f"Error evaluando individuo: {e}")
                individual["fitness"] = 1000.0  # Fitness muy malo en caso de error
    
    return population

def prob_population(population):
    # Filtrar solo individuos con fitness calculado
    evaluated_population = [ind for ind in population if ind.get("fitness") is not None]
    
    if not evaluated_population:
        # Si ningún individuo tiene fitness, asignar probabilidades uniformes
        for ind in population:
            ind["prob"] = 1.0 / len(population)
        return population
    
    # Convertir a float para evitar problemas de precisión
    fitness_values = [float(ind["fitness"]) for ind in evaluated_population]
    sum_all_fitness = sum(fitness_values)
    
    if sum_all_fitness == 0:
        # Si todos los fitness son 0, usar probabilidades uniformes
        prob_value = 1.0 / len(evaluated_population)
        for ind in evaluated_population:
            ind["prob"] = prob_value
    else:
        # Calcular probabilidades normalizadas
        probs = [1 - (fitness / sum_all_fitness) for fitness in fitness_values]
        
        # Normalizar para que sumen exactamente 1
        total_prob = sum(probs)
        normalized_probs = [p / total_prob for p in probs]
        
        # Asignar probabilidades solo a los evaluados
        for i, ind in enumerate(evaluated_population):
            ind["prob"] = normalized_probs[i]
        
        # Los no evaluados tienen probabilidad 0
        for ind in population:
            if ind.get("fitness") is None:
                ind["prob"] = 0.0
    
    return population

def select_from_population(population, percentage):
    # Filtrar solo individuos con probabilidad > 0 (los evaluados)
    eligible_population = [ind for ind in population if ind.get("prob", 0) > 0]
    
    if not eligible_population:
        return [], population.copy()
    
    k = int(len(eligible_population) * percentage)
    
    if k == 0:
        return [], population.copy()
    
    # Extraer probabilidades
    probabilities = [ind["prob"] for ind in eligible_population]
    
    # Normalizar por si hay errores de redondeo
    total_prob = sum(probabilities)
    if total_prob > 0:
        probabilities = [p / total_prob for p in probabilities]
    else:
        probabilities = [1/len(eligible_population)] * len(eligible_population)

    selected_idx = np.random.choice(
        len(eligible_population),
        size=k,
        replace=False,
        p=probabilities
    )

    selected = [eligible_population[i] for i in selected_idx]
    non_selected = [ind for ind in population if ind not in selected]
    
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

def crossover_population(pairs):
    """Crea nuevos hijos sin fitness calculado"""
    children = []
    
    for parent1, parent2 in pairs:
        gene1 = parent1["gene"]
        gene2 = parent2["gene"]
        
        child_gene = crossover_individuals(gene1, gene2)
        children.append({
            "gene": child_gene,
            "fitness": None  # Nuevo individuo, sin fitness calculado
        })
    
    return children

def mute_selected(selected_to_mute):
    """Crea individuos mutados sin fitness calculado"""
    muted = []
    for selected in selected_to_mute:
        muted_gene = mutate_individual_hard_feasibility(selected["gene"], PROB_MUTATE_CATCHES, PROB_MUTATE_TEAM)
        muted.append({
            "gene": muted_gene,
            "fitness": None  # Nuevo individuo, sin fitness calculado
        })
    
    return muted

def get_best_individuals(population, x):
    """Devuelve los mejores individuos completos (con gene y fitness)"""
    # Filtrar individuos que tienen fitness calculado
    evaluated_population = [ind for ind in population if ind.get("fitness") is not None]
    
    if not evaluated_population:
        return []
    
    if len(evaluated_population) < x:
        print(f"  Advertencia: Solo {len(evaluated_population)} individuos evaluados de {x} solicitados")
        x = len(evaluated_population)
    
    sorted_population = sorted(evaluated_population, key=lambda ind: ind["fitness"])
    return sorted_population[:x]

# ALGORITMO GENÉTICO OPTIMIZADO (VERSIÓN WINDOWS-SEGURA)
if __name__ == "__main__":
    population = generate_population(POPULATION_NUMBER)
    
    for generation in range(0, 0):
        print("GENERATION: ", generation)
        
        # 1. EVALUAR POBLACIÓN ACTUAL (solo los que no tienen fitness)
        # Usar versión secuencial para mayor estabilidad en Windows
        population = eval_population_sequential(population, dataset)
        # O comentar la línea anterior y descomentar esta para usar threads:
        # population = eval_population_parallel(population, dataset)
        
        # 2. CALCULAR PROBABILIDADES
        population_with_prob = prob_population(population)
        
        # 3. SELECCIÓN
        selected_to_cross_mute, non_selected = select_from_population(population_with_prob, SELECTED_PERCENTAGE)
        
        # Verificar que tenemos individuos para continuar
        if len(selected_to_cross_mute) < 2:
            print("  No hay suficientes individuos seleccionados, generando nueva población...")
            population = generate_population(POPULATION_NUMBER)
            continue
            
        selected_to_cross, selected_to_mute = select_from_population(selected_to_cross_mute, CROSS_PERCENTAGE)
        
        # 4. OPERADORES GENÉTICOS (crean nuevos individuos sin fitness)
        children = []
        if len(selected_to_cross) >= 2:
            pairs_to_cross = pair_individuals_for_crossover(selected_to_cross)
            children = crossover_population(pairs_to_cross)
        
        muted = []
        if selected_to_mute:
            muted = mute_selected(selected_to_mute)
        
        # 5. EVALUAR NUEVOS INDIVIDUOS (solo los nuevos)
        new_individuals = children + muted
        if new_individuals:
            new_individuals_evaluated = eval_population_sequential(new_individuals, dataset)
        else:
            new_individuals_evaluated = []
        
        # 6. COMBINAR Y SELECCIONAR MEJORES
        all_individuals = population + new_individuals_evaluated
        
        # Asegurar que tenemos suficientes individuos evaluados
        evaluated_count = len([ind for ind in all_individuals if ind.get("fitness") is not None])
        if evaluated_count < GENERATION_NUMBER:
            missing = GENERATION_NUMBER - evaluated_count
            additional = generate_population(missing)
            additional_evaluated = eval_population_sequential(additional, dataset)
            all_individuals.extend(additional_evaluated)
        
        best_individuals = get_best_individuals(all_individuals, GENERATION_NUMBER)
        
        # 7. COMPLETAR POBLACIÓN
        new_random = generate_population(POPULATION_NUMBER - GENERATION_NUMBER)
        
        # 8. NUEVA POBLACIÓN (los mejores mantienen su fitness, los nuevos no)
        population = best_individuals + new_random
        
        # 9. MOSTRAR PROGRESO
        evaluated_population = [ind for ind in population if ind.get("fitness") is not None]
        if evaluated_population:
            current_fitness = [ind["fitness"] for ind in evaluated_population]
            best_fitness = min(current_fitness)
            avg_fitness = sum(current_fitness) / len(current_fitness)
            print(f"  Mejor fitness: {best_fitness:.4f}, Promedio: {avg_fitness:.4f}")
            print("POPULATION:")
            print(population)
        
        print("-" * 50)

    print("Ejecución completada")


(pasa, value, logs)=calculate_fitness(


    individual=[
        [7, None, 56, None, None, 21, None, 74, 43, 63, None, None, None, 50, None, None, None, 58, 37, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [
            [7], # "GYM_PLATEADA"
            [43, 7], #"GYM_CELESTE"
            [50], # "GYM_CARMIN"
            [58, 37], # "GYM_AZULONA"
            [7, 58, 56], # "GIOVANNI_AZULONA"
            [7, 58, 56], # "GIOVANNI_AZAFRAN"
            [63], # "GYM_FUCSIA"
            [58, 7], # "GYM_AZAFRAN"
            [7], # "GYM_CANELA"
            [7], # "GYM_VERDE"
            [58, 43], # "ALTO_MANDO_LORELEI"
            [7, 21], # "ALTO_MANDO_BRUNO"
            [63, 7], # "ALTO_MANDO_AGATHA"
            [7, 74] # "ALTO_MANDO_LANCE"
        ]
    ],
    dataset=dataset,
    verbose=True
)

#for log in logs:
#    print(logs)
print(value)


