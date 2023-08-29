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
        
        self.capacity = 5
        self.load = 0
    
    
    def step(self):
        
        if self.role == "marco":
            if not self.model_width:
                self.investigate_width()
            
            else:
                self.random_move()
        
        if self.role == "polo":
            if not self.model_height:
                self.investigate_height()
            
            else:
                self.random_move()
    
    
    def move(self):
        
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        rd.shuffle(possible_moves) #Obtener un movimiento al azar, ya sea arriba, abajo, derecha, izquierda o en las diagonales
        
        for px, py in possible_moves:
            
            next_pos = (self.position[0] + px, self.position[1] + py)
            
            if self.can_move(next_pos):
                self.model.grid.move_agent(self, next_pos)
                break
    
    
    def investigate_width(self):
        
        next_pos = (self.position[0], self.position[1] + 1)
        diag_up = (self.position[0] - 1, self.position[1] +1)
        diag_down = (self.position[0] + 1, self.position[1] + 1)
        
        if self.can_move(next_pos):
            self.model.grid.move_agent(self, next_pos)
        elif self.can_move(diag_up):
            self.model.grid.move_agent(self, diag_up)
        elif self.can_move(diag_down):
            self.model.grid.move_agent(self, diag_down)
        else:
            # Buscar el camino más corto
            up_pos = (self.position[0] - 1, self.position[1])
            if self.can_move(up_pos):
                self.model.grid.move_agent(self, up_pos)
    
    
    def investigate_height(self):
        
        next_pos = (self.position[0] + 1, self.position[1])
        diag_left = (self.position[0] + 1, self.position[1] - 1)
        diag_right = (self.position[0] + 1, self.position[1] + 1)

        if self.can_move(next_pos):
            self.model.grid.move_agent(self, next_pos)
        elif self.can_move(diag_left):
            self.model.grid.move_agent(self, diag_left)
        elif self.can_move(diag_right):
            self.model.grid.move_agent(self, diag_right)
        else:
            # Buscar el camino más corto
            right_pos = (self.position[0] + 1, self.position[1])
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

        #Last line of __init__
        self.datacollector = DataCollector(model_reporters={"Grid" : get_grid})


    def step(self):

        self.datacollector.collect(self)
        self.schedule.step()
    
    
    def createRobot(self, role, x, y):
        
        agent = Robot(self.next_id(), self, role)
        
        self.grid.place_agent(agent, (x, y))
        self.schedule.add(agent)
    


def get_grid(model):

  grid = np.zeros((model.grid.width, model.grid.height))
  
  for (content, (x, y)) in model.grid.coord_iter():
    
    if content:
        cell_type = 0
        for agent in content:
            cell_type = agent.type
        grid[x][y] = cell_type

  return grid

#================================Global Params=====================

ROBOTS = 5

MAX_GENERATIONS = 1

gameboard = open('./inputs/input1.txt').read()
gameboard = [item.split() for item in gameboard.split('\n')[:-1]]
gameboard.pop(0)

GRID_SIZE_X = len(gameboard)
GRID_SIZE_Y = len(gameboard[0])

model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y, gameboard, ROBOTS)

for i in range(MAX_GENERATIONS):

  model.step()
  
all_grid = model.datacollector.get_model_vars_dataframe()

fig, axis = plt.subplots(figsize=(7,7))

axis.set_xticks([])
axis.set_yticks([])

patch = plt.imshow(all_grid.iloc[0][0], cmap=plt.cm.nipy_spectral)

def animate(i):

  patch.set_data(all_grid.iloc[i][0])

anim = animation.FuncAnimation(fig, animate, frames = MAX_GENERATIONS)

anim
anim.save(filename="cleaningRobots.mp4")