import re

def filtrar_generaciones(nombre_archivo):

    with open(nombre_archivo, 'r', encoding="utf-16") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if re.match(r'^(GENERATION:|Mejor fitness:)', linea):
                print(linea)

# Uso
filtrar_generaciones('./output2.txt')