from route_data.routes import ROUTES, ROUTES_ORDER
import random


def assign_unique_pokemon(routes, order, all_none=False):
    used = set()           # para no repetir pokémon
    assignment = []        # resultado final

    for route in order:
        options = routes.get(route, [])
        # Filtrar los que aún no se han usado
        available = [pkm for pkm in options if pkm not in used]
        if all_none:
            available = []

        if available:
            chosen = random.choice(available)  # elegir aleatoriamente
            used.add(chosen)
        else:
            chosen = None  # no queda ninguno disponible

        assignment.append(chosen)

    return assignment

result = assign_unique_pokemon(ROUTES, ROUTES_ORDER, all_none=False)
print(result)

INDIVIDUAL = [
        result,
        [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ]
]