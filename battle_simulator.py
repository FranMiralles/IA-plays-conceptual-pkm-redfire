import requests
import statistics
import json
from route_data.trainers import TOTAL_RIVAL_PKM, TRAINERS, TRAINERS_ORDER, PREVIOUS_ROUTES_TO_TRAINER
from route_data.routes import ROUTES_ORDER
from route_data.mt_moves import AVAILABLE_MT_TRAINERS
from route_data.evolve_obj import AVAILABLE_EVOLVE_OBJ_TRAINERS
import time
import math
import random

# In this version, in pkm battles the individuals only choose the team used in a gym. Attacks used are selected among the possible ones maximizing damage dealt to the rival's pkm. Also, current pkm cannot switch so the current pkm steals being the current one until the battle finishes or the pkm is dead.

# A Session to conect via TCP to server
session = requests.Session()

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
    res = session.post("http://localhost:3000/calc", json=data)
    maxHP = res.json()["defender"]["rawStats"]["hp"]
    if(type(res.json()["damage"]) == type(1)):
        lostHP = round(res.json()["damage"] / maxHP, 2)
    else:
        lostHP = round(statistics.median(res.json()["damage"]) / maxHP, 2)
    return lostHP

deal_damage(attacker = {'species': 'Krabby', 'ability': 'hyper-cutter', 'level': 43}, defender={'species': 'Weezing', 'level': 43, 'ability': 'levitate', 'moves': ['sludge', 'tackle'], 'speed': 69}, move="vise-grip")

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
    best_move = ("", float('-inf'))
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

def cure_with_drain_move(attacker_name, attack, real_damage, hp, total_damage, drain_attacks, logs, verbose=False):
    move_name = attack[0]
    if move_name in drain_attacks and real_damage > 0:
        heal = real_damage // 2
        recovered = min(100 - hp, heal)
        hp += recovered
        total_damage -= recovered
        if verbose and recovered > 0:
            log_message = f"{attacker_name} recovers {recovered} HP with {move_name}"
            logs.append(log_message)
    return hp, total_damage

