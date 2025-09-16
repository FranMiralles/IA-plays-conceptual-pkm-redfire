import requests

data = {
    "genReq": 3,
    "attacker": {"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100},
    "defender": {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100},
    "move": "Flamethrower"
}

res = requests.post("http://localhost:3000/calc", json=data)
if res.status_code == 200:
    print(res.json()["damage"])
else:
    print("Error:", res.status_code, res.text)