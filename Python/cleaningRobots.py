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
from matplotlib.colors import ListedColormap

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
    
    def __init__(self, id, model, robot_type):
        super().__init__(id, model)
        
        self.type = 1
        
        self.role = robot_type
        self.position = (0, 0) #Este es el valor inicial, luego se cambia cuando se coloque el agente en el grid
        
        self.model_width = 0
        self.model_height = 0
        
        self.find_width = False
        self.find_height = False
        
        self.capacity = 5
        self.load = 0
    
    
    def step(self):
        
        if self.role == "marco":
            if not self.find_width:
                self.investigate_width()
    
        
        if self.role == "polo":
            if not self.find_height:
                self.investigate_height()

    
    
    def move(self):
        
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        rd.shuffle(possible_moves) #Obtener un movimiento al azar, ya sea arriba, abajo, derecha, izquierda o en las diagonales
        
        for px, py in possible_moves:
            
            next_pos = (self.position[0] + px, self.position[1] + py)
            
            if self.can_move(next_pos):
                self.model.grid.move_agent(self, next_pos)
                break
    
    
    def investigate_width(self):
        
        next_pos = (self.pos[0], self.pos[1] + 1)
        diag_up = (self.pos[0] - 1, self.pos[1] +1)
        diag_down = (self.pos[0] + 1, self.pos[1] + 1)
        
        cells = self.model.grid.get_neighborhood(self.pos,
                                        moore = True,
                                        include_center = False)
        
        if self.can_move(next_pos):
            self.model.grid.move_agent(self, next_pos)
        elif self.can_move(diag_up):
            self.model.grid.move_agent(self, diag_up)
        elif self.can_move(diag_down):
            self.model.grid.move_agent(self, diag_down)
        elif len(cells) < 8:
            self.find_width = True
        else:
            # Buscar el camino más corto
            up_pos = (self.pos[0] - 1, self.pos[1])
            if self.can_move(up_pos):
                self.model.grid.move_agent(self, up_pos)
    
    
    def investigate_height(self):
        
        next_pos = (self.pos[0] + 1, self.pos[1])
        diag_left = (self.pos[0] + 1, self.pos[1] - 1)
        diag_right = (self.pos[0] + 1, self.pos[1] + 1)

        cells = self.model.grid.get_neighborhood(self.pos,
                                        moore = True,
                                        include_center = False)
            
        if self.can_move(next_pos):
            self.model.grid.move_agent(self, next_pos)
        elif self.can_move(diag_left):
            self.model.grid.move_agent(self, diag_left)
        elif self.can_move(diag_right):
            self.model.grid.move_agent(self, diag_right)
        elif len(cells) < 8:
            self.find_height = True
        else:
            # Buscar el camino más corto
            right_pos = (self.pos[0] + 1, self.pos[1])
            if self.can_move(right_pos):
                self.model.grid.move_agent(self, right_pos)
    
    def can_move(self, pos):
        
        if self.model.grid.out_of_bounds(pos):
            return False
        
        else:
            
            for content in self.model.grid.get_cell_list_contents((pos)):
                if content.type == 1 or content.type == 3:
                    return False
                
            return True
                
        

class GameBoard(Model):
    
    def __init__(self, width, height, gameboard, robots_count):
         
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        self.current_id = 0
        
        self.robot_roles = {"marco":1, "polo":1, "mo": 3}

        self.robot_roles = {"marco":1, "polo":1, "mo": 3}

        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):

                cell = gameboard[x][y]

                if cell.isnumeric():
                    
                    litter_count = int(cell)

                    while(litter_count > 0):
                        
                        agent = Litter(self.next_id(), self)
                        
                        self.grid.place_agent(agent, (x, y))
                        self.schedule.add(agent)
                        
                        litter_count -= 1

                elif cell == "X":

                    agent = Wall(self.next_id(), self)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)

                elif cell == "P":

                    agent = PaperBin(self.next_id(), self)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)

                elif cell == "S":
                    
                    while(robots_count):
                        
                        if self.robot_roles["marco"] > 0:
                            
                            self.createRobot("marco", x, y)
                            self.robot_roles["marco"] -= 1
                        
                        elif self.robot_roles["polo"] > 0:
                            
                            self.createRobot("polo", x, y)
                            self.robot_roles["polo"] -= 1
                        
                        elif self.robot_roles["mo"] > 0:
                            
                            self.createRobot("mo", x, y)
                            self.robot_roles["mo"] -= 1
                        
                        robots_count -= 1

        self.datacollector = DataCollector(
            model_reporters={
                "GridRepr": lambda m: get_grid(m)[0],
                "GridColors": lambda m: get_grid(m)[1]
            })

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        
    def createRobot(self, role, x, y):
        
        agent = Robot(self.next_id(), self, role)
        
        self.grid.place_agent(agent, (x, y))
        self.schedule.add(agent)
        
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
ROBOTS = 5
MAX_GENERATIONS = 60
step_count = 0

gameboard = [line.split() for line in open('./inputs/input1.txt').read().splitlines() if line][1:]
GRID_SIZE_X = len(gameboard)
GRID_SIZE_Y = len(gameboard[0])
model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y, gameboard, ROBOTS)

for i in range(MAX_GENERATIONS):

  step_count += 1
  model.step()

all_grid_repr = model.datacollector.get_model_vars_dataframe()["GridRepr"]
all_grid_colors = model.datacollector.get_model_vars_dataframe()["GridColors"]

#COLORES OCUPADOS
my_cmap = ListedColormap(['pink', 'blue', 'pink', 'red', 'black'])

fig, axis = plt.subplots(figsize=(7, 7))
axis.set_xticks([])
axis.set_yticks([])
patch = plt.imshow(all_grid_colors.iloc[0], cmap=my_cmap)

def animate(i):
    axis.clear()
    grid_data_repr = all_grid_repr.iloc[i]
    grid_data_colors = all_grid_colors.iloc[i]
    axis.imshow(grid_data_colors, cmap=my_cmap)
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



anim = animation.FuncAnimation(fig, animate, frames=len(all_grid_repr), repeat=False)
anim.save(filename="cleaningRobots.mp4")
