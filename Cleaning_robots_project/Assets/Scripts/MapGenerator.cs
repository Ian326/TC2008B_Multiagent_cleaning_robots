using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using System.Text.RegularExpressions;

public class MapGenerator : MonoBehaviour
{
    public GameObject obstaclePrefab; // prefab para "X"
    public GameObject floorPrefab; // prefab para "0"
    public GameObject robotPrefab; // prefab para "S"
    public GameObject trashcanPrefab; // prefab para "P"
    public List<GameObject> garbagePrefab; // prefab para basura (número diferente de 0)
    public List<GameObject> toPreservePrefabs; // prefab para basura (número diferente de 0)
    public int tileDimension = 2;

    public void clearMap(){
        // Obtén todos los objetos en la escena
        GameObject[] allObjects = GameObject.FindObjectsOfType<GameObject>();

        // Itera a través de todos los objetos en la escena
        foreach (GameObject obj in allObjects)
        {
            //Destroy(obj);
            // Si el objeto no está en la lista de prefabs permitidos, destrúyelo
            if (!toPreservePrefabs.Contains(obj))
            {
                Destroy(obj);
            }
        }
    }
    public void GenerateMapFromData(string grid)
    {
    
        int startX = -51; 
        int startZ = 51;
        float startY = 0.09600022f;

        string auxString = Regex.Replace(grid, @"[']", "");
        //auxString = auxString.Substring(1, auxString.Length - 2);

        // Divide el string en líneas
        string[] lines = auxString.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        // Crea una lista de strings para almacenar los elementos
        List<List<string>> modelGrid = new List<List<string>>();

        // Divide cada línea por espacios y agrega los elementos a la lista de listas
        foreach (string line in lines)
        {
            string[] elements = line.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
            modelGrid.Add(new List<string>(elements));
        }

        Debug.Log(grid);

        for (int y = 0; y < modelGrid.Count; y++)
        {
            
            for (int x = 0; x < modelGrid[y].Count; x++)
            {
                // Calcula las nuevas coordenadas para instanciar
                int newX = startX + (x * tileDimension);
                int newZ = startZ - (y * tileDimension);
                float newY = startY;

                // Instanciamos un piso en cada posición.
                Vector3 pisoPos = new Vector3(newX, 0, newZ);
                GameObject floor = Instantiate(floorPrefab, pisoPos, Quaternion.identity);
                

                // Obtener el tipo de celda en esta posición.
                string cellType = modelGrid[y][x];

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
                    // La altura en Y donde todas las latas de basura estarán situadas
                    newY += 1;
                    if(value == 1){prefabToUse = garbagePrefab[0];}
                    else if(value == 2){prefabToUse = garbagePrefab[1]; }
                    else if(value == 3){prefabToUse = garbagePrefab[2]; }
                    else if(value == 4){prefabToUse = garbagePrefab[3]; }
                    else if(value == 5){prefabToUse = garbagePrefab[4]; }
                    else if(value == 6){prefabToUse = garbagePrefab[5]; }
                    else if(value == 7){prefabToUse = garbagePrefab[6]; }
                    else if(value == 8){prefabToUse = garbagePrefab[7]; }

                }

                if (prefabToUse != null)
                {
                    Vector3 pos = new Vector3(newX, newY, newZ);

                    GameObject temp = Instantiate(prefabToUse, pos, Quaternion.identity);
                    

                }
            }
        }
    }

    public bool IsObjectAtPos(Vector3 pos)
    {
        // Realiza un Raycast en la posición del spawnPoint para verificar si hay objetos
        RaycastHit hit;
        if (Physics.Raycast(pos, Vector3.down, out hit)){
            return true;
        }
        else{
            return false;
        }
    }
}