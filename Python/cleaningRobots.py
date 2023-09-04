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
        #Las primeras n (Igual al tamaño del tablero) iteraciones, explorará sin orden
        if self.model.current_step <= self.model.cellsCount:
            if self.model.current_step >= 1:
                self.explore_random()
                
        #Las siguientes iteraciones, explorará las celdas faltantes
        elif self.model.exploredCellsCount != self.model.cellsCount:
                self.state = "explore_missing"
                self.explore_missing()
                #print(self.model.robots_internal_map)
                print(f"Se han explorado {self.model.exploredCellsCount}/{self.model.cellsCount} celdas")
        
        #[WIP] Recolectar basura
        else:
            if self.state == "explore_missing":
                self.state = "cleaning"
                self.targetCell = ()
            
            print(f"Atributos del Robot {self.pos} - TC: {self.targetCell} QM: {self.queuedMovements} Load: {self.load} Cleaned: {self.alreadyCleaned}")
            
            #Agregar una Celda para moverse
            if not self.targetCell:
                print(f"[Robot en {self.pos}] No tengo TC, asignando una...")
                self.assign_Litter()
            
            #Al tener una celda para moverse, checa donde está
            else:
                
                self.model.updateMapToGraph(self.model.robots_pos_map)

                #Si llegó a la celda, con basura, la limpia (No debe ser la papelera)
                if (self.pos == self.targetCell and 
                    self.pos != self.model.paperBin_pos and not 
                    self.alreadyCleaned):
                    
                    print(f"[Robot en {self.pos}] ya estoy encima de la basura. Limpiando...")
                    self.queuedMovements = []
                    
                    self.pickUpLitter() #self.alreadyCleaned = True
                
                if (self.alreadyCleaned):
                    self.moveToPaperBin()
                    return
                
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
            self.update_pos_map()
    
    #Elige una de las celdas que faltan de explorar, si puede moverse, generará la mejor ruta para ir a ella
    def explore_missing(self):
        self.update_internal_map()      
        self.update_pos_map()
        self.model.updateMapToGraph(self.model.robots_internal_map)
        
                    
        print(f"Atributos del Robot - SP: {self.pos} TC: {self.targetCell} QM: {self.queuedMovements}")
            
        if not self.targetCell:
                
            nearestUCDist = 71
            
            #Sin movimientos pendientes, sin target, con celdas por descubrir
            if self.model.unexploredCells:
                print(f"{len(self.model.unexploredCells)} Celdas por explorar: {self.model.unexploredCells}")
                for cell in self.model.unexploredCells:
                    
                    dist = np.sqrt( (self.pos[0]-cell[0])**2 + (self.pos[1]-cell[1])**2 )
                    
                    if dist < nearestUCDist:
                        nearestUCDist = dist
                        self.targetCell = (cell[0],cell[1])

                self.model.unexploredCells.remove(self.targetCell)
            else:
                print(f"[Robot en {self.pos}] Mision completada. Esperando a los demás...")
                self.move_random()
                return
        
        self.queuedMovements = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
            
        if(self.queuedMovements):
            self.queuedMovements.pop(0)
        
            print(f"El robot en la celda {self.pos} explorará la celda {self.targetCell}")
            print(f"Movimientos: {self.queuedMovements}")
            #Seguir el movimiento para llegar a la celda seleccionada
            if self.can_move(self.queuedMovements[0]):
                
                self.model.grid.move_agent(self, self.queuedMovements[0])
                print(f"El robot se movio a la celda {self.pos}")
                
                
                if self.pos == self.targetCell:
                    self.targetCell = ()
                    
            self.queuedMovements = []
                    
        else: 
            print(f"No se encontró un camino de {self.pos} a {self.targetCell}")
            if self.model.robots_internal_map[self.targetCell[0]][self.targetCell[1]] == 'X':
                self.targetCell = ()
    
    #Elige una celda con basura como objetivo
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
                print(f"[Robot en {self.pos}] Iré a la basura en {self.targetCell}")
                if self.pos != self.targetCell:
                    
                    self.model.updateMapToGraph(self.model.robots_pos_map)
                    
                    path = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
                    if path:
                        print(f"El camino más corto encontrado es: {path}")
                        if len(path) > 1:
                            path.pop(0)
                        self.queuedMovements.append(path[0]) 
                    else: 
                        for agent in self.model.grid.get_cell_list_contents(self.targetCell):
                            if agent.type == 1:
                                print(f"Ya hay un robot en {self.targetCell}. Asignando otra...")
                                self.assign_Litter()
                                return
        else:
            print(f"[Robot en {self.pos}] Enhorabuena, no hay más basura!")
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
    
    
    def moveToPaperBin(self):
        #Si ya está en la papelera, deposita la basura y se intenta mover de regreso o a una nueva celda
        if self.pos == self.model.paperBin_pos:
            
            self.load = 0
            self.queuedMovements = []
            self.alreadyCleaned = False
            
            missingTrash = len(self.model.grid.get_cell_list_contents(self.targetCell_aux))
            
            print(f"Robot en papelera: Ya dejé la basura, hay {missingTrash} basuras en mi celda asignada")
            
            if  missingTrash == 0:
                print(f"Robot en papelera: Buscaré una nueva posición con basura")
                self.targetCell = ()
                self.targetCell_aux = ()
                self.assign_Litter()
            
            else:
                print(f"Robot en papelera: Me falta recoger basura en {self.targetCell_aux} Volveré a esa celda")
                self.targetCell = self.targetCell_aux
                self.targetCell_aux = ()
            
            return
        
        #Si llamaste esta funcion es porque quieres ir a la papelera, entonces, tu targetCell es la papelera
        if self.targetCell != self.model.paperBin_pos:
            self.targetCell_aux = self.targetCell
            self.targetCell = self.model.paperBin_pos
        
        #Checar si existe una ruta posible a la papelera
        self.model.updateMapToGraph(self.model.robots_pos_map)
        path = self.model.bfs(self.model.cellsGraph, self.pos, self.model.paperBin_pos)
        
        if path:
            
            if(len(path) > 1):
                path.pop(0)
            print(f"[Robot en {self.pos}] se moverá al paperBin. Steps: {path}")
            
            if self.can_move(path[0]):
                self.model.grid.move_agent(self, path[0])
                self.update_pos_map()
                path.pop(0)
                print(f"[Robot se movio a {self.pos}]")
            
            else:
                print(f"El robot no se puede mover a {path[0]}. Se moverá random")
                self.move_random()
                print(f"El robot se movió a {self.pos}")
        else:
            print("La papelera está ocupada. Se moverá random")
            self.move_random()
            print(f"El robot se movió a {self.pos}")
                
    
    def move(self):
        if self.queuedMovements:
            print(f"[Robot en {self.pos}] Tenía movimientos pendientes.")
            if self.can_move(self.queuedMovements[0]):
                    self.model.grid.move_agent(self, self.queuedMovements[0])
                    self.update_pos_map()
                    print(f"[Robot se movió a {self.pos}]")
                    self.queuedMovements.pop(0)
        else:
            print(f"[Robot en {self.pos}] No tengo movimientos pendientes. Intentaré ir a {self.targetCell}")
            self.model.updateMapToGraph(self.model.robots_pos_map)
            path = self.model.bfs(self.model.cellsGraph, self.pos, self.targetCell)
            
            if path:
                if(len(path) > 1):
                    path.pop(0)
                print(f"[Robot en {self.pos}] se moverá a {self.targetCell}. Steps: {path}")
                if self.can_move(path[0]):
                    self.model.grid.move_agent(self, path[0])
                    self.update_pos_map()
                    path.pop(0)
                    print(f"[Robot se movio a {self.pos}]")
                else:
                    print(f"El robot no se puede mover a {path[0]}. Se moverá random")
                    self.move_random()
                    print(f"El robot se movió a {self.pos}")
                    
            else:
                print("No encontré camino a casa. Me moveré random")
                self.move_random()
                print(f"El robot se movió a {self.pos}")
    
    def move_random(self):
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
            self.update_pos_map()
        
    
    def update_pos_map(self):
        # Si last_position está definida, quita la 'S' de esa posición
        if hasattr(self, 'last_position'):
            self.model.robots_pos_map[self.last_position[0]][self.last_position[1]] = ''

        # Guardar la última posición
        self.last_position = self.pos

        # Marca la posición actual del robot como 'S'
        self.model.robots_pos_map[self.pos[0]][self.pos[1]] = 'S'

        # Otras partes del código no relacionadas con el rastreo del robot
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)

        for agent in neighbors:
            if agent.type == 3:
                self.model.robots_pos_map[agent.pos[0]][agent.pos[1]] = 'X'
            elif agent.type == 4:
                self.model.robots_pos_map[agent.pos[0]][agent.pos[1]] = 'P'
        # SE PUEDE BORRAR
        if self.model.robots_pos_map[self.pos[0]][self.pos[1]] == '':
            self.model.robots_pos_map[self.pos[0]][self.pos[1]] = '0'
        # elif (self.model.robots_pos_map[self.pos[0]][self.pos[1]].isnumeric() and 
        #       self.model.robots_pos_map[self.pos[0]][self.pos[1]] != '0'):
            

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
        self.current_state = ""
        self.total_steps = 0
        self.robotCount = robots_count
        
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

        self.datacollector = DataCollector(
            model_reporters={
                "GridRepr": lambda m: get_grid(m)[0],
                "GridColors": lambda m: get_grid(m)[1]
            })


    def step(self):
        print("================================")
        print(self.current_step)
        if self.exploredCellsCount == self.cellsCount:
            print("Se exploraron todas las celdas\n")
            self.litterCoords.sort()
            print(self.robots_pos_map)
            print(f"Hay {len(self.litterCoords)} celdas con basura: {self.litterCoords}")
        
        self.schedule.step()
        
        self.datacollector.collect(self)

        if self.current_step == self.cellsCount:
            self.updateUnexplored()
        self.current_step += 1
            
            

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
MAX_GENERATIONS = 120

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
    axis.annotate(f'Step: {i+1}', xy=(0.5, 1.05), xycoords='axes fraction', ha='center', va='center', fontsize=12, color='black')
# animacion de la simulacion
anim = animation.FuncAnimation(fig, animate, frames=MAX_GENERATIONS, repeat=False)
anim.save(filename="cleaningRobots.mp4")
