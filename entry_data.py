POPULATION_NUMBER = 500 # Number of individuals in my population

# Exploration parameters
'''
VALORES PRIMERA PRUEBA

SELECTED_PERCENTAGE_EXPLORATION = 0.8 # Percentage of individuals selected to mutate and cross
CROSS_PERCENTAGE_EXPLORATION = 0.9 # Percentage from selected individuals to be crossed
PROB_MUTATE_CATCHES_EXPLORATION = 0.25
PROB_MUTATE_TEAM_EXPLORATION = 0.25
GENERATION_NUMBER_EXPLORATION = int(0.05 * POPULATION_NUMBER)  # Number of individuals that survive to the generation before generating random ones
# Exploitation parameters
SELECTED_PERCENTAGE_EXPLOITATION = 0.5
CROSS_PERCENTAGE_EXPLOITATION = 0.5
PROB_MUTATE_CATCHES_EXPLOITATION = 0.1
PROB_MUTATE_TEAM_EXPLOITATION = 0.1
GENERATION_NUMBER_EXPLOITATION = int(0.3 * POPULATION_NUMBER)
'''

# EXPLORACIÓN - Máxima diversidad, búsqueda amplia
SELECTED_PERCENTAGE_EXPLORATION = 0.9  # Casi toda la población se selecciona
CROSS_PERCENTAGE_EXPLORATION = 0.95    # Muy alta recombinación
PROB_MUTATE_CATCHES_EXPLORATION = 0.4  # Alta mutación en capturas
PROB_MUTATE_TEAM_EXPLORATION = 0.4     # Alta mutación en equipo
GENERATION_NUMBER_EXPLORATION = int(0.02 * POPULATION_NUMBER)  # Muy pocos supervivientes

# EXPLOTACIÓN - Máxima convergencia, búsqueda local
SELECTED_PERCENTAGE_EXPLOITATION = 0.3  # Solo los mejores
CROSS_PERCENTAGE_EXPLOITATION = 0.3     # Poca recombinación
PROB_MUTATE_CATCHES_EXPLOITATION = 0.05 # Muy baja mutación
PROB_MUTATE_TEAM_EXPLOITATION = 0.05    # Muy baja mutación  
GENERATION_NUMBER_EXPLOITATION = int(0.5 * POPULATION_NUMBER)  # Muchos supervivientes


SELECTED_PERCENTAGE = 0.7
CROSS_PERCENTAGE = 0.7
PROB_MUTATE_CATCHES = 0.15
PROB_MUTATE_TEAM = 0.15
GENERATION_NUMBER = int(0.15 * POPULATION_NUMBER)




T_0 = 3000
T_min = 1
PASOS = 5