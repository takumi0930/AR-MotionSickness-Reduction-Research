using UnityEngine;
using System;
using Microsoft.MixedReality.Toolkit.SpatialManipulation;

public class DataProcessor : MonoBehaviour
{
    [SerializeField] private GameObject right_bar;
    [SerializeField] private GameObject left_bar;
    [SerializeField] private CSVWriter _csvWriter;

    private float handle_angvel = 0f;
    private float vehicle_angvel = 0f;
    private float handle_pure_angvel = 0f;
    private int display_state = 0; // 表示状態 左-1 非表示0 右1
    private int old_display_state = 0; // 表示状態 左-1 非表示0 右1

    private Material right_bar_mat;
    private Material left_bar_mat;
    Color32 colorZero = new Color32(29, 161, 242, 0); // 非表示
    Color32 colorBright = new Color32(29, 161, 242, 255); // 表示

    private void Start()
    {
        right_bar_mat = right_bar.GetComponent<MeshRenderer>().material;
        left_bar_mat = left_bar.GetComponent<MeshRenderer>().material;
    }

    public void ProcessReceivedData(string data)
    {
        StoreReceivedData(data);
        UpdateBarDisplay();
        _csvWriter.WriteToCSV(handle_pure_angvel + ", " + display_state);
    }

    private void StoreReceivedData(string data)
    {
        string[] parts = data.Split(' ');
        if(parts.Length != 2) return;

        try{
            handle_angvel = -float.Parse(parts[0]);
            vehicle_angvel = -float.Parse(parts[1]);
        }
        catch (Exception e){
            Debug.LogWarning("データ処理エラー: " + data + " - " + e.Message);
        }

        handle_pure_angvel = handle_angvel - vehicle_angvel;
    }

    private void UpdateBarDisplay()
    {
        // ハンドル角速度により表示状態を設定する
        if(handle_pure_angvel >= 30f)
            display_state = 1;
        else if(handle_pure_angvel > -30f)
            display_state = 0;
        else
            display_state = -1;

        // 表示状態に変更がなければ、return
        if(display_state == old_display_state){
            old_display_state = display_state;
            return;
        }

        // 表示状態に応じて、色を変更する
        switch(display_state){
            case 1:
                right_bar_mat.SetColor("_Color", colorBright);
                left_bar_mat.SetColor("_Color", colorZero);
                break;
            
            case 0:
                right_bar_mat.SetColor("_Color", colorZero);
                left_bar_mat.SetColor("_Color", colorZero);
                break;
            
            case -1:
                right_bar_mat.SetColor("_Color", colorZero);
                left_bar_mat.SetColor("_Color", colorBright);
                break;
            
            default:
                break;
        }

        // 表示状態を更新する
        old_display_state = display_state;
    }
}
