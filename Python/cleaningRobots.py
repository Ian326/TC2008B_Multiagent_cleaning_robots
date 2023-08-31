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
    
    def __init__(self, id, model, pB_Pos):
        super().__init__(id, model)
        
        self.type = 1
    
        self.position = (0, 0) #Este es el valor inicial, luego se cambia cuando se coloque el agente en el grid
        
        self.model_width = 0
        self.model_height = 0
        
        self.capacity = 5
        self.load = 0
        
        #Guardar el mapa explorado por los robots
        
        # Las coordenadas iniciales y de la papelera se almacenan aquí
        self.initial_coordinates = (0, 0)
        self.paperBin_pos = pB_Pos
        self.steps = 0
    
    def step(self):
        if self.steps == 0:
            self.steps += 1
            return
        self.move()

    
    def move(self):
        
        # Definir las posibles direcciones de movimiento
        sp = self.pos
        possible_moves = [(sp[0], sp[1] + 1), (sp[0], sp[1] - 1), (sp[0]+ 1, sp[1]), (sp[0] - 1, sp[1]), (sp[0] + 1, sp[1] + 1), (sp[0] + 1, sp[1] - 1), (sp[0] - 1, sp[1] + 1), (sp[0] - 1, sp[1] - 1)]
        while(True):
            next_pos = rd.choice(possible_moves) #Obtener un movimiento al azar, ya sea arriba, abajo, derecha, izquierda o en las diagonales
            if self.can_move(next_pos):
                    self.model.grid.move_agent(self, next_pos)
                    self.update_internal_map()  # Actualizar el mapa interno después de moverse
                    break


    def can_move(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False
        # Verificar si hay algún otro robot en la celda de destino
        return not any(agent.type == 1 or agent.type == 3 for agent in self.model.grid.get_cell_list_contents([pos]))
    
    def update_internal_map(self):
        # Obtener las celdas circundantes
        cell_content = self.model.grid.get_cell_list_contents(self.pos)
        litter = 0
        for agent in cell_content:
            # Actualizar el mapa interno
            if agent != 1:
                if agent.type == 2:
                    litter += 1
                    self.model.robots_internal_map[self.pos[0]][self.pos[1]] = str(litter)
                if agent.type == 4:
                    self.model.robots_internal_map[self.pos[0]][self.pos[1]] = 'P'
        litter = 0
        neighbors = self.model.grid.get_neighbors(self.pos, moore = True, include_center = False)

        for agent in neighbors:
            if agent.type == 3:
                self.model.robots_internal_map[agent.pos[0]][agent.pos[1]] = 'X'
        
        if self.model.robots_internal_map[self.pos[0]][self.pos[1]] == '':
            self.model.robots_internal_map[self.pos[0]][self.pos[1]] = '0'


class GameBoard(Model):
    
    def __init__(self, width, height, gameboard, robots_count):
         
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        
        self.current_id = 0  # Initialize current_id before using it
        self.paperBin_pos = (0,0) #Initialize paperBin coords
        self.robots_internal_map = np.zeros((width, height), dtype=str)  # Iniciar el mapa interno vacio
        
        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):
                self.initialize_agents(gameboard, x, y, robots_count)

        self.datacollector = DataCollector(
            model_reporters={
                "GridRepr": lambda m: get_grid(m)[0],
                "GridColors": lambda m: get_grid(m)[1]
            })

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        print(self.robots_internal_map)

    def initialize_agents(self, gameboard, x, y, robots_count):
        cell = gameboard[x][y]
        if cell.isnumeric():
            litter_count = int(cell)
            while litter_count > 0:
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
            self.paperBin_pos = (x, y)
        elif cell == "S":
            self.initialize_robots(x, y, robots_count, self.paperBin_pos)
            robots_count = 0
    
    def initialize_robots(self, x, y, robots_count, pB_pos):
        while robots_count > 0:
            agent = Robot(self.next_id(), self, pB_pos)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            robots_count -= 1

        
def get_grid(model):
    grid_repr = np.zeros((model.grid.width, model.grid.height), dtype=object)
    grid_colors = np.zeros((model.grid.width, model.grid.height))
    for (content, (x, y)) in model.grid.coord_iter():
        has_paper_bin = False  # Variable para rastrear si la celda contiene una papelera
        for agent in content:
            if isinstance(agent, PaperBin):
                grid_repr[x][y] = "P"
                grid_colors[x][y] = 4
                has_paper_bin = True
            elif isinstance(agent, Litter):
                grid_repr[x][y] = str(int(grid_repr[x][y]) + 1) if grid_repr[x][y] else "1"
                grid_colors[x][y] = 2
            elif isinstance(agent, Wall):
                grid_repr[x][y] = "X"
                grid_colors[x][y] = 3
            elif isinstance(agent, Robot):
                if not has_paper_bin:  # Solo se coloca un robot si no hay una papelera en la celda
                    grid_repr[x][y] = "S"
                    grid_colors[x][y] = 1
            else:
                grid_repr[x][y] = "0"
                grid_colors[x][y] = 0
    return grid_repr, grid_colors



# --- Ejecución y visualización ---
ROBOTS = 5
MAX_GENERATIONS = 91
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
my_cmap = ListedColormap(['snow', 'slategray', 'thistle', 'black', 'skyblue'])

fig, axis = plt.subplots(figsize=(7, 7))

def animate(i):
    axis.clear()
    grid_data_repr = all_grid_repr.iloc[i]
    grid_data_colors = all_grid_colors.iloc[i]
    axis.imshow(grid_data_colors, cmap=my_cmap)
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            num = grid_data_repr[x][y]
            color = 'black'  # Color por defecto
            
            # Buscar si hay un robot o papelera en la celda
            robot = next((agent for agent in model.grid.get_cell_list_contents([(x, y)]) if isinstance(agent, Robot)), None)
            paper_bin = next((agent for agent in model.grid.get_cell_list_contents([(x, y)]) if isinstance(agent, PaperBin)), None)
            
            # Si hay una papelera y un robot en la celda, mostrar el robot encima
            if paper_bin and robot:
                num = 'S'
                color = 'white'  # El color del texto del robot será blanco para que sea visible sobre la papelera
                
            # Cambiar el color del texto en función del tipo de agente en la celda
            elif str(num).isdigit():
                color = 'black'
            else:
                color = 'white'
            
            if num != "0":
                axis.annotate(num, xy=(y, x), ha='center', va='center', color=color)

    axis.set_xlim(-0.5, GRID_SIZE_Y - 0.5)
    axis.set_ylim(-0.5, GRID_SIZE_X - 0.5)
    axis.invert_yaxis()


anim = animation.FuncAnimation(fig, animate, frames=MAX_GENERATIONS, repeat=False)
anim.save(filename="cleaningRobots.mp4")
