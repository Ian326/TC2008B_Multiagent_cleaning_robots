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
    def __init__(self, id, model):
        super().__init__(id, model)
        self.capacity = 5
        self.load = 0 
        self.type = 1
        self.pos = (0, 0) #Este es el valor inicial, luego se cambia cuando se coloque el agente en el grid
    
    def step(self):
        self.attribute1 = rd.randrange(0,2)
    
    def move(self):
       possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
       rd.shuffle(possible_moves) #Obtener un movimiento al azar, ya sea arriba, abajo, derecha, izquierda o en las diagonales
       
       for px, py in possible_moves:
           next_pos = (self.pos[0] + px, self.pos[1] + py)
           if self.can_move(next_pos):
               self.model.grid.move_agent(self, next_pos)
               break
       
    def investigate_width(self):
        x, y = self.pos

class GameBoard(Model):
    def __init__(self, width, height, gameboard, robots_count):
        
        self.attribute2 = "hola"

        self.grid = MultiGrid(width, height, torus = True)
        self.schedule = RandomActivation(self)
        self.current_id = 0

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
                    
                    while(robots_count > 0 ):
                        
                        agent = Robot(self.next_id(), self)
                        self.grid.place_agent(agent, (x, y))
                        self.schedule.add(agent)
                        
                        robots_count -= 1

        #Last line of __init__
        self.datacollector = DataCollector(model_reporters={"Grid" : get_grid})

    def step(self):

        self.datacollector.collect(self)
        self.schedule.step()
        
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

MAX_GENERATIONS = 100

gameboard = open('./inputs/input1.txt').read()
gameboard = [item.split() for item in gameboard.split('\n')[:-1]]
gameboard.pop(0)
print(gameboard)
GRID_SIZE_X = len(gameboard)
GRID_SIZE_Y = len(gameboard[0])
print(GRID_SIZE_X)
print(GRID_SIZE_Y) 

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