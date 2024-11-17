import paho.mqtt.client as mqtt
import json


# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # 訂閱主題
    client.subscribe("sunwen_gps")

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print(f"收到的訊息: {msg.topic} - {message}")
    try:
        # 將 JSON 格式的文字轉換成字典
        data = json.loads(message)
        print(f"轉換後的字典: {data}")
        print(f"經度: {data['經度']}, 緯度: {data['緯度']}")
    except json.JSONDecodeError as e:
        print(f"無法解析 JSON: {e}")

# 發佈訊息的方法
def publish_message(client):
    topic = "sunwen_get"
    while True:
        # 從使用者輸入訊息
        message = input("請輸入要傳輸的訊息 (輸入 'exit' 離開): ")
        if message.lower() == "exit":
            print("已結束發佈訊息。")
            break
        client.publish(topic, message)
        print(f"已發佈訊息到主題 '{topic}': {message}")

# MQTT 客戶端執行緒
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.emqx.io", 1883, 60)

    # 啟動 MQTT 迴圈
    client.loop_start()
    publish_message(client)
    client.loop_stop()
    client.disconnect()



