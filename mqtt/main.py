import paho.mqtt.client as mqtt
import json


# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client:mqtt.Client, userdata, flags, rc,properties=None):
    print("Connected with result code "+str(rc))
    # 訂閱主題
    client.subscribe("sunwen_gps",qos=2)

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
    message = msg.payload.decode('utf-8')
    print(f"收到的訊息: {msg.topic} - {message}")
    try:
        # 將 JSON 格式的文字轉換成字典
        data = json.loads(message)
        print(f"轉換後的字典: {data}")
        print(f"經度: {data['經度']}, 緯度: {data['緯度']}")
    except json.JSONDecodeError as e:
        print(f"無法解析 JSON: {e}")


def init_mqtt() -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,protocol=mqtt.MQTTv5, )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.emqx.io", 1883, 60)
    return client

# MQTT 客戶端執行緒
def mqtt_thread():
    client = init_mqtt()

    # 啟動 MQTT 迴圈
    client.loop_forever()


if __name__ == '__main__':
    mqtt_thread()


