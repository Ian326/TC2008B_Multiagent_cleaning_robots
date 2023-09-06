listado = []
steps = []
board = []
rows = 0
cols = 0

with open('./model.txt', 'r') as file:
    
    lines = file.readlines()
    # Buscamos la primera línea que comienza con '[[' para identificar el comienzo de la primera "lista de listas"
    start_index = next(i for i, line in enumerate(lines) if line.strip().startswith("[["))
    # Ahora, buscamos la primera línea que termina con ']]' para identificar el final de la primera "lista de listas"
    end_index = next(i for i, line in enumerate(lines[start_index:]) if line.strip().endswith("]]")) + start_index
    # Calculamos las dimensiones
    rows = end_index - start_index + 1
    cols = len(lines[start_index].strip().split())  # Usamos split para contar los elementos en la primera línea

    steps = []

with open('./model.txt', 'r') as file:
     # Itera línea por línea en el archivo
    for linea in file:
        # Quita los corchetes y elimina espacios en blanco de los extremos
        linea_limpia = linea.replace('[', '').replace(']', '').strip()
        # Si la línea no está vacía después de limpiarla, añade a la lista
        if linea_limpia:
            listado.append(linea_limpia)
    
print(rows,cols)
for i in range(len(listado)):
    if i % (rows+1) == (rows):
        print(board)
        steps.append(board)
        board = []
    else:
        board.append(listado[i])