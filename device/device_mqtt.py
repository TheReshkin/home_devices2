import time
import os
import paho.mqtt.client as mqtt

BROKER = os.environ.get("BROKER")
BROKER_PORT = int(os.environ.get("BROKER_PORT"))
topic = os.environ.get("TOPIC")
client_id = os.environ.get("CLIENT_ID")

# broker = f"tcp://{BROKER}:{BROKER_PORT}"
state = "OFF"


class Time:
    def __init__(self):
        self.start = time.time()  # точка отсчета времени
        self.last_req = time.time()

    def get_last_req(self):
        time_between = time.time() - self.last_req
        self.last_req = time.time()
        return time_between

    def get_time_run(self):
        return time.time() - self.start


def main():
    while True:
        try:
            client = mqtt.Client(client_id=client_id, clean_session=True, transport="tcp")
            client.connect(BROKER, BROKER_PORT)
            print(f"Sending data to the broker {BROKER} {run_time.get_time_run()}")

            device_data = {
                "device_id": f"{client_id}",
                "request": {
                    "state": f"{state}",
                    "runtime": f"{run_time.get_time_run()}",  # Время работы в секундах
                    "time_between_req": f"{run_time.get_last_req()}",
                    "data": "Some data"
                }
            }
            client.publish(topic, str(device_data))
            print(client_id + " send data")
            client.disconnect()
        except Error as e:
            print(e)
            time.sleep(5)
            main()
        time.sleep(10)

run_time = Time()
main()
