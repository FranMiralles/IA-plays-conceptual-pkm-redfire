import re
import matplotlib.pyplot as plt


def filtrar_f_local(nombre_archivo):
    fitness_values = []
    with open(nombre_archivo, 'r', encoding="utf-16") as archivo:
        for linea in archivo:
            linea = linea.strip()
            # Buscar líneas que contengan "f_local="
            if "f_global_best=" in linea:
                # Extraer el valor después de "f_local="
                match = re.search(r'f_global_best=([\d.]+)', linea)
                if match:
                    fitness_values.append(float(match.group(1)))
            else:
                match = re.search(r'f_best=([\d.]+)', linea)
                if match:
                    fitness_values.append(float(match.group(1)))
    return fitness_values

# Uso
best1 = filtrar_f_local('./simulated_2_bestAG_1.txt')
best2 = filtrar_f_local('./simulated_4_bestAG_1.txt')
best3 = filtrar_f_local('./simulated_bestAG_1.txt')
start1 = filtrar_f_local('./simulated_4_startAG_1.txt')
start2 = filtrar_f_local('./simulated_startAG_1.txt')
half1 = filtrar_f_local('./simulated_halfAG_2.txt')

# Agrupar todas las listas
listas = [best1, best2, best3, start1, start2, half1]

# Calcular la longitud máxima
max_len = max(len(lst) for lst in listas)

# Rellenar las listas más cortas repitiendo su último valor
listas_rellenadas = []
for lst in listas:
    if len(lst) < max_len:
        lst_rellena = lst + [lst[-1]] * (max_len - len(lst))
    else:
        lst_rellena = lst
    listas_rellenadas.append(lst_rellena)

# Asignar nombres más claros (según tu gráfico original)
best1, best2, best3, start1, start2, half1 = listas_rellenadas

plt.plot(range(50,max_len), best1[50:max_len], color='#2E86AB', linewidth=2, linestyle='-', marker='o', markersize=3, markevery=50, label="Temperatura 200, mejor individuo AG")
plt.plot(range(50,max_len), best2[50:max_len], color='#A23B72', linewidth=2, linestyle='-', marker='s', markersize=3, markevery=50, label="Temperatura 100, mejor individuo AG")
plt.plot(range(50,max_len), best3[50:max_len], color="#59DB03", linewidth=2, linestyle='-', marker='^', markersize=3, markevery=50, label="Temperatura 450, mejor individuo AG")
plt.plot(range(50,max_len), start1[50:max_len], color='#F18F01', linewidth=2, linestyle='-', marker='^', markersize=3, markevery=50, label="Temperatura 6000, individuo aleatorio")
plt.plot(range(50,max_len), start2[50:max_len], color="#C00D0D", linewidth=2, linestyle='-', marker='^', markersize=3, markevery=50, label="Temperatura 3000, individuo aleatorio")
plt.plot(range(50,max_len), half1[50:max_len], color="#F5F123", linewidth=2, linestyle='-', marker='^', markersize=3, markevery=50, label="Temperatura 3000, individuo medio")

plt.xlabel("Generación")
plt.ylabel("Fitness (f_local)")
plt.title("Evolución del Mejor Fitness Global")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fitness_evolution_f_local.png")
plt.show()