using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using UnityEngine;

public class camera_script : MonoBehaviour
{
    public GameObject background;
    public GameObject targetObject;
    public GameObject floor;
    public GameObject plants;
    public Material standard;
    public Material whiteMask;
    private int FileCounter = 0;

    Camera cam;

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(ExampleCoroutine());
        cam = GetComponent<Camera>();
        cam.depthTextureMode = DepthTextureMode.Depth;
    }

    // Update is called once per frame
    void Update()
    { 
    }

    IEnumerator ExampleCoroutine()
    {
        for(int i = 0; i < 50; i++) {
            yield return new WaitForSeconds(0.1f);
            string name = FileCounter + ".png";
            CamCapture(cam, name);
            floor.SetActive(false);
            plants.SetActive(false);
            background.GetComponent<Image>().color = Color.black;
            targetObject.GetComponent<MeshRenderer>().material = whiteMask;
            name = FileCounter + "_mask.png";
            CamCapture(cam, name);
            floor.SetActive(true);
            plants.SetActive(false);
            background.GetComponent<Image>().color = new Color(0.529f, 0.808f, 0.922f, 1f);
            targetObject.GetComponent<MeshRenderer>().material = standard;
            FileCounter++;
            float y = Random.Range(0f, 1f);
            float z = Random.Range(-7f, -12f);
            transform.position = new Vector3(0, y, z);
            transform.localRotation = Quaternion.Euler(new Vector3(Random.Range(-20f, 0), 0, 0));
            targetObject.transform.Rotate(new Vector3(0, 0.3f, 0) * Random.Range(-180f, -180f), Space.World);
            //transform.RotateAround(new Vector3(0, 0, 0), Vector3.right, Random.Range(-5, 0));
        }    
    }
/*
    void OnGUI()    
    {
        Vector3 point = new Vector3();
        Event   currentEvent = Event.current;
        Vector2 mousePos = new Vector2();

        // Get the mouse position from Event.
        // Note that the y position from Event is inverted.
        mousePos.x = currentEvent.mousePosition.x;
        mousePos.y = cam.pixelHeight - currentEvent.mousePosition.y;

        point = cam.ScreenToWorldPoint(new Vector3(mousePos.x, mousePos.y, cam.transform.position.z));

        GUILayout.BeginArea(new Rect(20, 20, 250, 120));
        GUILayout.Label("Screen pixels: " + cam.pixelWidth + ":" + cam.pixelHeight);
        GUILayout.Label("Mouse position: " + mousePos);
        GUILayout.Label("World position: " + point.ToString("F3"));
        GUILayout.EndArea();
    }
*/
    private void CamCapture(Camera cam, string name)
    {

        Debug.Log("Capture");

        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
 
        cam.Render();
        Texture2D Image = new Texture2D(cam.targetTexture.width, cam.targetTexture.height);
        Image.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0);
        Image.Apply();
        RenderTexture.active = currentRT;
        
        var Bytes = Image.EncodeToPNG();
        Destroy(Image);
        
        System.IO.File.WriteAllBytes(Application.dataPath + "/DataSet/" + name, Bytes);
        Debug.Log("Capture realized");
    }

}
