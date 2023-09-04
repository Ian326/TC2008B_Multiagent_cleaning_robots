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
    
    #--- Constructor del Robot ---
    def __init__(self, id, model, pB_Pos):
        super().__init__(id, model)
        
        self.type = 1
        
        self.capacity = 5
        self.load = 0
        
        self.paperBin_pos = pB_Pos
        self.queuedMovements = []
        
        self.targetLitter = ()
    
    
    def step(self):
        #Las primeras n (Igual al tamaño del tablero) iteraciones, explorará sin orden
        if self.model.current_step <= self.model.cellsCount:
            if self.model.current_step == 1:
                return
            self.explore_random()
        #Las siguientes iteraciones, explorará las celdas faltantes
        elif self.model.exploredCellsCount != self.model.cellsCount:
                self.model.state = 2
                self.explore_missing()
        #[WIP] Recolectar basura
        else:
            print(self.model.current_step)
            self.model.state = 3
            
            if not self.targetLitter:
                self.assign_Litter()
                
            else:
                
                if (self.pos == self.targetLitter):
                    self.pickUpLitter()
                    print(f"[Robot en {self.pos}] Terminé de recoger basura")
                    self.moveToPaperBin()
                    #return
                else:
                    self.move()
    
    
    def can_move(self, pos):
        
        if self.model.grid.out_of_bounds(pos):
            return False
        # Verificar si hay algún robot o muro en la celda de destino
        return not any(agent.type == 1 or 
                       agent.type == 3 
                       for agent in self.model.grid.get_cell_list_contents([pos]))
    
    #Elige una celda aleatoria a su alrededor, si se puede mover, lo hará.
    def explore_random(self):
        
        # Definir las posibles direcciones de movimiento
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
    
    #Elige una de las celdas que faltan de explorar, si puede moverse, generará la mejor ruta para ir a ella
    def explore_missing(self):
        
        path = []
        end_point = (0,0)
        start_point = self.pos
        
        #Si hay celdas no exploradas. Elegir una celda no explorada
        if self.model.unexploredCells:
            if not self.queuedMovements:
                
                end_point = rd.choice(self.model.unexploredCells)
                self.model.unexploredCells.remove(end_point)
                
                graph = self.model.mapToGraph(self.model.robots_internal_map)
                
                path = self.model.bfs(graph, start_point, end_point)
                if path:
                    path.pop(0)
                    self.queuedMovements = path
            #Seguir los movimientos para llegar a la celda seleccionada
            else:
                
                end_point = self.queuedMovements[0]

                if self.can_move(self.queuedMovements[0]):
                    
                    self.model.grid.move_agent(self, self.queuedMovements[0])
                    self.update_internal_map()
                    self.queuedMovements.pop(0)
        #Si ya se exploraron todas las celdas, pasar a la siguiente fase
        else:
            self.model.state = 3
            
        print(f"Se han visitado {self.model.exploredCellsCount}/{self.model.cellsCount}")
        print("==========================================================================")
    
    def assign_Litter(self):
        
        if self.model.litterCoords:
                
                nearestLitterDist = 71
                nearestLitterPos = ()
                
                for litterPos in self.model.litterCoords:
                    
                    dist = np.sqrt( (self.pos[0]-litterPos[0]) **2 + (self.pos[1]-litterPos[1])**2 )
                    
                    if dist < nearestLitterDist:
                        nearestLitterDist = dist
                        nearestLitterPos = (litterPos[0],litterPos[1])
                
                self.targetLitter = nearestLitterPos
                self.model.litterCoords.remove(self.targetLitter)
                
                if self.pos != self.targetLitter:
                    
                    graph = self.model.mapToGraph(self.model.robots_internal_map)
                    
                    path = self.model.bfs(graph, self.pos, self.targetLitter)
                    
                    path.pop(0)
                    
                    self.queuedMovements = path
                
                print(f"[Robot en {self.pos}] Iré a la basura en {self.targetLitter}")
                print(f"[Robot en {self.pos}] Pasos para llegar: {self.queuedMovements}")
    
    def pickUpLitter(self):
        cell = self.model.grid.get_cell_list_contents(self.pos)
        toCollect = min(self.capacity-self.load, len(cell))
        for i in range(toCollect):
            if cell[i].type == 2:
                self.model.grid.remove_agent(cell[i])
                self.model.schedule.remove(cell[i])
                self.load += 1
    
    def moveToPaperBin(self):
        print(f"[Robot en {self.pos}] Me moveré a la papelera")
        if not self.queuedMovements:
                
                end_point = self.model.paperBin_pos
                
                graph = self.model.mapToGraph(self.model.robots_internal_map)
                
                path = self.model.bfs(graph, self.pos, end_point)
                
                path.pop(0)
                
                self.queuedMovements = path
                print(f"[Robot en {self.pos}] Pasos a seguir: {self.queuedMovements}\n")
                self.model.grid.move_agent(self, self.queuedMovements[0])
                self.queuedMovements.pop(0)
                
    
    def move(self):
        if self.queuedMovements:
            end_point = self.queuedMovements[0]
            print(f"[Robot en {self.pos}] Pasos a seguir: {self.queuedMovements}\n")
            if self.can_move(end_point):
                self.model.grid.move_agent(self, end_point)
                self.queuedMovements.pop(0)
            
        else:
           
            if self.pos == self.model.paperBin_pos:
                print(f"[Robot en {self.pos}] Estoy en la papelera.")
                if len(self.model.grid.get_cell_list_contents(self.targetLitter)) == 0:
                    self.targetLitter = ()
                    print(f"[Robot en {self.pos}] Terminé mi tarea, buscaré otra basura")
                else:
                
                    graph = self.model.mapToGraph(self.model.robots_internal_map)
        
                    path = self.model.bfs(graph, self.pos, self.targetLitter)
                    path.pop(0)
                    
                    self.queuedMovements = path
                    self.model.grid.move_agent(self, self.queuedMovements[0])
                    self.queuedMovements.pop(0)
                    print(f"[Robot en {self.pos}] Regresaré a la celda de basura")
    
    #Con cada movimiento de un Robot, se llena un mapa con lo que hay en esa celda. Si hay muros los registrará
    def update_internal_map(self):
        
        if self.model.robots_internal_map[self.pos[0]][self.pos[1]] == '':
            self.model.exploredCellsCount += 1
        
        cell_content = self.model.grid.get_cell_list_contents(self.pos)
        neighbors = self.model.grid.get_neighbors(self.pos, moore = True, include_center = False)
        litter = 0
        # Actualizar el mapa interno, dependiendo del tipo de agente (2 = Basura, 3 = Pared, 4 = Papelera)
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
        
        #Si la celda no contiene agentes, entonces está 'libre'
        if self.model.robots_internal_map[self.pos[0]][self.pos[1]] == '':
            self.model.robots_internal_map[self.pos[0]][self.pos[1]] = '0'
        elif (self.model.robots_internal_map[self.pos[0]][self.pos[1]].isnumeric() and self.model.robots_internal_map[self.pos[0]][self.pos[1]] != '0'):
            if (self.pos[0],self.pos[1]) not in self.model.litterCoords:
                    self.model.litterCoords.append((self.pos[0],self.pos[1]))

