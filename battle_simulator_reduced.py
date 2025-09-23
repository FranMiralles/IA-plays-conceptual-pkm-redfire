import requests
import statistics
import json
from route_data.trainers import TRAINERS, TRAINERS_ORDER
import time

# In this version, in pkm battles the individuals only choose the team used in a gym. Attacks used are selected among the possible ones maximizing damage dealt to the rival's pkm. Also, current pkm cannot switch so the current pkm steals being the current one until the battle finishes or the pkm is dead.

# 

def load_json_in_dataset():
    def cargar_json(nombre_archivo):
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
            return datos
        except FileNotFoundError:
            print(f"El archivo {nombre_archivo} no existe.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON en {nombre_archivo}: {e}")
            return {}
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return {}
    dataset = {}
    evolutions = cargar_json("./pkm_data/evolutions.json")
    moves = cargar_json("./pkm_data/moves_priority.json")
    pkdex = cargar_json("./pkm_data/pkdex.json")
    dataset["evolutions"] = evolutions
    dataset["moves"] = moves
    dataset["pkdex"] = pkdex
    return dataset

def calculate_speed(base: int, level: int):
    return int((((2 * base) + 31)*level)/100 + 5)

def deal_damage(attacker:object, defender:object, move:str):
    '''
    Returns the damage dealt by an attacker to a defender using a move in format % of HP lost
        attacker: obj
                    - species: str
                    - ability: str
                    - level: int
        defender: obj
                    - species: str
                    - ability: str
                    - level: int
        move: str
    '''
    data={
        "genReq": 3,
        "attacker": attacker,
        "defender": defender,
        "move": move
    }
    res = requests.post("http://localhost:3000/calc", json=data)
    maxHP = res.json()["defender"]["rawStats"]["hp"]
    if(type(res.json()["damage"]) == type(1)):
        lostHP = round(res.json()["damage"] / maxHP, 2)
    else:
        lostHP = round(statistics.median(res.json()["damage"]) / maxHP, 2)
    return lostHP

def select_best_attack(attacker:object, target:object):
    '''
        attacker: obj
                    - species: str
                    - ability: str
                    - level: int
                    - moves: list(str)
        defender: obj
                    - species: str
                    - ability: str
                    - level: int
    '''
    best_move = ("", 0)
    for move in attacker["moves"]:
        lostHP = deal_damage(
            {
                "species": attacker["species"],
                "ability": attacker["ability"],
                "level": attacker["level"],
            }
        ,target, move=move)
        if(lostHP > best_move[1]):
            best_move = (move, lostHP)
    return best_move

def select_level_cap(rival_team:object):
    '''
    Returns max level of the rival team
        rival_team: list of objects
            - name: str
            - level: int
            - ability: str
            - moves: list
    '''
    max_level = 1
    for pkm in rival_team:
        if(pkm["level"] > max_level):
            max_level = pkm["level"]
    return max_level


