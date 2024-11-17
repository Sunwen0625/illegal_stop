import threading
import cv2
import mqtt.main as mqtt

# OpenCV 相機顯示執行緒
def opencv_thread():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟相機")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取影像")
            break

        # 顯示畫面
        cv2.imshow("Camera", frame)

        # 按下 'q' 鍵退出相機顯示
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("退出相機顯示")
            break

    cap.release()
    cv2.destroyAllWindows()

# 主程式入口
if __name__ == "__main__":
    # 建立 MQTT 與 OpenCV 的執行緒
    mqtt_thread_obj = threading.Thread(target=mqtt.mqtt_thread)
    opencv_thread_obj = threading.Thread(target=opencv_thread)

    # 啟動執行緒
    mqtt_thread_obj.start()
    opencv_thread_obj.start()

    # 等待執行緒結束
    mqtt_thread_obj.join()
    opencv_thread_obj.join()