# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
from mesa import Agent, Model

# Debido a que necesitamos que existan varios agents por celda, elegimos ''MultiGrid''
# En la primera iteración.
from mesa.space import MultiGrid

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al mismo tiempo''.
from mesa.time import RandomActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector

# matplotlib lo usaremos crear una animación de cada uno de los pasos del modelo.

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import random as rd

# --- Definición de Agentes ---

class Litter(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.type = 2

class Wall(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.type = 3

class PaperBin(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.type = 4

class Robot(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.capacity = 5
        self.load = 0
        self.type = 1

    def step(self):
        self.attribute1 = rd.randrange(0,2)
        self.move()
        # TODO: Agregar otros comportamientos si es necesario

    def move(self):
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        rd.shuffle(possible_moves)
        for px, py in possible_moves:
            next_pos = (self.pos[0] + px, self.pos[1] + py)
            if self.can_move(next_pos):
                self.model.grid.move_agent(self, next_pos)
                break

    def can_move(self, pos):
        # TODO: Agregar lógica para determinar si el Robot puede moverse a la posición 'pos'
        pass


# --- Definición del Modelo ---

class GameBoard(Model):
    def __init__(self, width, height, gameboard, robots_count):
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.current_id = 0

        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):
                cell = gameboard[x][y]
                if cell.isnumeric():
                    litter_count = int(cell)
                    for _ in range(litter_count):
                        agent = Litter(self.next_id(True), self)
                        self.grid.place_agent(agent, (x, y))
                        self.schedule.add(agent)
                elif cell == "X":
                    agent = Wall(self.next_id(True), self)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)
                elif cell == "P":
                    agent = PaperBin(self.next_id(True), self)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)
                elif cell == "S":
                    for _ in range(robots_count):
                        agent = Robot(self.next_id(True), self)
                        self.grid.place_agent(agent, (x, y))
                        self.schedule.add(agent)

        self.datacollector = DataCollector(
            model_reporters={
                "GridRepr": lambda m: get_grid(m)[0],
                "GridColors": lambda m: get_grid(m)[1]
            })

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def next_id(self, increment=False):
        if increment:
            self.current_id += 1
        return self.current_id


def get_grid(model):
    grid_repr = np.zeros((model.grid.width, model.grid.height), dtype=object)
    grid_colors = np.zeros((model.grid.width, model.grid.height))
    for (content, (x, y)) in model.grid.coord_iter():
        for agent in content:
            if isinstance(agent, Litter):
                grid_repr[x][y] = str(int(grid_repr[x][y]) + 1) if grid_repr[x][y] else "1"
                grid_colors[x][y] = 2
            elif isinstance(agent, Wall):
                grid_repr[x][y] = "X"
                grid_colors[x][y] = 3
            elif isinstance(agent, PaperBin):
                grid_repr[x][y] = "P"
                grid_colors[x][y] = 4
            elif isinstance(agent, Robot):
                grid_repr[x][y] = "S"
                grid_colors[x][y] = 1
            else:
                grid_repr[x][y] = "0"
                grid_colors[x][y] = 0
    return grid_repr, grid_colors


# --- Ejecución y visualización ---

gameboard = [line.split() for line in open('./inputs/input1.txt').read().splitlines() if line][1:]
GRID_SIZE_X = len(gameboard)
GRID_SIZE_Y = len(gameboard[0])
model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y, gameboard, 5)

for _ in range(100):
    model.step()

all_grid_repr = model.datacollector.get_model_vars_dataframe()["GridRepr"]
all_grid_colors = model.datacollector.get_model_vars_dataframe()["GridColors"]

fig, axis = plt.subplots(figsize=(7, 7))
axis.set_xticks([])
axis.set_yticks([])
patch = plt.imshow(all_grid_colors.iloc[0], cmap=plt.cm.nipy_spectral)

def animate(i):
    axis.clear()
    grid_data_repr = all_grid_repr.iloc[i]
    grid_data_colors = all_grid_colors.iloc[i]
    axis.imshow(grid_data_colors, cmap=plt.cm.nipy_spectral)
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            num = grid_data_repr[x][y]
            if num != "0":
                color = 'black' if str(num).isdigit() else 'white'
                axis.annotate(num, xy=(y, x), ha='center', va='center', color=color)

    axis.set_xlim(-0.5, GRID_SIZE_Y - 0.5)  # Ajuste de límites del eje X
    axis.set_ylim(-0.5, GRID_SIZE_X - 0.5)  # Ajuste de límites del eje Y
    axis.invert_yaxis()
    # axis.axis('off')  # Comentado temporalmente para ver los bordes



anim = animation.FuncAnimation(fig, animate, frames=100, repeat=False)
anim.save(filename="cleaningRobots.mp4")
