import requests
import time

data = {
    "genReq": 3,
    "attacker": {"species": "Salamence", "ability": "Intimidate", "item": "Choice Band", "level": 100},
    "defender": {"species": "Skarmory", "ability": "Sturdy", "item": "Choice Band", "level": 100},
    "move": "Flamethrower"
}

start = time.perf_counter()
res = requests.post("http://localhost:3000/calc", json=data)
end = time.perf_counter()

elapsed_seconds = end - start
print(f"Status: {res.status_code}, tiempo total: {elapsed_seconds:.6f} s")

if res.status_code == 200:
    print(res.json()["damage"])
else:
    print("Error:", res.status_code, res.text)