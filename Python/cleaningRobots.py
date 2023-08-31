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
    
    def __init__(self, id, model):
        super().__init__(id, model)
        
        self.type = 1
    
        self.position = (0, 0) #Este es el valor inicial, luego se cambia cuando se coloque el agente en el grid
        
        self.model_width = 0
        self.model_height = 0
        
        self.capacity = 5
        self.load = 0

        self.on_paper_bin = False  # Indica si el robot se encuentra sobre una papelera
        
        self.explored_map = {} #Guardar el mapa explorado por los robots
        self.internal_map = {}  # Iniciar el mapa interno
        # Las coordenadas iniciales y de la papelera se almacenan aquí
        self.initial_coordinates = (0, 0)
        self.paper_bin_coordinates = (0, 0)
        self.first_step = True
    
    def step(self):
        if self.first_step:
            self.first_step = False
            return
        self.move()
        self.register_current_position()

        
        #     self.move()  # Moverse aleatoriamente
    
    def move(self):
        
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
        self.on_paper_bin = any(isinstance(agent, PaperBin) for agent in self.model.grid.get_cell_list_contents([self.pos]))

    def can_move(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False
        # Verificar si hay algún otro robot en la celda de destino
        return not any(agent.type == 1 or agent.type == 3 for agent in self.model.grid.get_cell_list_contents([pos]))
    
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

    def initialize_robots(self, x, y, robots_count):
        while robots_count > 0:
            agent = Robot(self.next_id(), self)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            robots_count -= 1




class GameBoard(Model):
    
    def __init__(self, width, height, gameboard, robots_count):
         
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        
        self.current_id = 0  # Initialize current_id before using it

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
        #elif cell == "S":
        #    self.initialize_robots(x, y, robots_count)
        #    robots_count = 0
    
    def place_robots_at_s(self, gameboard, robots_count):
        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):
                cell = gameboard[x][y]
                if cell == "S":
                    self.initialize_robots(x, y, robots_count)
                    return
    
    def next_id(self):
        self.current_id += 1
        return self.current_id
    
    def initialize_robots(self, x, y, robots_count):
        while robots_count > 0:
            agent = Robot(self.next_id(), self)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            robots_count -= 1

        
def get_grid(model):
    grid_repr = np.zeros((model.grid.width, model.grid.height), dtype=object)
    grid_colors = np.zeros((model.grid.width, model.grid.height))
    for (content, (x, y)) in model.grid.coord_iter():
        is_paper_bin = False  # Variable para rastrear si la celda contiene una papelera
        for agent in content:
            if isinstance(agent, PaperBin):
                is_paper_bin = True  # Se encontró una papelera en la celda
                grid_repr[x][y] = "P"
                grid_colors[x][y] = 4
            elif isinstance(agent, Litter):
                grid_repr[x][y] = str(int(grid_repr[x][y]) + 1) if grid_repr[x][y] else "1"
                grid_colors[x][y] = 2
            elif isinstance(agent, Wall):
                grid_repr[x][y] = "X"
                grid_colors[x][y] = 3
            elif isinstance(agent, Robot):
                if not is_paper_bin:  # Solo se coloca un robot si no hay una papelera en la celda
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
model.place_robots_at_s(gameboard, ROBOTS)

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
