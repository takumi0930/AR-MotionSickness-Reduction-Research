using System.IO;
using UnityEngine;

public class CSVWriter : MonoBehaviour
{
    private string filePath;
    private StreamWriter streamWriter;

    private float flushInterval = 1.0f; // 1秒ごとにFlush
    private float lastFlushTime = 0f;


    void Start(){
        string fileName = "appdata_" + System.DateTime.Now.ToString("yyMMdd_HHmmss") + ".csv";

        string directoryPath = Path.Combine(Application.persistentDataPath, "csv");
        Directory.CreateDirectory(directoryPath);
        filePath = Path.Combine(directoryPath, fileName);
        Debug.Log(filePath);

        streamWriter = new StreamWriter(filePath, true);
        // ヘッダー
        streamWriter.WriteLine("time, handle_pure_angvel, display_state");
    }


    public void WriteToCSV(string data){
        string currentTime = System.DateTime.Now.ToString("HH:mm:ss.fff");
        string formattedData = $"{currentTime},{data}";
        streamWriter.WriteLine(formattedData);
    }


    void Update(){
        if (Time.time - lastFlushTime >= flushInterval)
        {
            streamWriter.Flush();
            lastFlushTime = Time.time;
        }
    }


    private void OnDestroy(){
        if (streamWriter != null)
        {
            streamWriter.Flush();
            streamWriter.Close();
            streamWriter = null;
        }
    }
}
