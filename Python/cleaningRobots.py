from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
from matplotlib.colors import ListedColormap
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128
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
        self.type = 1
        self.state = "explore_rand"
        self.capacity = 5
        self.load = 0
        self.queuedMovements = []
        self.targetCell = ()
        self.targetCell_aux = ()
        self.alreadyCleaned = False
    def step(self):
        if self.model.current_step <= self.model.cellsCount:
            if self.model.current_step >= 1:
                self.explore_random()
        elif self.model.exploredCellsCount != self.model.cellsCount:
                self.state = "explore_missing"
                self.explore_missing()
        else:
            if self.state == "explore_missing":
                self.state = "cleaning"
                self.targetCell = ()
            if not self.targetCell:
                self.assign_Litter()
            else:
                if (self.pos == self.targetCell and 
                    self.pos != self.model.paperBin_pos and not 
                    self.alreadyCleaned):
                    self.queuedMovements = []
                    self.pickUpLitter()
                    return
                if (self.alreadyCleaned and self.pos != self.model.paperBin_pos):
                    self.moveToPaperBin()
                    if(self.alreadyCleaned and self.pos == self.model.paperBin_pos):
                        self.disposePaperBin()
                        return
                    return
                if(self.alreadyCleaned and self.pos == self.model.paperBin_pos):
                    self.disposePaperBin()
                self.move()
    def can_move(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False
        return not any(agent.type == 1 or 
                       agent.type == 3 
                       for agent in self.model.grid.get_cell_list_contents([pos]))
    def explore_random(self):
        sp = self.pos
        possible_moves = [(sp[0], sp[1] + 1), (sp[0], sp[1] - 1), 
                          (sp[0]+ 1, sp[1]), (sp[0] - 1, sp[1]), 
                          (sp[0] + 1, sp[1] + 1), (sp[0] + 1, sp[1] - 1), 
                          (sp[0] - 1, sp[1] + 1), (sp[0] - 1, sp[1] - 1)]
        valid_moves = [pos for pos in possible_moves if self.can_move(pos)] # Filtrar movimientos válidos
        if valid_moves:
            next_pos = rd.choice(valid_moves)
            self.model.grid.move_agent(self, next_pos)
            self.update_internal_map()
            self.update_pos_map()
    def explore_missing(self):
        self.update_internal_map()      
        self.update_pos_map()
        self.model.updateMapToGraph(self.model.robots_internal_map)    
        if not self.targetCell:
            nearestUCDist = 71
            if self.model.unexploredCells:
                print(f"{len(self.model.unexploredCells)} Celdas por explorar: {self.model.unexploredCells}")
                for cell in self.model.unexploredCells:
                    dist = np.sqrt( (self.pos[0]-cell[0])**2 + (self.pos[1]-cell[1])**2 )
                    if dist < nearestUCDist:
                        nearestUCDist = dist
                        self.targetCell = (cell[0],cell[1])
                self.model.unexploredCells.remove(self.targetCell)
            else:
                self.move_random()
                return
        self.queuedMovements = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
        if(self.queuedMovements):
            self.queuedMovements.pop(0)
            if self.can_move(self.queuedMovements[0]):
                self.model.grid.move_agent(self, self.queuedMovements[0])
                print(f"El robot se movio a la celda {self.pos}")
                if self.pos == self.targetCell:
                    self.targetCell = ()
            self.queuedMovements = []
        else: 
            if self.model.robots_internal_map[self.targetCell[0]][self.targetCell[1]] == 'X':
                self.targetCell = ()
    def assign_Litter(self):
        if self.model.litterCoords:
                self.queuedMovements = []
                nearestLitterDist = 71
                nearestLitterPos = ()
                for litterPos in self.model.litterCoords:
                    dist = np.sqrt( (self.pos[0]-litterPos[0])**2 + (self.pos[1]-litterPos[1])**2 )
                    if dist < nearestLitterDist:
                        nearestLitterDist = dist
                        nearestLitterPos = (litterPos[0],litterPos[1])
                self.targetCell = nearestLitterPos
                self.model.litterCoords.remove(self.targetCell)
                if self.pos != self.targetCell:
                    self.model.updateMapToGraph(self.model.robots_pos_map)
                    path = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
                    if path:
                        if len(path) > 1:
                            path.pop(0)
                        self.queuedMovements.append(path[0]) 
                    else: 
                        for agent in self.model.grid.get_cell_list_contents(self.targetCell):
                            if agent.type == 1:
                                self.assign_Litter()
                                return
        else:
            print(f"[Robot en {self.pos} - LT: {self.load}] Enhorabuena, no hay más basura!")
            if self.state == "cleaning":
                self.state = "done"
                self.model.robots_finished += 1
            self.move_random()
    def pickUpLitter(self):
        cell = self.model.grid.get_cell_list_contents(self.pos)
        toCollect = min(self.capacity-self.load, len(cell))
        for i in range(toCollect):
            if cell[i].type == 2:
                self.model.grid.remove_agent(cell[i])
                self.model.schedule.remove(cell[i])
                self.load += 1
        self.alreadyCleaned = True
    def disposePaperBin(self):
        self.load = 0
        self.queuedMovements = []
        self.alreadyCleaned = False
        missingTrash = len(self.model.grid.get_cell_list_contents(self.targetCell_aux))
        if  missingTrash == 0:
            self.targetCell = ()
            self.targetCell_aux = ()
            self.assign_Litter()
        else:
            self.targetCell = self.targetCell_aux
            self.targetCell_aux = ()
    def moveToPaperBin(self):
        if self.targetCell != self.model.paperBin_pos:
            self.targetCell_aux = self.targetCell
            self.targetCell = self.model.paperBin_pos
        self.model.updateMapToGraph(self.model.robots_pos_map)
        path = self.model.bfs(self.model.cellsGraph, self.pos, self.model.paperBin_pos)
        if path:
            if(len(path) > 1):
                path.pop(0)
            if self.can_move(path[0]):
                self.model.grid.move_agent(self, path[0])
                self.update_pos_map()
                path.pop(0)
            else:
                self.move_random()
        else:
            self.move_random()
    def move(self):
        if self.queuedMovements:
            if self.can_move(self.queuedMovements[0]):
                self.model.grid.move_agent(self, self.queuedMovements[0])
                self.update_pos_map()
                self.queuedMovements.pop(0)
        else:
            self.model.updateMapToGraph(self.model.robots_pos_map)
            path = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
            if path:
                if(len(path) > 1):
                    path.pop(0)
                if self.can_move(path[0]):
                    self.model.grid.move_agent(self, path[0])
                    self.update_pos_map()
                    path.pop(0)
                else:
                    self.move_random()
            else:
                self.move_random()
    def move_random(self):
        sp = self.pos
        possible_moves = [(sp[0], sp[1] + 1), (sp[0], sp[1] - 1), 
                          (sp[0]+ 1, sp[1]), (sp[0] - 1, sp[1]), 
                          (sp[0] + 1, sp[1] + 1), (sp[0] + 1, sp[1] - 1), 
                          (sp[0] - 1, sp[1] + 1), (sp[0] - 1, sp[1] - 1)]
        valid_moves = [pos for pos in possible_moves if self.can_move(pos)] # Filtrar movimientos válidos
        if valid_moves:
            next_pos = rd.choice(valid_moves)
            if next_pos != self.model.paperBin_pos:
                self.model.grid.move_agent(self, next_pos)
                self.update_pos_map()
    def update_pos_map(self):
        if hasattr(self, 'last_position'):
            self.model.robots_pos_map[self.last_position[0]][self.last_position[1]] = ''
        self.last_position = self.pos
        self.model.robots_pos_map[self.pos[0]][self.pos[1]] = 'S'
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for agent in neighbors:
            if agent.type == 3:
                self.model.robots_pos_map[agent.pos[0]][agent.pos[1]] = 'X'
            elif agent.type == 4:
                self.model.robots_pos_map[agent.pos[0]][agent.pos[1]] = 'P'
        if self.model.robots_pos_map[self.pos[0]][self.pos[1]] == '':
            self.model.robots_pos_map[self.pos[0]][self.pos[1]] = '0'
    def update_internal_map(self):
        if self.model.robots_internal_map[self.pos[0]][self.pos[1]] == '':
            self.model.exploredCellsCount += 1
        cell_content = self.model.grid.get_cell_list_contents(self.pos)
        neighbors = self.model.grid.get_neighbors(self.pos, moore = True, include_center = False)
        litter = 0
        for agent in cell_content:
            if agent != 1:
                if agent.type == 2:
                    litter += 1
                    self.model.robots_internal_map[self.pos[0]][self.pos[1]] = str(litter)
                if agent.type == 4:
                    self.model.robots_internal_map[self.pos[0]][self.pos[1]] = 'P'
        litter = 0
        for agent in neighbors:
            if agent.type == 3:
                if self.model.robots_internal_map[agent.pos[0]][agent.pos[1]] == '':
                    self.model.exploredCellsCount += 1
                self.model.robots_internal_map[agent.pos[0]][agent.pos[1]] = 'X'
        if self.model.robots_internal_map[self.pos[0]][self.pos[1]] == '':
            self.model.robots_internal_map[self.pos[0]][self.pos[1]] = '0'
        elif (self.model.robots_internal_map[self.pos[0]][self.pos[1]].isnumeric() and self.model.robots_internal_map[self.pos[0]][self.pos[1]] != '0'):
            if (self.pos[0],self.pos[1]) not in self.model.litterCoords:
                    self.model.litterCoords.append((self.pos[0],self.pos[1]))
class GameBoard(Model):
    def __init__(self, width, height, gameboard, robots_count):
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        self.simulation_continue = True
        self.current_id = 0
        self.current_step = 0
        self.current_state = ""
        self.total_steps = 0
        self.robots_finished = 0
        self.paperBin_pos = (0,0)
        self.robots_internal_map = np.zeros((width, height), dtype=str)
        self.robots_pos_map = np.zeros((width, height), dtype=str)
        self.cellsGraph = {}
        self.cellsCount = width*height
        self.exploredCellsCount = 0
        self.unexploredCells = []
        self.litterCoords = []
        self.litterCount = 0
        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):
                self.initialize_agents(gameboard, x, y, robots_count)
        self.datacollector = DataCollector(model_reporters={"Grid": get_grid})

    def step(self):
        if self.robots_finished == 5:
            self.simulation_continue = False
        print("================================")
        print(self.current_step)
        if self.exploredCellsCount == self.cellsCount:
            print(f"Hay {len(self.litterCoords)} celdas con basura: {self.litterCoords}")
        self.schedule.step()
        self.datacollector.collect(self)
        if self.current_step == self.cellsCount:
            self.updateUnexplored()
        self.current_step += 1  

    def initialize_agents(self, gameboard, x, y, robots_count):
        
        cell = gameboard[x][y]
        
        if cell.isnumeric():
            litter_count = int(cell)
            while litter_count > 0:
                agent = Litter(self.next_id(), self)
                self.place_agent(agent, (x,y))
                litter_count -= 1
        
        elif cell == "X":
            agent = Wall(self.next_id(), self)
            self.place_agent(agent, (x,y))
        
        elif cell == "P":
            agent = PaperBin(self.next_id(), self)
            self.place_agent(agent, (x,y))
            self.paperBin_pos = (x, y)
        
        elif cell == "S":
            self.initialize_robots(x, y, robots_count)
            robots_count = 0
    
    
    def place_agent(self, agent, agent_pos):
        self.grid.place_agent(agent, agent_pos)
        self.schedule.add(agent)
    
    
    def initialize_robots(self, x, y, robots_count):
       
        while robots_count > 0:
            agent = Robot(self.next_id(), self)
            self.place_agent(agent, (x, y))
            robots_count -= 1
    
    # Creacion de lista con las celdas no exploradas
    def updateUnexplored(self):

        x = 0
        for row in self.robots_internal_map:
            y = 0
            
            for _ in row:
                
                if self.robots_internal_map[x][y] == '':
                    if (x,y) not in self.unexploredCells:
                        self.unexploredCells.append((x,y))
                y += 1
            x += 1
        
        self.unexploredCells.sort()
    
    #Convertir la matriz de las celdas exploradas por los robots en un grafo para el BFS
    def updateMapToGraph(self, matrix):

        graph = {}

        # Recorrer la matriz y agregar conexiones
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                connections = []
                if matrix[i][j] != 'X':
                    # Agregar conexiones en todas las direcciones, incluyendo diagonales
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            # Se realiza la comparacion para que las celdas vecinas no sean obstaculos o punto de salida
                            new_i, new_j = i + di, j + dj
                            if (0 <= new_i < len(matrix) and 
                                0 <= new_j < len(matrix[i]) 
                                and (di != 0 or dj != 0) 
                                and matrix[new_i][new_j] not in ('X', 'S')):
                                
                                connections.append((new_i, new_j))
                # Asignar las conexiones al nodo correspondiente
                graph[(i, j)] = connections

        self.cellsGraph = graph
    
    # Algoritmo de Breadth-First Search para llegar a las celdas no exploradas
    def bfs(self, grafo, inicio, objetivo):
        visitados = set()  # Conjunto para mantener registro de nodos visitados
        cola = [(inicio, [inicio])]  # Pares de nodo y el camino hacia el nodo

        while cola:
            (nodo_actual, camino) = cola.pop(0)  # Obtiene el primer nodo y su camino

            if nodo_actual == objetivo:
                return camino  # Si es el nodo objetivo, regresa el camino
            
            if nodo_actual not in visitados:
                visitados.add(nodo_actual)
                
                # Explora los posibles vecinos
                for vecino in grafo[nodo_actual]:
                    nuevo_camino = list(camino)
                    nuevo_camino.append(vecino)
                    cola.append((vecino, nuevo_camino))
        #Si no encuentra un camino, devuelve None
        return None 
    

