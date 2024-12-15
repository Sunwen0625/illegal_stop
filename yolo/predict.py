import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import threading
import time
from queue import Queue


def init_mqtt() -> mqtt.Client:
    """初始化 MQTT 客戶端並連線到伺服器"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("broker.emqx.io", 1883, 60)
    client.loop_start()  # 在初始化時啟動 loop
    return client


def initialize_video_capture(source: int | str) -> cv2.VideoCapture:
    """
    初始化影像來源
    Args:
        source (int | str): 預設攝影機 (int) 或影像來源網址/檔案路徑 (str)
    Returns:
        cv2.VideoCapture: 已初始化的 VideoCapture 對象
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频来源: {source}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def load_yolo_model(model_path: str) -> YOLO:
    """
    加載 YOLO 模型
    Args:
        model_path (str): YOLO 模型路徑
    Returns:
        YOLO: 已加載的 YOLO 模型
    """
    return YOLO(model_path)


def publish_message(client: mqtt.Client, detection_queue: Queue) -> None:
    """
    循環發佈檢測結果到 MQTT 主題
    Args:
        client (mqtt.Client): MQTT 客戶端
        detection_queue (Queue): 檢測結果隊列
    """
    topic = "sunwen_get"
    while True:
        # 清空佇列中所有舊的結果，只取最新的
        while not detection_queue.empty():
            try:
                detection_queue.get_nowait()
            except Exception:
                pass
        # 取最新結果
        detected = detection_queue.get()  # 這裡是阻塞的，直到有結果進入佇列
        message = "检测到物体" if detected else "未检测到物体"
        print(message)
        client.publish(topic, detected, qos=2)
        print(f"已發佈訊息到主題 '{topic}': {detected}")
        time.sleep(5)


def process_frames(model: YOLO, cap: cv2.VideoCapture, detection_queue: Queue) -> None:
    """
    循環處理影像幀並進行物體檢測
    Args:
        model (YOLO): YOLO 模型
        cap (cv2.VideoCapture): 影像來源
        detection_queue (Queue): 檢測結果隊列
    """
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("无法读取视频流")
            break

        results = model.predict(frame)
        detected = len(results[0].boxes) > 0
        detection_queue.put(detected)  # 將檢測結果放入佇列

        # 繪製檢測結果
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO", annotated_frame)

        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    #FRAME_SOURCE = "http://192.168.71.66:8080/video"  # 攝影機
    FRAME_SOURCE = 0
    MODEL_PATH = "yolov8s.pt"  # 模型檔案

    # 初始化 MQTT 客戶端
    client = init_mqtt()

    # 初始化 YOLO 模型和影像來源
    model = load_yolo_model(MODEL_PATH)
    cap = initialize_video_capture(FRAME_SOURCE)

    # 使用佇列進行檢測結果通信
    detection_queue = Queue()

    # 啟動發佈訊息的執行緒
    threading.Thread(target=publish_message, args=(client, detection_queue), daemon=True).start()

    # 處理影像幀
    process_frames(model, cap, detection_queue)

    # 清理 MQTT 客戶端
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
