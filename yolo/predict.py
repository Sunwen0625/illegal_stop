import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import time


# 發佈訊息的方法
def publish_message(client:mqtt.Client,msg: str) -> None:
    topic = "sunwen_get"
    
    client.publish(topic, msg, qos=2)
    print(f"已發佈訊息到主題 '{topic}': {msg}")
    time.sleep(5)

def init_mqtt() -> mqtt.Client:
    """連線網址 tcp://broker.emqx.io:1883

    Returns:
        mqtt.Client: 實例化且初始化Client物件
    """
    client = mqtt.Client()
    client.connect("broker.emqx.io", 1883, 60)
    return client


def load_model(model) -> YOLO:
    model = YOLO(model)
    return model    

def init_fram(frame:int|str) -> cv2.VideoCapture:
    """
    選擇載入畫面\n
    int: 預設攝影機  || str: 網址|影片 \n
    example : http://192.168.96.180:8080/video
    """
    #載入攝影機
    cap = cv2.VideoCapture(frame)
    # 设置窗口大小
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def on_detection(detected_count,client:mqtt.Client) -> None:
    def is_detected(detected_count:list) -> bool:
        # 检查是否检测到了物体
        detected = False
        if detected_count is not None:
            detected = len(detected_count) > 0
        return detected
    
    
    detected =is_detected(detected_count)
    if detected :
        print("检测到物体")
        publish_message(client,"True")
    else:
        print("未检测到物体")
        publish_message(client,"False")

def main(FRAME , model) -> None:
    """
    執行辨識yolo

    Args:
        FRAME (_type_): 影像畫面
        model (_type_): yolo 模型
    """
    client = init_mqtt()
    client.loop_start()
    
    model = load_model(model)
    cap = init_fram(FRAME)
    

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("无法读取视频流")
            break
        results = model.predict(frame)
        detected_count = results[0].boxes
        on_detection(detected_count,client)
        # 绘制检测结果
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO", annotated_frame) 
        if cv2.waitKey(1) == ord('q'):
            break
    client.loop_stop()
    cap.release()

    
if __name__ == "__main__":
    FRAME = 0
    MODEL = "yolov8s.pt"
    main(FRAME,MODEL)