# --- Definición del Modelo ---
class GameBoard(Model):
    
    #--- Constructor del Modelo---
    def __init__(self, width, height, gameboard, robots_count):
        
        self.grid = MultiGrid(width, height, torus = False)
        self.schedule = RandomActivation(self)
        
        self.current_id = 0
        self.current_step = 0
    
        self.paperBin_pos = (0,0)
        
        self.robots_internal_map = np.zeros((width, height), dtype=str)

        self.cellsCount = width*height
        self.exploredCellsCount = 0
        self.unexploredCells = []
        
        self.litterCoords = []
        
        self.state = 1
        
        for x in range(len(gameboard)):
            for y in range(len(gameboard[x])):
                self.initialize_agents(gameboard, x, y, robots_count)

        self.datacollector = DataCollector(
            model_reporters={
                "GridRepr": lambda m: get_grid(m)[0],
                "GridColors": lambda m: get_grid(m)[1]
            })


    def step(self):
        if self.state == 3:
            self.litterCoords.sort()
            
        self.current_step += 1
        
        self.schedule.step()
        self.datacollector.collect(self)

        if self.current_step >= self.cellsCount:
            self.updateUnexplored()
        if self.state == 3:
            self.litterCoords.sort()

    #Inicializa los agentes de acuerdo a la lectura del input.txt
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
            self.initialize_robots(x, y, robots_count, self.paperBin_pos)
            robots_count = 0
    
    
    def place_agent(self, agent, agent_pos):
        self.grid.place_agent(agent, agent_pos)
        self.schedule.add(agent)
    
    
    def initialize_robots(self, x, y, robots_count, pB_pos):
       
        while robots_count > 0:
            agent = Robot(self.next_id(), self, pB_pos)
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
    
    #Convertir la matriz de las celdas exploradas por los robots en un grafo para el BFS
    def mapToGraph(self, matrix):

        graph = {}

        # Recorrer la matriz y agregar conexiones
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                connections = []
                if matrix[i][j] not in ('X', 'S'):
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

        return graph
    
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
    grid_repr = np.zeros((model.grid.width, model.grid.height), dtype=object)
    grid_colors = np.zeros((model.grid.width, model.grid.height))
    
    for (content, (x, y)) in model.grid.coord_iter():
        has_paper_bin = False  # Variable para rastrear si la celda contiene una papelera
        
        for agent in content:
            # Creacion del contenido de las celdas de acuerdo con su tipo
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


# --- Ejecucion y visualizacion del grid. Parámetros iniciales del modelo ---
ROBOTS = 5
MAX_GENERATIONS = 182

gameboard = [line.split() for line in open('./inputs/input1.txt').read().splitlines() if line][1:]
GRID_SIZE_X = len(gameboard)
GRID_SIZE_Y = len(gameboard[0])

model = GameBoard(GRID_SIZE_X, GRID_SIZE_Y, gameboard, ROBOTS)

for i in range(MAX_GENERATIONS):
  model.step()

#Optiene todos los colores y registros de celdas por el tipo de agente
all_grid_repr = model.datacollector.get_model_vars_dataframe()["GridRepr"]
all_grid_colors = model.datacollector.get_model_vars_dataframe()["GridColors"]

#---- Colores puestos para los agentes -----
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
                color = 'white'  # El color del texto del robot sera blanco para que sea visible sobre la papelera
                
            # Cambiar el color del texto en funcion del tipo de agente en la celda
            elif str(num).isdigit():
                color = 'black'
            else:
                color = 'white'
            
            if num != "0":
                axis.annotate(num, xy=(y, x), ha='center', va='center', color=color)

    axis.set_xlim(-0.5, GRID_SIZE_Y - 0.5)
    axis.set_ylim(-0.5, GRID_SIZE_X - 0.5)
    axis.invert_yaxis()
    axis.annotate(f'Step: {i}', xy=(0.5, 1.05), xycoords='axes fraction', ha='center', va='center', fontsize=12, color='black')
# animacion de la simulacion
anim = animation.FuncAnimation(fig, animate, frames=MAX_GENERATIONS, repeat=False)
anim.save(filename="cleaningRobots.mp4")
