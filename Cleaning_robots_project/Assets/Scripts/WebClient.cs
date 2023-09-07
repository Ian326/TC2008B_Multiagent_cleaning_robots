// TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
// C# client to interact with Python server via POST
// Sergio Ruiz-Loza, Ph.D. March 2021

using System.Collections;
using UnityEngine;
using UnityEngine.Networking;


public class WebClient : MonoBehaviour
{
    public MapGenerator mapGenerator;  // Referencia al MapGenerator

    IEnumerator SendData(string data)
    {
        while(true){
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
                    string grid = www.downloadHandler.text;
                    // Debug.Log(grid);
                    // Asegurándose de pasar todos los parámetros necesarios
                    mapGenerator.clearMap();
                    mapGenerator.GenerateMapFromData(grid);
                }
            }

            yield return wait();
        }
    }

    void Start()
    {
        StartCoroutine(SendData("dummy data"));
    }

    void Update()
    {
    }

    IEnumerator wait()
    {
        yield return new WaitForSeconds(0.25f);
    }
}   