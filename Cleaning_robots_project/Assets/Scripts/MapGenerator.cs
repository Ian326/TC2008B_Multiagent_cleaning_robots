using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SimpleJSON;
using System.Linq;


public class MapGenerator : MonoBehaviour
{
    public GameObject obstaclePrefab; // prefab para "X"
    public GameObject floorPrefab; // prefab para "0"
    public GameObject robotPrefab; // prefab para "S"
    public GameObject trashcanPrefab; // prefab para "P"
    public GameObject garbagePrefab; // prefab para basura (número diferente de 0)
    public Camera mainCamera; //Cámara 2D

    public void GenerateMapFromData(string mapData, int rows, int cols, int total_cells, int total_trash, int total_obstacles, int total_robots, int total_trashcans)
    {
        // Dividir el texto del mapa en líneas.
        string[] lines = mapData.Trim().Split('\n');
        
        int width = lines[0].Split(' ').Length;
        int height = lines.Length;
        int startX = -51, startZ = 51;
        int tileDimension = 2; // Asumiendo que el piso mide 2x2

        for (int y = 0; y < rows; y++)
        {
            string[] cells = lines[y].Trim().Split(' ');
            for (int x = 0; x < cols; x++)
            {
                // Calcula las nuevas coordenadas para instanciar
                int newX = startX + (x * tileDimension);
                int newZ = startZ - (y * tileDimension);
                // Instanciamos un piso en cada posición.
                Instantiate(floorPrefab, new Vector3(newX, 0, newZ), Quaternion.identity);

                // Obtener el tipo de celda en esta posición.
                string cellType = cells[x].Trim();

                GameObject prefabToUse = null;

                // Decidir qué prefab usar en función del tipo de celda.
                if (cellType == "X")
                {
                    prefabToUse = obstaclePrefab;
                }
                else if (cellType == "S")
                {
                    for (int i = 0; i < total_robots; i++) // Bucle para iterar para que se agreguen los 5 robots
                    {
                        Instantiate(robotPrefab, new Vector3(newX, 0.09600022f, newZ), Quaternion.identity);
                    }
                    continue;  // No hay necesidad de volver a instanciar al final del bucle, así que podemos continuar con la siguiente iteración.
                }
                else if (cellType == "P")
                {
                    prefabToUse = trashcanPrefab;
                }
                else if (int.TryParse(cellType, out int value) && value > 0)
                {
                    // La altura en Y donde todas las latas de basura estarán situadas
                    float yPosition = 0.09600022f;
                    
                    // Lista para mantener un registro de las coordenadas ocupadas dentro de esta celda
                    List<Vector3> occupiedPositions = new List<Vector3>();

                    // Si el tipo de celda es un número y ese número es mayor que 0, entonces es basura.
                    for (int i = 0; i < value; i++)
                    {
                        Vector3 newPos;

                        do
                        {
                            float randomX = Random.Range(-0.5f, 0.5f);
                            float randomZ = Random.Range(-0.5f, 0.5f);
                            newPos = new Vector3(newX + randomX, yPosition, newZ + randomZ);
                        }
                        while (occupiedPositions.Any(pos => Vector3.Distance(newPos, pos) < 0.188)); // Asegurarse de que no está demasiado cerca de otra lata
                        
                        // Añadir la nueva posición a la lista de posiciones ocupadas
                        occupiedPositions.Add(newPos);
                        
                        Instantiate(garbagePrefab, newPos, Quaternion.identity);
                    }
                }
                // Instanciamos el prefab en la posición (x, 1, y), sobre el piso.
                if (prefabToUse != null)
                {
                    Instantiate(prefabToUse, new Vector3(newX, 0.09600022f, newZ), Quaternion.identity);
                }
            }
        }
        
        // Ajusta la posición de la cámara para que esté centrada en la cuadrícula.
        Vector3 cameraPosition = new Vector3(startX + ((float)cols / 2 * tileDimension), mainCamera.transform.position.y, startZ - ((float)rows / 2 * tileDimension) +1);

        // Ajusta la cámara para modo ortográfico
        mainCamera.orthographic = true;

        // Rotar la cámara 90 grados en X para que mire hacia abajo
        mainCamera.transform.rotation = Quaternion.Euler(90, 0, 0);

        // Ajustar la altura (posición Y) de la cámara para que abarque toda la cuadrícula.
        float cameraHeight = Mathf.Max(rows, cols) * 0.5f * tileDimension;
        cameraPosition.y = cameraHeight;
        
        // Asignar la nueva posición y rotación a la cámara
        mainCamera.transform.position = cameraPosition;
        
        // Ajustar el tamaño del área que la cámara captura
        mainCamera.orthographicSize = cameraHeight;
    }
}