def simulate_battle(team: list, rival_team: list, dataset: object, debug:bool):
    '''
        team: list of int idPkm
        rival_team: list of objects
                    - name: str
                    - level: int
                    - ability: str
                    - moves: list
        dataset: object
                    - evolutions.json to object
                    - moves.json to object
                    - pkdex.json to object
    '''
    start = time.perf_counter()
    level_cap = select_level_cap(rival_team)

    # Evolve team
    team_evolved = []
    for pkmID in team:
        pkmID = str(pkmID)
        while pkmID in dataset["evolutions"]:
            if dataset["evolutions"][pkmID][1] == 'level-up' and dataset["evolutions"][pkmID][2] <= level_cap:
                pkmID = str(dataset["evolutions"][pkmID][0])
            else:
                break
        team_evolved.append(int(pkmID))
    team = team_evolved

    totalHP_team = len(team) * 100
    totalHP_rival_team = len(rival_team) * 100
    damage_team = 0
    damage_rival_team = 0

    turn = 0

    while damage_team < totalHP_team and damage_rival_team < totalHP_rival_team :
        # New turn
        turn += 1
        if debug:
            print("TURNO", turn)
            print("**********************")
        
        # Select the active pkm and the rival one
        activePkmID = team[damage_team // 100]
        active_HP = 100 - (damage_team % 100)
        
        activePkm = {
            "species": dataset["pkdex"][str(activePkmID)]["name"],
            "level": level_cap,
            "ability": dataset["pkdex"][str(activePkmID)]["abilities"],
            "speed": calculate_speed(dataset["pkdex"][str(activePkmID)]["speed"], level_cap),
            "moves": [move_key for move_key, move_value in dataset["pkdex"][str(activePkmID)]["moves"].items() if move_value["level"] <= level_cap]
        }
        
        rival_selected_pos = damage_rival_team // 100
        active_rival_HP = 100 - (damage_rival_team % 100)
        
        if debug:
            print(activePkm["species"], "HP", active_HP)
            print(rival_team[rival_selected_pos]["species"], "HP", active_rival_HP)
        
        # Choose which move selects each pkm
        activePkm_attack = select_best_attack(activePkm, rival_team[rival_selected_pos])
        activePkm_rival_attack = select_best_attack(rival_team[rival_selected_pos], activePkm)

        player_first = False
        # Which of the moves performs first
        if dataset["moves"][activePkm_attack[0]] > dataset["moves"][activePkm_rival_attack[0]]:
            player_first = True
        elif dataset["moves"][activePkm_rival_attack[0]] > dataset["moves"][activePkm_attack[0]]:
            player_first = False
        else:
            if activePkm["speed"] > rival_team[rival_selected_pos]["speed"]:
                player_first = True

        player_damage = round(activePkm_attack[1] * 100)
        rival_damage = round(activePkm_rival_attack[1] * 100)

        # Perform first move and reduce hp
        if player_first:
            # Player attacks first
            if debug:
                print(activePkm["species"], "attacks with", activePkm_attack)
            if active_rival_HP <= player_damage:
                damage_rival_team += active_rival_HP
                active_rival_HP = 0
            else:
                if debug:
                    print(rival_team[rival_selected_pos]["species"], "attacks with", activePkm_rival_attack)
                damage_rival_team += player_damage
                active_rival_HP -= player_damage
                # Rival attacks back
                if active_HP <= rival_damage:
                    damage_team += active_HP
                    active_HP = 0
                else:
                    damage_team += rival_damage
                    active_HP -= rival_damage
        else:
            # Rival attacks first
            if debug:
                print(rival_team[rival_selected_pos]["species"], "attacks with", activePkm_rival_attack)
            if active_HP <= rival_damage:
                damage_team += active_HP
                active_HP = 0
            else:
                if debug:
                    print(activePkm["species"], "attacks with", activePkm_attack)
                damage_team += rival_damage
                active_HP -= rival_damage
                # Player attacks back
                if active_rival_HP <= player_damage:
                    damage_rival_team += active_rival_HP
                    active_rival_HP = 0
                else:
                    damage_rival_team += player_damage
                    active_rival_HP -= player_damage

        if debug:
            print(activePkm["species"], "HP", active_HP)
            print(rival_team[rival_selected_pos]["species"], "HP", active_rival_HP)

    end = time.perf_counter()
    elapsed_seconds = end - start
    if debug:
        print(f"Tiempo total: {elapsed_seconds:.6f} s")
    
    player_wins = (damage_team < totalHP_team)
    return (player_wins, damage_team)

def calculate_fitness(individual:list, dataset):
    '''
        individual: list
            - first element: list of int that reference pkmID of catched
    '''
    pkm_catched = individual[0]
    teams = individual[1]
    simulations = []
    for i in range(0, len(teams)):
        simulations.append(simulate_battle(team=teams[i], rival_team=TRAINERS[TRAINERS_ORDER[i]], dataset=dataset, debug=True))

    for simulation in simulations:
        print(simulation)


dataset = load_json_in_dataset()


# (passed, damage_lost) = simulate_battle([1, 1, 1, 1, 1, 1], TRAINERS["GYM_CARMIN"], dataset=dataset, debug=True)
# print("RESULTADOS")
# print(passed)
# print(damage_lost)

calculate_fitness([[1,2,3,4,5,6,7,8,9],[[1,4,7],[1,4,7],[1,4,7],[1,4,7],[1,4,7],[1,4,7],[1,4,7],[1,4,7]]], dataset=dataset)