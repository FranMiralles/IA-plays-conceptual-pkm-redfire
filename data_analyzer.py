import re
import matplotlib.pyplot as plt


def filtrar_generaciones(nombre_archivo):
    fitness_values = []
    with open(nombre_archivo, 'r', encoding="utf-16") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if re.match(r'^(Mejor fitness:)', linea):
                fitness_values.append(float(linea.split(", ")[0].split(" ")[2]))
    return fitness_values

# Uso
fitness_values_5000 = filtrar_generaciones('./genetic_5000_1.txt')
fitness_values_1000 = filtrar_generaciones('./genetic_1000_1.txt')
fitness_values_500 = filtrar_generaciones('./genetic_500_5.txt')

plt.figure(figsize=(10,6))
plt.plot(range(1501), fitness_values_5000[:1501], color='#2E86AB', linewidth=1.5, linestyle='-', marker='o', markersize=3, markevery=50, label="Población de 5000")
plt.plot(range(1501), fitness_values_1000[:1501], color='#A23B72', linewidth=1.5, linestyle='-', marker='s', markersize=3, markevery=50, label="Población de 1000")
plt.plot(range(1501), fitness_values_500[:1501], color='#F18F01', linewidth=1.5, linestyle='-', marker='^', markersize=3, markevery=50, label="Población de 500")
plt.xlabel("Generación")
plt.ylabel("Fitness")
plt.title("Evolución del Fitness")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fitness_evolution_5000.png")
plt.show()