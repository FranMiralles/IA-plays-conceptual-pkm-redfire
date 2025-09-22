import requests
import statistics
import json
from route_data.trainers import TRAINERS


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
                    - item: str
                    - level: int
        defender: obj
                    - species: str
                    - ability: str
                    - item: str
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
                    - item: str
                    - level: int
                    - moves: list(str)
        defender: obj
                    - species: str
                    - ability: str
                    - item: str
                    - level: int
    '''
    biggestDamage = 0
    for move in attacker["moves"]:
        lostHP = deal_damage(
            {
                "species": attacker["species"],
                "ability": attacker["ability"],
                "item": attacker["item"],
                "level": attacker["level"],
            }
        ,target, move=move)
        print(move, " : ",lostHP)
        if(lostHP > biggestDamage):
            biggestDamage = lostHP
    return biggestDamage


def simulate_battle(actions:list, rival_team:object, dataset:object):
    '''
    At least actions has length 1, and cannot start with a change (-1, idPkm)
        actions: list of tuples
                    - (int idPkm, int idAttack): idPkm performs idAttack to current pkm from rival_team
                    - (-1, idPkm): active pkm changes to idPkm
        rival_team: object (keys=pkms)
                    - pkm: object (key=name)
                            - level: int
                            - ability: string
                            - moves: list
        dataset: object
                    - evolutions.json to object
                    - moves.json to object
                    - pkdex.json to object
    '''
    (activePkmID, attackID) = actions[0]
    print(dataset["pkdex"][str(activePkmID)])
    dataset["pkdex"][str(activePkmID)]
    print(dataset["moves"][str(attackID)])
    print(dataset["pkdex"][str(activePkmID)]["speed"])
    print(calculate_speed(dataset["pkdex"][str(activePkmID)]["speed"], 55))


damage = deal_damage({"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100, "iv": {"as": 31}}, 
            {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100},
            "Flamethrower")

print(damage)

damage = select_best_attack({"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100, "moves": ["tackle", "flamethrower"]}, 
            {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100}
            )

print(damage)

dataset = load_json_in_dataset()


print("SIMULATE BATTLE")
simulate_battle([(1,1)],TRAINERS["GYM_PLATEADA"], dataset=dataset)
