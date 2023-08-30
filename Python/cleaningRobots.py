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
        
        self.explored_map = {} #Guardar el mapa explorado por los robots
        self.internal_map = {}  # Iniciar el mapa interno
        # Las coordenadas iniciales y de la papelera se almacenan aquí
        self.initial_coordinates = (0, 0)
        self.paper_bin_coordinates = (0, 0)
    
    
    def step(self):
        self.register_current_position()
        
        if self.role == "marco":
            if not self.find_width:
                self.investigate_width()
            else:
                self.move() #Si ya terminó de investigar, se mueve aleatoriamente 
    
        
        if self.role == "polo":
            if not self.find_height:
                self.investigate_height()
            else:
                self.move() #Si ya terminó de investigar, se mueve aleatoriamente 
        
        if self.role == "mo":
            self.move()  # Moverse aleatoriamente al iniciar la simulación
    
    def move(self):
        
        # Verificar si el agente ya está en la programación (schedule)
        # if self not in self.model.schedule.agents:
        #     # Si no está en la programación, agregarlo
        #     self.model.schedule.add(self)
        
        # Definir las posibles direcciones de movimiento
        sp = self.pos
        possible_moves = [(sp[0], sp[1] + 1), (sp[0], sp[1] - 1), (sp[0]+ 1, sp[1]), (sp[0] - 1, sp[1]), (sp[0] + 1, sp[1] + 1), (sp[0] + 1, sp[1] - 1), (sp[0] - 1, sp[1] + 1), (sp[0] - 1, sp[1] - 1)]
        rd.shuffle(possible_moves) #Obtener un movimiento al azar, ya sea arriba, abajo, derecha, izquierda o en las diagonales
            
        # Recorrer las direcciones posibles
        for next_pos in possible_moves:
            if self.can_move(next_pos):
                self.model.grid.move_agent(self, next_pos)
                break
        
        self.update_internal_map()  # Actualizar el mapa interno después de moverse
    
    
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
        self.update_internal_map() # Actualizar el mapa interno después de investigar el ancho
    
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
        
        self.update_internal_map()  # Actualizar el mapa interno después de investigar el alto
    
    def can_move(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False
        # Usando 'any' para simplificar la condición
        return not any(agent.type in [1, 3] for agent in self.model.grid.get_cell_list_contents([pos]))
    
    def register_current_position(self):
        x, y = self.position
        cell_content = self.model.grid.get_cell_list_contents([self.position])
        for content in cell_content:
            # Usamos el mapa interno en lugar de un mapa compartido
            self.internal_map[(x, y)] = str(content.type)
    
    def update_internal_map(self):
        # Obtener las celdas circundantes
        neighbors = self.model.grid.get_neighborhood(
            self.position, moore=True, include_center=False
        )
        
        for neighbor in neighbors:
            cell_content = self.model.grid.get_cell_list_contents([neighbor])
            # Inicializar con un valor por defecto para celdas vacías
            self.internal_map[neighbor] = '0'
            for content in cell_content:
                # Actualizar el mapa interno
                self.internal_map[neighbor] = str(content.type)


class GameBoard(Model):
    
    def __init__(self, width, height, gameboard, robots_count):
         
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        self.current_id = 0

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
        
    def createRobot(self, role, x, y):
        
        agent = Robot(self.next_id(), self, role)
        
        self.grid.place_agent(agent, (x, y))
        self.schedule.add(agent)
        
    def initialize_agents(self, gameboard, x, y, robots_count):
        # Inicializa los agentes
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
            self.initialize_robots(x, y, robots_count)
            
    def initialize_robots(self, x, y, robots_count):
        while robots_count > 0:
            agent = Robot(self.next_id(), self, "marco")  # Cambiar "marco" según lo necesario
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            robots_count -= 1

    def next_id(self):
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



anim = animation.FuncAnimation(fig, animate, frames=len(all_grid_repr), repeat=False)
anim.save(filename="cleaningRobots.mp4")