def simulate_battle(team: list, rival_team: list, available_mt: list, available_ev_obj: list,dataset: object, verbose:bool):
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
    level_cap = select_level_cap(rival_team)

    logs = []

    # Evolve team
    
    team_evolved = []
    for pkmID in team:
        pkmID = str(pkmID)
        while pkmID in dataset["evolutions"]:
            if ((
                    dataset["evolutions"][pkmID][1] == 'level-up' and dataset["evolutions"][pkmID][2] <= level_cap
                ) or (
                    dataset["evolutions"][pkmID][1] == "use-item" and dataset["evolutions"][pkmID][2] in available_ev_obj
                )) and (
                    dataset["evolutions"][pkmID][0] <= 151
                ):
                pkmID = str(dataset["evolutions"][pkmID][0])
            else:
                break
        team_evolved.append(int(pkmID))
    team = team_evolved

    logs.append(str(team_evolved))
    

    totalHP_team = len(team) * 100
    totalHP_rival_team = len(rival_team) * 100
    damage_team = 0
    damage_rival_team = 0

    turn = 0

    drain_attacks = ["absorb", "mega-drain", "giga-drain"]
    explosion_moves = ["explosion", "self-destruct"]
    

    player_must_recharge_HB = False # hyper beam
    rival_must_recharge_HB = False # hyper beam

    player_turns_using_sb = 0 # solar beam
    rival_turns_using_sb = 0 # solar beam
    player_turns_using_dig = 0 # dig
    rival_turns_using_dig = 0 # dig
    player_turns_using_fly = 0 # fly
    rival_turns_using_fly = 0 # fly

    while damage_team < totalHP_team and damage_rival_team < totalHP_rival_team:
        # New turn
        turn += 1
        logs.append("TURNO " + str(turn))
        
        # Select the active pkm and the rival one
        activePkmID = team[damage_team // 100]
        active_HP = 100 - (damage_team % 100)
        activePkm = {
            "species": dataset["pkdex"][str(activePkmID)]["name"],
            "level": level_cap,
            "ability": dataset["pkdex"][str(activePkmID)]["abilities"],
            "speed": calculate_speed(dataset["pkdex"][str(activePkmID)]["speed"], level_cap),
            "moves": 
                    [move_key 
                        for move_key, move_value in dataset["pkdex"][str(activePkmID)]["moves"].items() 
                            if (
                                (move_value["level"] <= level_cap and move_value["method"] == "level-up" and move_key not in explosion_moves) 
                                or 
                                (move_value["method"] == "machine" and move_key in available_mt and move_key not in explosion_moves)
                                )
                    ]
        }
        
        rival_selected_pos = damage_rival_team // 100
        active_rival_HP = 100 - (damage_rival_team % 100)
        
        logs.append("PLAYER " + activePkm["species"] + " HP " + str(active_HP))
        logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " HP " + str(active_rival_HP))
        
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


        # FLAGS CASES

        # Hyper beam
        player_uses_hyperbeam = True if activePkm_attack[0] == "hyper-beam" and not player_must_recharge_HB else False
        rival_uses_hyperbeam = True if activePkm_rival_attack[0] == "hyper-beam" and not rival_must_recharge_HB else False

        # Solar beam
        if activePkm_attack[0] == "solar-beam":  
            player_turns_using_sb += 1
        else:
            player_turns_using_sb = 0
        if activePkm_rival_attack[0] == "solar-beam":  
            rival_turns_using_sb += 1
        else:
            rival_turns_using_sb = 0
        
        # Dig
        if activePkm_attack[0] == "dig":  
            player_turns_using_dig += 1
        else:
            player_turns_using_dig = 0
        if activePkm_rival_attack[0] == "dig":
            rival_turns_using_dig += 1
        else:
            rival_turns_using_dig = 0

        # Fly
        if activePkm_attack[0] == "fly":
            player_turns_using_fly += 1
        else:
            player_turns_using_fly = 0
        if activePkm_rival_attack[0] == "fly":
            rival_turns_using_fly += 1
        else:
            rival_turns_using_fly = 0

        # Dive
        if activePkm_attack[0] == "dive":
            player_turns_using_dive += 1
        else:
            player_turns_using_dive = 0
        if activePkm_rival_attack[0] == "dive":
            rival_turns_using_dive += 1
        else:
            rival_turns_using_dive = 0

        # Damage
        player_damage = round(activePkm_attack[1] * 100) if not player_must_recharge_HB and player_turns_using_sb != 1 and player_turns_using_dig != 1 and player_turns_using_fly != 1 and player_turns_using_dive != 1 else 0
        rival_damage = round(activePkm_rival_attack[1] * 100) if not rival_must_recharge_HB and rival_turns_using_sb != 1 and rival_turns_using_dig != 1 and rival_turns_using_fly != 1 and rival_turns_using_dive != 1 else 0


        # player_uses_explosion = True if activePkm_attack[0] in explosion_moves and not player_must_recharge_HB else False
        # rival_uses_explosion = True if activePkm_rival_attack[0] in explosion_moves and not rival_must_recharge_HB else False
        
        # TURN
        # Perform first move and reduce hp
        if player_first:
            # Player attacks first
            if player_must_recharge_HB:
                logs.append("PLAYER " + activePkm["species"] + " must recharge!")
            elif player_turns_using_sb == 1:
                logs.append("PLAYER " + activePkm["species"] + " took in sunlight!")
            elif player_turns_using_dig == 1:
                logs.append("PLAYER " + activePkm["species"] + " dug a hole!")
                rival_damage = 0
            elif player_turns_using_fly == 1:
                logs.append("PLAYER " + activePkm["species"] + " flew up high!")
                rival_damage = 0
            elif player_turns_using_dive == 1:
                logs.append("PLAYER " + activePkm["species"] + " hid underwater!")
                rival_damage = 0
            else:
                logs.append("PLAYER " + activePkm["species"] + " attacks with " + str(activePkm_attack))

            # Rival is inmune if has used in the last turn an inmune attack
            if rival_turns_using_dig == 2:
                player_damage = 0
            if rival_turns_using_fly == 2:
                player_damage = 0
            if rival_turns_using_dive == 2:
                player_damage = 0

            # Normal behaviour
            if active_rival_HP <= player_damage:
                # Rival death
                real_damage = active_rival_HP
                damage_rival_team += active_rival_HP
                active_rival_HP = 0
                # Cure player if drain attack
                active_HP, damage_team = cure_with_drain_move(
                    attacker_name=activePkm["species"],
                    attack=activePkm_attack,
                    real_damage=real_damage,
                    hp=active_HP,
                    total_damage=damage_team,
                    drain_attacks=drain_attacks,
                    logs=logs,
                    verbose=verbose
                )

                if player_uses_hyperbeam:
                    player_must_recharge_HB = True
                if rival_uses_hyperbeam:
                    rival_must_recharge_HB = False

            else:
                real_damage = player_damage
                damage_rival_team += player_damage
                active_rival_HP -= player_damage
                # Cure player if drain attack
                active_HP, damage_team = cure_with_drain_move(
                    attacker_name=activePkm["species"],
                    attack=activePkm_attack,
                    real_damage=real_damage,
                    hp=active_HP,
                    total_damage=damage_team,
                    drain_attacks=drain_attacks,
                    logs=logs,
                    verbose=verbose
                )

                # Rival attacks back
                if rival_must_recharge_HB:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " must recharge!")
                elif rival_turns_using_sb == 1:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " took in sunlight!")
                elif rival_turns_using_dig == 1:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " dug a hole!")
                elif rival_turns_using_fly == 1:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " flew up high!")
                elif rival_turns_using_dive == 1:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " hid underwater!")
                else:
                    logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " attacks with " + str(activePkm_rival_attack))

                if active_HP <= rival_damage:
                    real_damage = active_HP
                    damage_team += active_HP
                    active_HP = 0
                    # Cure rival if drain attack
                    active_rival_HP, damage_rival_team = cure_with_drain_move(
                        attacker_name=rival_team[rival_selected_pos]["species"],
                        attack=activePkm_rival_attack,
                        real_damage=real_damage,
                        hp=active_rival_HP,
                        total_damage=damage_rival_team,
                        drain_attacks=drain_attacks,
                        logs=logs,
                        verbose=verbose
                    )

                    
                    if player_uses_hyperbeam:
                        player_must_recharge_HB = False
                    if rival_uses_hyperbeam:
                        rival_must_recharge_HB = True

                else:
                    real_damage = rival_damage
                    damage_team += rival_damage
                    active_HP -= rival_damage
                    # Cure rival if drain attack
                    active_rival_HP, damage_rival_team = cure_with_drain_move(
                        attacker_name=rival_team[rival_selected_pos]["species"],
                        attack=activePkm_rival_attack,
                        real_damage=real_damage,
                        hp=active_rival_HP,
                        total_damage=damage_rival_team,
                        drain_attacks=drain_attacks,
                        logs=logs,
                        verbose=verbose
                    )

                    if player_uses_hyperbeam:
                        player_must_recharge_HB = True
                    if rival_uses_hyperbeam:
                        rival_must_recharge_HB = True

        else:
            # Rival attacks first
            if rival_must_recharge_HB:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " must recharge!")
            elif rival_turns_using_sb == 1:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " took in sunlight!")
            elif rival_turns_using_dig == 1:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " dug a hole!")
                player_damage = 0
            elif rival_turns_using_fly == 1:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " flew up high!")
                player_damage = 0
            elif rival_turns_using_dive == 1:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " hid underwater!")
                player_damage = 0
            else:
                logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " attacks with " + str(activePkm_rival_attack))

            # Player is inmune if has used in the last turn an inmune attack
            if player_turns_using_dig == 2:
                rival_damage = 0
            if player_turns_using_fly == 2:
                rival_damage = 0
            if player_turns_using_dive == 2:
                rival_damage = 0

            if active_HP <= rival_damage:
                real_damage = active_HP
                damage_team += active_HP
                active_HP = 0
                # Cure rival if drain attack
                active_rival_HP, damage_rival_team = cure_with_drain_move(
                    attacker_name=rival_team[rival_selected_pos]["species"],
                    attack=activePkm_rival_attack,
                    real_damage=real_damage,
                    hp=active_rival_HP,
                    total_damage=damage_rival_team,
                    drain_attacks=drain_attacks,
                    logs=logs,
                    verbose=verbose
                )

                if player_uses_hyperbeam:
                    player_must_recharge_HB = False
                if rival_uses_hyperbeam:
                    rival_must_recharge_HB = True

            else:
                real_damage = rival_damage
                damage_team += rival_damage
                active_HP -= rival_damage
                # Cure rival if drain attack
                active_rival_HP, damage_rival_team = cure_with_drain_move(
                    attacker_name=rival_team[rival_selected_pos]["species"],
                    attack=activePkm_rival_attack,
                    real_damage=real_damage,
                    hp=active_rival_HP,
                    total_damage=damage_rival_team,
                    drain_attacks=drain_attacks,
                    logs=logs,
                    verbose=verbose
                )
                # Player attacks back
                if player_must_recharge_HB:
                    logs.append("PLAYER " + activePkm["species"] + " must recharge!")
                elif player_turns_using_sb == 1:
                    logs.append("PLAYER " + activePkm["species"] + " took in sunlight!")
                elif player_turns_using_dig == 1:
                    logs.append("PLAYER " + activePkm["species"] + " dug a hole!")
                elif player_turns_using_fly == 1:
                    logs.append("PLAYER " + activePkm["species"] + " flew up high!")
                elif player_turns_using_dive == 1:
                    logs.append("PLAYER " + activePkm["species"] + " hid underwater!")
                else:
                    logs.append("PLAYER " + activePkm["species"] + " attacks with " + str(activePkm_attack))

                if active_rival_HP <= player_damage:
                    real_damage = active_rival_HP
                    damage_rival_team += active_rival_HP
                    active_rival_HP = 0
                    # Cure player if drain attack
                    active_HP, damage_team = cure_with_drain_move(
                        attacker_name=activePkm["species"],
                        attack=activePkm_attack,
                        real_damage=real_damage,
                        hp=active_HP,
                        total_damage=damage_team,
                        drain_attacks=drain_attacks,
                        logs=logs,
                        verbose=verbose
                    )

                    if player_uses_hyperbeam:
                        player_must_recharge_HB = True
                    if rival_uses_hyperbeam:
                        rival_must_recharge_HB = False

                else:
                    real_damage = player_damage
                    damage_rival_team += player_damage
                    active_rival_HP -= player_damage
                    # Cure player if drain attack
                    active_HP, damage_team = cure_with_drain_move(
                        attacker_name=activePkm["species"],
                        attack=activePkm_attack,
                        real_damage=real_damage,
                        hp=active_HP,
                        total_damage=damage_team,
                        drain_attacks=drain_attacks,
                        logs=logs,
                        verbose=verbose
                    )

                    if player_uses_hyperbeam:
                        player_must_recharge_HB = True
                    if rival_uses_hyperbeam:
                        rival_must_recharge_HB = True

        # NEXT TURN FLAGS
        if not player_uses_hyperbeam:
            player_must_recharge_HB = False
        if not rival_uses_hyperbeam:
            rival_must_recharge_HB = False
        if player_turns_using_sb > 1:
            player_turns_using_sb = 0
        if rival_turns_using_sb > 1:
            rival_turns_using_sb = 0
        # DIG
        if player_turns_using_dig > 1:
            player_turns_using_dig = 0
        if rival_turns_using_dig > 1:
            rival_turns_using_dig = 0

        # FLY
        if player_turns_using_fly > 1:
            player_turns_using_fly = 0
        if rival_turns_using_fly > 1:
            rival_turns_using_fly = 0

        # DIVE
        if player_turns_using_dive > 1:
            player_turns_using_dive = 0
        if rival_turns_using_dive > 1:
            rival_turns_using_dive = 0


        logs.append("PLAYER " + activePkm["species"] + " HP " + str(active_HP))
        logs.append("RIVAL " + rival_team[rival_selected_pos]["species"] + " HP " + str(active_rival_HP))
    
    player_wins = (damage_team < totalHP_team)

    if verbose:
        for log in logs:
            print(log)
    return (player_wins, damage_team, logs)

