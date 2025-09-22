import requests
import statistics
import json
from route_data.trainers import TRAINERS

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
    moves = cargar_json("./pkm_data/moves.json")
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
    lostHP = round(statistics.median(res.json()["damage"]) / maxHP, 3)
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


def simulate_battle(team:list, rival_team:list, dataset:object):
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
    activePkmID = team[0]
    level_cap = select_level_cap(rival_team)
    # Define activePkm
    activePkm = {
        "species": dataset["pkdex"][str(activePkmID)]["name"],
        "level": level_cap,
        "ability": dataset["pkdex"][str(activePkmID)]["abilities"],
        "speed": calculate_speed(dataset["pkdex"][str(activePkmID)]["speed"], level_cap - 13)
    }
    # Define possibles moves for activePkm
    possibles_moves_with_priorities = [(dataset["moves"][moveID]["name"], dataset["moves"][moveID]["priority"]) for moveID in dataset["pkdex"][str(activePkmID)]["moves"] if dataset["pkdex"][str(activePkmID)]["moves"][moveID]['level'] <= level_cap]
    activePkm["moves"] = [move_name for (move_name, _) in possibles_moves_with_priorities]

    activePkm_rival = {
        "species": rival_team[0]["name"],
        "level": rival_team[0]["level"],
        "ability": rival_team[0]["ability"],
        "speed": rival_team[0]["speed"],
        "moves": rival_team[0]["moves"]
    }

    totalHP_team = len(rival_team)
    playerHP_team = totalHP_team
    rivalHP_team = totalHP_team

    turn = 1

    while playerHP_team > 0 and rivalHP_team > 0:
        # Loop that ends if one of the teams runs out of pkm
        print("PKM ACTIVO")
        print(activePkm)
        print("PKM RIVAL ACTIVO")
        print(activePkm_rival)
        # Choose wich move selects each pkm
        activePkm_attack = select_best_attack(activePkm, activePkm_rival)
        activePkm_rival_attack = select_best_attack(activePkm_rival, activePkm)
        print(activePkm_attack)
        print(activePkm_rival_attack)
        playerHP_team = 0

        turn += 1

    '''
    print(dataset["pkdex"][str(activePkmID)])
    
    dataset["pkdex"][str(activePkmID)]
    print(dataset["moves"][str(attackID)])
    print(dataset["pkdex"][str(activePkmID)]["speed"])
    print(calculate_speed(dataset["pkdex"][str(activePkmID)]["speed"], 55))
    print(rival_team)
    print(select_level_cap(rival_team))
    '''


damage = deal_damage({"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100, "iv": {"as": 31}}, 
            {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100},
            "Flamethrower")


damage = select_best_attack({"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100, "moves": ["tackle", "flamethrower"]}, 
            {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100}
    )


dataset = load_json_in_dataset()


print("SIMULATE BATTLE")
simulate_battle([1, 4],TRAINERS["GYM_PLATEADA"], dataset=dataset)