# Representacion de los agentes en la animacion con colores
def get_grid(model):
    grid_state = np.zeros((model.grid.width, model.grid.height), dtype=int)

    for cell in model.grid.coord_iter():
        x, y = cell
        cell_contents = model.grid.get_cell_list_contents((x, y))
        
        # Assuming you have a Robot class with type 1 and a Wall class with type 3
        # You can modify this part to include other agent types
        for agent in cell_contents:
            if agent.type == 1:
                grid_state[x][y] = 1  # For Robots
            elif agent.type == 3:
                grid_state[x][y] = 3  # For Walls

    return grid_state
    
width = 5
height = 5
office = []

flag = True
# --- Ejecucion y visualizacion del grid. Parámetros iniciales del modelo ---
ROBOTS = 5
step_count = 0

with open('./inputs/input1.txt', 'r') as input:
    for linea in input:
        if flag:
            width, height = [int(num) for num in linea.split(" ")]
            flag = False
        
        else:
            office.append(linea.split(" "))
model = GameBoard(width, height, office, ROBOTS)
while model.simulation_continue:
    model.step()
    step_count += 1
print("Algoritmo terminado en ", model.total_steps, " steps") 

 # Arreglo de matrices

# Este es un supuesto basado en tu código



def animate(i):
    patch.set_data(all_grid.iloc[i][0])