def calculate_fitness(individual:list, dataset, verbose: bool):
    '''
        individual: list
            - first element: list of int that reference pkmID of catched
    '''
    pkm_catched = individual[0]
    fitness_value = 0
    feasibility = True
    entire_logs = []

    teams = individual[1]
    for i in range(0, len(teams)):
        pkm_catched_previously = pkm_catched[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]]
        # Comprobar que el equipo utilizado ha sido atrapado, sino penalizar con + INF y dejar de calcular
        for pkm in teams[i]:
            if(pkm not in pkm_catched_previously):
                return (False, float('inf'), entire_logs)
       
        (player_wins, damage_team, logs) = simulate_battle(
                team=teams[i], 
                rival_team=TRAINERS[TRAINERS_ORDER[i]], 
                available_mt=AVAILABLE_MT_TRAINERS[TRAINERS_ORDER[i]],
                available_ev_obj=AVAILABLE_EVOLVE_OBJ_TRAINERS[TRAINERS_ORDER[i]], 
                dataset=dataset, 
                verbose=verbose
        )
        entire_logs.append(logs)
        if not player_wins:
            feasibility = False
            fitness_value += 10000
        else:
            fitness_value += damage_team

    return (feasibility, fitness_value, entire_logs)

def approximate_fitness(number_of_battles: 5, individual:list, dataset, verbose: bool):
    '''
        individual: list
            - first element: list of int that reference pkmID of catched
    '''
    pkm_catched = individual[0]
    fitness_value = 0
    feasibility = True
    entire_logs = []

    teams = individual[1]

    random_teams = random.sample(range(len(teams)), number_of_battles)
    pkm_defeated = 0

    for i in random_teams:
        pkm_catched_previously = pkm_catched[:PREVIOUS_ROUTES_TO_TRAINER[TRAINERS_ORDER[i]]]
        # Comprobar que el equipo utilizado ha sido atrapado, sino penalizar con + INF y dejar de calcular
        for pkm in teams[i]:
            if(pkm not in pkm_catched_previously):
                return (False, float('inf'), entire_logs)
        (player_wins, damage_team, logs) = simulate_battle(
                team=teams[i], 
                rival_team=TRAINERS[TRAINERS_ORDER[i]], 
                available_mt=AVAILABLE_MT_TRAINERS[TRAINERS_ORDER[i]],
                available_ev_obj=AVAILABLE_EVOLVE_OBJ_TRAINERS[TRAINERS_ORDER[i]], 
                dataset=dataset, 
                verbose=verbose
        )
        entire_logs += logs
        if not player_wins:
            feasibility = False
            fitness_value += 10000
        else:
            fitness_value += damage_team
        pkm_defeated += len(TRAINERS[TRAINERS_ORDER[i]])

    return (feasibility, int(fitness_value * (TOTAL_RIVAL_PKM/pkm_defeated)), entire_logs)


dataset = load_json_in_dataset()