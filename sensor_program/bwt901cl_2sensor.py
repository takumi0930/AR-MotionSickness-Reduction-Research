from class_bwt901cl import BWT901CL
import os
import datetime
from time import sleep
import socket
import threading
from pynput import keyboard
from pynput.keyboard import Key
from functools import partial


def read_sensor_data(sensor, stop_event):
    while not stop_event.is_set():
        sensor._readData()
    print("thread end:", sensor.port)


def keyboard_listener(sock, UDP_IP, UDP_PORT, stop_event):
    # stop_event を on_press_with_args に追加
    on_press_with_args = partial(on_press, sock, UDP_IP, UDP_PORT, stop_event)
    with keyboard.Listener(on_press=on_press_with_args) as listener:
        while not stop_event.is_set():
            sleep(0.1)  # 小さなスリープでCPU使用率を下げる
        listener.stop()  # ストップイベントがセットされたらlistenerを停止
    print("keyboard listener thread end")


def on_press(sock, UDP_IP, UDP_PORT, stop_event, key):
    # if stop_event.is_set():  # ストップイベントがセットされていればListenerを停止
    #     return False
    try:
        if key == Key.esc:
            print("\nkeyboard listener finished.\n")
            return False  # Listenerを停止する
        
    except AttributeError:
        pass


def main():

    while True:
        try:
            # ポート変更 
            sensor1 = BWT901CL("COM3") # 1 ハンドル
            sensor2 = BWT901CL("COM9") # 2 車
            break
        except Exception as e:
            print(e)
            continue

    # IPv4アドレスとポート番号を指定、通信用socketを作成
    #UDP_IP = '127.0.0.1'
    #UDP_IP = '192.168.100.49'
    UDP_IP = '172.20.10.6'
    UDP_PORT = 9000 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # csv フォルダが存在しない場合は作成
    if not os.path.exists('csv'):
        os.makedir('csv')

    current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    folder = 'csv'
    filename = f'sensorData_{current_time}.csv'
    file_path = os.path.join(folder, filename)


    with open(file_path, 'w', buffering=1) as file:
        header = 'Time, AngVelZ1, AngVelZ2, AngZ1, AngZ2\n'
        file.write(header)
        
        # スレッド終了用のイベントを作成
        stop_event = threading.Event()

        # 各センサーのデータ読み取り用スレッドを作成
        thread1 = threading.Thread(target=read_sensor_data, args=(sensor1, stop_event))
        thread2 = threading.Thread(target=read_sensor_data, args=(sensor2, stop_event))

        # キーボードリスナーのスレッドを作成
        thread3 = threading.Thread(target=keyboard_listener, args=(sock, UDP_IP, UDP_PORT, stop_event))

        # スレッドをスタート
        thread1.start()
        thread2.start()
        thread3.start()

        last_flush_time = datetime.datetime.now()

        try:
            while True:
                # 受信
                s1_angVel = sensor1.getAngularVelocity()
                s2_angVel = sensor2.getAngularVelocity()
                s1_angle = sensor1.getAngle()
                s2_angle = sensor2.getAngle()
                

                # 送信 手法2 角速度累積
                msg1 = 'ANGVEL1 ' + str(s1_angVel[2]) # ハンドル角速度
                msg2 = 'ANGVEL2 ' + str(s2_angVel[2]) # 車角速度
                sock.sendto(msg1.encode(), (UDP_IP, UDP_PORT))
                sock.sendto(msg2.encode(), (UDP_IP, UDP_PORT))

                # 送信 手法3 角速度
                #msg = str(s1_angVel[2]) + ' ' + str(s2_angVel[2]) # ハンドル角速度 車角速度
                #ock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
                
                # 出力
                time_stamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(time_stamp, " | ", s1_angVel[2], " | ", s2_angVel[2], " | ", s1_angle[2], " | ", s2_angle[2])
                file.write(f'{time_stamp}, {s1_angVel[2]}, {s2_angVel[2]}, {s1_angle[2]}, {s2_angle[2]}\n')
                
                # フラッシュ
                if (datetime.datetime.now() - last_flush_time) > datetime.timedelta(seconds=60):
                    file.flush()
                    last_flush_time = datetime.datetime.now()
                    
                # 受送信間隔調整 -----------------------------------------------
                sleep(0.05)
                # -----------------------------------------------------------------^-


        except KeyboardInterrupt:
            print("KeyboardInterrupt: stop process")
            # スレッド終了イベントを設定
            stop_event.set()
            # スレッド終了待機
            thread1.join()
            thread2.join()
            thread3.join()
            # センサーを停止
            sensor1.stop()
            sensor2.stop()
            # ファイルをフラッシュ
            file.flush()
            print("file flush")


if __name__ == "__main__":
    main()