all_grid = model.datacollector.get_model_vars_dataframe()
fig, axis = plt.subplots(figsize=(width, height))
axis.set_xticks([])
axis.set_yticks([])
patch = plt.imshow(all_grid.iloc[0][0], cmap=sns.color_palette("Paired", as_cmap=True))
anim = animation.FuncAnimation(fig, animate, frames = step_count, blit=False)

plt.show()


# GRID_SIZE_X = len(gameboard)
# GRID_SIZE_Y = len(gameboard[0])

# model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y, gameboard, ROBOTS)

# while model.simulation_continue:
#     model.step()
#     step_count += 1

# #Optiene todos los colores y registros de celdas por el tipo de agente
# all_grid_colors = model.datacollector.get_model_vars_dataframe()["GridColors"]

# #---- Colores puestos para los agentes -----
# my_cmap = ListedColormap(['snow', 'slategray', 'thistle', 'black', 'skyblue'])


# ani = None
# def animate(i):
    
#     axis.clear()
#     grid_data_repr = all_grid_repr.iloc[i]
#     grid_data_colors = all_grid_colors.iloc[i]
#     axis.imshow(grid_data_colors, cmap=my_cmap)
#     axis.set_xlim(-0.5, GRID_SIZE_Y - 0.5)
#     axis.set_ylim(-0.5, GRID_SIZE_X - 0.5)
#     axis.invert_yaxis()
#     axis.annotate(f'Step: {i+1}', xy=(0.5, 1.05), xycoords='axes fraction', ha='center', va='center', fontsize=12, color='black')
# # animacion de la simulacion
# fig, axis = plt.subplots(figsize=(7, 7))

# # Inicialización de la animación
# ani = animation.FuncAnimation(fig, animate, frames=step_count, repeat=False)

# # Mostrar la animación
# plt.show(block=True)

