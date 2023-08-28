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

class Robot(Agent):
    def __init__(self, id, model, robot_capacity = 5):
        super().__init__(id, model)
        self.capacity = robot_capacity
        self.load = 0 
        self.attribute1 = rd.randrange(0,2)
    

    def step(self):
        self.attribute1 = rd.randrange(0,2)

class GameBoard(Model):
    def __init__(self, width, height):
        self.attribute2 = "hola"

        self.grid = MultiGrid(width, height, torus = True)
        self.schedule = RandomActivation(self)
        self.current_id = 0

        for _ in range(5):
      
            x = rd.randrange(width)
            y = rd.randrange(height)
            
            if self.grid.is_cell_empty((x, y)) == True:
                agent = Robot(self.next_id(), self, 1)
                
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        #Last line of __init__
        self.datacollector = DataCollector(model_reporters={"Grid" : get_grid})

    def step(self):

        self.datacollector.collect(self)
        self.schedule.step()
        
def get_grid(model):

  grid = np.zeros((model.grid.width, model.grid.height))
  
  for (content, (x, y)) in model.grid.coord_iter():
    
    if content: 
        grid[x][y] = content.attribute1
        

  return grid

#================================Global Params=====================


    
GRID_SIZE_X = 100
GRID_SIZE_Y = 100
MAX_GENERATIONS = 100

model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y)

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