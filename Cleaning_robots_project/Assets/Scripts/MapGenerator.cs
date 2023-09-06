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
    public List <GameObject> garbagePrefab; // prefab para la basura
    // public Camera mainCamera; //Cámara 2D
    public void ClearOldMap() {
    // Asumiendo que todos los objetos del mapa son hijos de este GameObject
    foreach (Transform child in transform) {
        Destroy(child.gameObject);
    }
}
    public void GenerateMapFromData(string mapData, int rows, int cols, int total_robots)
    {
        ClearOldMap();  // Limpia el mapa anterior
        // Dividir el texto del mapa en líneas.
        string[] lines = mapData.Split('\n');
        
        int startX = -51, startZ = 51;
        int tileDimension = 2; // Asumiendo que el Tile (piso) mide 2x2

        for (int y = 0; y < rows; y++)
        {
            string[] cells = lines[y].Trim().Split(' ');
            for (int x = 0; x < cols; x++)
            {
                // Calcula las nuevas coordenadas para instanciar
                int newX = startX + (x * tileDimension);
                int newZ = startZ - (y * tileDimension);
                float newY = 0.09600022f;
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
                    //prefabToUse = robotPrefab;
                    for (int i = 0; i < total_robots; i++) // Ciclo para iterar para que se agreguen los 5 robots
                    {
                        Instantiate(robotPrefab, new Vector3(newX, 0.09600022f, newZ), Quaternion.identity);
                    }
                    continue;  // Continuar a la siguiente
                }
                else if (cellType == "P")
                {
                    prefabToUse = trashcanPrefab;
                }
                else if (int.TryParse(cellType, out int value) && value > 0)
                {
                    newY = 1.16f;

                    if (value == 1){
                        prefabToUse = garbagePrefab[0];
                    }
                    else if (value == 2){
                        prefabToUse = garbagePrefab[1];
                    }
                    else if (value == 3){
                        prefabToUse = garbagePrefab[2];
                    }
                    else if (value == 4){
                        prefabToUse = garbagePrefab[3];
                    }
                    else if (value == 5){
                        prefabToUse = garbagePrefab[4];
                    }
                    else if (value == 6){
                        prefabToUse = garbagePrefab[5];
                    }
                    else if (value == 7){
                        prefabToUse = garbagePrefab[6];
                    }
                    else if (value == 8){
                        prefabToUse = garbagePrefab[7];
                    }
                }
                // Instanciamos el prefab en la posición (x, 1, y), sobre el piso.
                if (prefabToUse != null)
                {
                    Instantiate(prefabToUse, new Vector3(newX, newY, newZ), Quaternion.identity);
                }
            }
        }
        
    }
}