import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

# Leer el archivo de texto y convertirlo en una matriz
with open('input1.txt', 'r') as file:
    lines = file.readlines()

    # Leer dimensiones y ajustar líneas
    rows, cols = map(int, lines[0].strip().split())
    matrix = [line.strip().split() for line in lines[1:rows+1]]

# Convertir los valores a números o cadenas según el símbolo
def parse_symbol(symbol):
    if symbol.isdigit():
        return int(symbol)
    else:
        return symbol

matrix = [[parse_symbol(symbol) for symbol in row] for row in matrix]

# Crear una figura y ejes de Matplotlib
fig, ax = plt.subplots()

# Define un mapa de colores personalizado
colors = [(0.53, 0.81, 0.92)]  # color para el valor 0 (blanco)
cmap = ListedColormap(colors)
cmap.set_over(color='red')    # Para 'X'
cmap.set_under(color='blue')  # Para 'P'
cmap.set_bad(color='green')   # Para 'S'

# Inicializa la matriz de colores
color_matrix = np.zeros((len(matrix), len(matrix[0])), dtype=float)

# Llenar color_matrix basado en matrix
for row in range(len(matrix)):
    for col in range(len(matrix[row])):
        if matrix[row][col] == 'X':
            color_matrix[row][col] = 10
        elif matrix[row][col] == 'P':
            color_matrix[row][col] = -1
        elif matrix[row][col] == 'S':
            color_matrix[row][col] = np.nan
        else:
            color_matrix[row][col] = matrix[row][col]

# Función para animar cada frame del vídeo
def animate(i):
    ax.clear()
    ax.imshow(color_matrix, cmap=cmap, vmin=0, vmax=9)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if isinstance(matrix[row][col], int):
                color = 'white' if matrix[row][col] in range(4, 10) else 'black'
                ax.text(col, row, str(matrix[row][col]), ha='center', va='center', color=color)
            else:
                ax.text(col, row, matrix[row][col], ha='center', va='center', color='white')
    ax.set_xticks(np.arange(len(matrix[0])))
    ax.set_yticks(np.arange(len(matrix)))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
    ax.set_xticks(np.arange(-.5, len(matrix[0]), 1))
    ax.set_yticks(np.arange(-.5, len(matrix), 1))

# Crear animación usando la función animate
anim = animation.FuncAnimation(fig, animate, frames=100, repeat=True)

# Guardar el vídeo
anim.save(filename="Mapa.mp4")

plt.close()  # cerrar la figura al finalizar




