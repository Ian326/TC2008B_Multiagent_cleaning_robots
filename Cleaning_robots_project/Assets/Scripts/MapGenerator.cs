using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SimpleJSON;


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
                    prefabToUse = robotPrefab;
                }
                else if (cellType == "P")
                {
                    prefabToUse = trashcanPrefab;
                }
                else if (int.TryParse(cellType, out int value) && value > 0)
                {
                    // Inicializamos la altura de la primera lata
                    float yOffset = 0.09600022f;
                    // Si el tipo de celda es un número y ese número es mayor que 0, entonces es basura.
                    for (int i = 0; i < value; i++)
                    {
                        // Ajustamos la posición vertical en Y de cada lata
                        float yPosition = yOffset + 0.30386477f * i; //0.307f

                        Instantiate(garbagePrefab, new Vector3(newX, yPosition, newZ), Quaternion.identity);
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