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
        # Leer el archivo 'input.txt'
        with open('C:\\Users\\marif\\OneDrive\\Escritorio\\TC2008B_Multiagent_cleaning_robots\\Python\\inputs\\input1.txt', 'r') as f:
            # Leer la primera línea para obtener las dimensiones del mapa
            first_line = f.readline().strip()
            rows, cols = map(int, first_line.split())
            # Calcular el total de celdas basado en las dimensiones
            total_cells = rows * cols
            # Continúa leyendo el resto del archivo para contar los demás elementos
            map_data = f.read()

        # Calcular la cantidad de cada tipo de elemento
        total_trash = 0
        total_obstacles = 0
        total_robots = 5
        total_trashcans = 1
        
        # Contar las celdas desde la segunda línea
        lines = map_data.split("\n")[1:]

        for line in lines:
            total_cells += len(line.split())
            for cell in line.split():
                if cell.isdigit():
                    total_trash += int(cell)
                elif cell == "X":
                    total_obstacles += 1

        # Preparar el JSON para enviar
        response ={
            "map_data": map_data,
            "total_cells": total_cells,
            "total_trash": total_trash,
            "total_obstacles": total_obstacles,
            "total_robots": total_robots,
            "total_trashcans": total_trashcans,
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