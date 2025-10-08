using UnityEngine;
using System;
using System.Collections.Concurrent;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

public class UDPReceiver : MonoBehaviour
{
    [SerializeField] private DataProcessor dataProcessor;

    private const int port = 9000;
    private UdpClient udpClient;
    private bool isServerRunning = false;

    private ConcurrentQueue<string> receivedQueue = new ConcurrentQueue<string>();

    private async void Start()
    {
        await StartServerAsync();
    }

    private async Task StartServerAsync()
    {
        if (isServerRunning)
            return;

        udpClient = new UdpClient(port);
        isServerRunning = true;
        Debug.Log("UDPReceiver started on port " + port);

        while (isServerRunning)
        {
            try{
                UdpReceiveResult result = await udpClient.ReceiveAsync();
                string receivedData = Encoding.ASCII.GetString(result.Buffer);
                // 受信キューにデータを格納する
                receivedQueue.Enqueue(receivedData);
            }
            catch (Exception e){
                Debug.LogError("UDP receive error: " + e);
            }
        }
    }

     private void Update()
    {
        // 受信キューからデータを取り出して処理させる
        while (receivedQueue.TryDequeue(out string data)){
            dataProcessor.ProcessReceivedData(data);
        }
    }

    private void OnApplicationQuit()
    {
        isServerRunning = false;
        udpClient?.Close();
    }
}
