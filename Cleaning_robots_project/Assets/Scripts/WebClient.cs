// TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
// C# client to interact with Python server via POST
// Sergio Ruiz-Loza, Ph.D. March 2021

using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;
using SimpleJSON;

public class WebClient : MonoBehaviour
{
    public MapGenerator mapGenerator;  // Referencia al MapGenerator

    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8585";

        using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();
            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)  
            {
                Debug.Log(www.error);
            }
            else
            {
                // Parse the JSON response
                var jsonResponse = JsonUtility.FromJson<MapResponse>(www.downloadHandler.text);
                string mapData = jsonResponse.map_data;
                int total_cells = jsonResponse.total_cells;
                int total_trash = jsonResponse.total_trash;
                int total_obstacles = jsonResponse.total_obstacles;
                int total_robots = jsonResponse.total_robots;
                int total_trashcans = jsonResponse.total_trashcans;

                // Asegurándose de pasar todos los parámetros necesarios
                mapGenerator.GenerateMapFromData(mapData, jsonResponse.rows, jsonResponse.cols, total_cells, total_trash, total_obstacles, total_robots, total_trashcans);
            }
        }
    }

    void Start()
    {
        StartCoroutine(SendData("dummy data"));

        if (mapGenerator.mainCamera == null) 
        {
            mapGenerator.mainCamera = Camera.main;  
        }
    }

    void Update()
    {
    }
}
[System.Serializable]
public class MapResponse{
    public string map_data;
    public int total_cells;
    public int total_trash;
    public int total_obstacles;
    public int total_robots;
    public int total_trashcans;
    public int rows;  
    public int cols;  
}