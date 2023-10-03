import os
import paho.mqtt.client as mqtt

BROKER = os.environ.get("BROKER")
BROKER_PORT = int(os.environ.get("BROKER_PORT"))

print(BROKER)
print(BROKER_PORT)


topic = "device"


# Функция, которая будет вызвана при получении нового сообщения
def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')  # Декодируем байты в строку
    print(f"Получено сообщение на теме '{topic}': {payload}")


if __name__ == '__main__':
    client = mqtt.Client(client_id="home_assistant", clean_session=True, userdata=None, transport="tcp")

    client.on_message = on_message
    client.connect(BROKER, BROKER_PORT)
    client.subscribe(topic)
    client.loop_forever()
