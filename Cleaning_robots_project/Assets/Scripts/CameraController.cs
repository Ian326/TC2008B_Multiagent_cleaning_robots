using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float moveSpeed = 10f;
    public float turnSpeed = 60f;
    public float zoomSpeed = 1f;  

    // Cantidad máxima en Y para hacer zoom in
    public float minOrthographicSize = 2f;
    //Cantidad máxima en Y para hacer zoom out
    public float maxOrthographicSize = 40f;

    private Camera cam;  // Referencia a la cámara
    void Start()
    {
        //Inicializar la cámara
        cam = GetComponent<Camera>();
        cam.orthographic = true;
    }


    // Update is called once per frame
    void Update()
    {
        // Guardas las posiciones de la cámara horizontal y verticalmente
        float horizontalInput = 0f;
        float verticalInput = 0f;

        if (Input.GetKey(KeyCode.A)) horizontalInput = -1f;
        if (Input.GetKey(KeyCode.D)) horizontalInput = 1f;
        if (Input.GetKey(KeyCode.W)) verticalInput = 1f;
        if (Input.GetKey(KeyCode.S)) verticalInput = -1f;

        //Nueva posición de la cámara
        Vector3 movement = new Vector3(horizontalInput, 0, verticalInput);

        transform.Translate(movement * Time.deltaTime * moveSpeed, Space.World);

        // Guardar la rotación de la cámara
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            transform.Rotate(Vector3.up, -turnSpeed * Time.deltaTime, Space.World);
        }
        if (Input.GetKey(KeyCode.RightArrow))
        {
            transform.Rotate(Vector3.up, turnSpeed * Time.deltaTime, Space.World);
        }
        // Control del zoom
        float zoomInput = Input.GetAxis("Mouse ScrollWheel");

        if (zoomInput != 0)
        {
            float newOrthographicSize = cam.orthographicSize;

            // Incrementa o decrementa en múltiplos de 2f
            if (zoomInput > 0)
            {
                newOrthographicSize -= 2f;  // Zoom In
            }
            else if (zoomInput < 0)
            {
                newOrthographicSize += 2f;  // Zoom Out
            }

            // Limita el tamaño ortográfico a los valores mínimo y máximo
            newOrthographicSize = Mathf.Clamp(newOrthographicSize, minOrthographicSize, maxOrthographicSize);

            // Asigna el nuevo tamaño ortográfico
            cam.orthographicSize = newOrthographicSize;
        }
    }
}