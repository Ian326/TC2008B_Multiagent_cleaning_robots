from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import os

class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):

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
                step = []
                for line in file:
                    line = line.strip()
                    if line.startswith("[["):
                        step = []
                    elif line.endswith("]]"):
                        step.append(line.replace("[", "").replace("]", "").strip())
                        steps.append(step)
                        step = []
                    else:
                        step.append(line.replace("[", "").replace("]", "").strip())
        """with open('./model.txt', 'r') as file:
            ## Itera línea por línea en el archivo
            for linea in file:
                # Quita los corchetes y elimina espacios en blanco de los extremos
                linea_limpia = linea.replace('[', '').replace(']', '').strip()
                # Si la línea no está vacía después de limpiarla, añade a la lista
                if linea_limpia:
                    listado.append(linea_limpia)
        
        
        for i in range(len(listado)):
            if i % (rows+1) == (rows):
                print(board)
                steps.append(board)
                board = []
            else:
                board.append(listado[i])"""

        map_data = steps[-1]
        # Calcular la cantidad de cada tipo de elemento

        total_robots = 5

        # Preparar el JSON para enviar
        response ={
            "map_data": map_data,
            "total_robots": total_robots,
            "rows": rows,
            "cols": cols
        }

        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()