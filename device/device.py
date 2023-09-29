from flask import Flask, request, jsonify
import requests
import os
import time
import socket
import threading

from datetime import datetime

# # библиотеки для шифрования данных
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)

# Адрес и порт шлюза
GATEWAY_HOST = os.environ.get('GATEWAY_HOST')
GATEWAY_PORT = os.environ.get('GATEWAY_PORT')
DEVICE_NAME = os.environ.get('DEVICE_NAME')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE')

# глобальные состояния устройства
global state
device_types = ["humidity_sensor", "thermometer", "socket", "switch", "lamp"]


def write_log(log_message, log_file="device_log.txt"):
    with open(log_file, "a") as log:
        log.write(str(datetime.now().time()) + " -- " + str(log_message) + "\n")


# обработчик запросов от gateway
@app.route("/manage", methods=["POST"])
def receive_data():
    global state
    try:
        # Получаем данные из входящего HTTP запроса
        data = request.json

        remote_addr = request.remote_addr
        try:
            state_req = data.get('state')
            code = data.get('code')
            write_log(code)
            if code is None or code != 123:
                write_log("/manage" + "Auth error")
                return jsonify(result="Auth error")
            else:
                if state_req == 'off':
                    state = "OFF"
                    result = 'State: off'
                    write_log("curr state" + str(state))
                elif state_req == 'on':
                    state = "ON"
                    result = 'State: On'
                    write_log("curr state" + str(state))
                else:
                    result = "wrong param state"
                # Верните ответ в формате JSON
                write_log("/manage " + str(data))
                return jsonify(result=result)
        except Exception:
            write_log(f"Received data from {remote_addr}. ")

        write_log(data)

    except Exception as e:
        print(e)
        return str(e), 500


def send_data():
    # remote_addr = request.remote_addr
    # print(remote_addr)
    # if remote_addr not in white_list:
    #     response = {"ERROR": 1, "status": "unauthorized host"}
    #     return jsonify(response), 200
    while True:
        print(f"Sending data to the gateway {GATEWAY_HOST} {run_time.get_time_run()}")
        try:
            global state
            state = "OFF"
            # парсинг намерений отправителя (проверка есть ли отправитель в белом списке)
            # обмен rsa ключом
            # дешифровка rsa ключом

            device_data = {
                "params": {
                    "device_name": f"{DEVICE_NAME}",
                    "request": {
                        "state": f"{state}",  # Состояние устройства (включено)
                        "runtime": f"{run_time.get_time_run()}",  # Время работы в секундах
                        "time_between_req": f"{run_time.get_last_req()}",
                        "data": "Some data"
                    }
                }
            }
            response = requests.post(f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/gateway", json=device_data)
            print(response.status_code)
            # write_log(response.status_code)
        except Exception as e:
            print(e)
            write_log(e)
            return str(e), 500
        time.sleep(60)


def auth_request():
    # инициатор подключения устройство, оно отправляет запрос на подключение,
    # шлюз возвращает публичный rsa ключ, шлюз добавляется в белый список, дальнейшее общение шифруется
    # временное добавление в белый список
    white_list = [socket.gethostbyname(GATEWAY_HOST)]
    print("WhiteList: " + str(white_list))
    write_log("WhiteList: " + str(white_list))
    try:
        print('auth_request')
        device_data = {
            "params": {
                "auth": {
                    "Name": f"{DEVICE_NAME}",
                    "Device_type": f"{DEVICE_TYPE}",
                    "data": "Auth data"

                }
            }
        }
        response = requests.post(f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/auth", json=device_data)
        write_log(response.status_code)


    except Exception as e:
        print(e)
        write_log(e)
        # ждет 5 сек и снова пытается авторизоваться
        time.sleep(5)
        auth_request()
        # return str(e), 500


# поменять библиотеку, в контейнере не робит
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


class Encrypt:
    def __init__(self):
        # Генерация ключей для асимметричной криптографии
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.public_key2 = None

    # сериализация для отправки публичного ключа
    def serialize_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_public_key(self, public_key2_bytes):
        self.public_key2 = serialization.load_pem_public_key(public_key2_bytes)

    def encrypt_data(self, data):
        return data.encrypt(
            self.public_key2,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None  # Добавьте этот аргумент label и установите его в None
            ))


if __name__ == "__main__":
    run_time = Time()
    print("device up")
    print(f"{GATEWAY_HOST}, {GATEWAY_PORT}, {DEVICE_NAME}")
    # авторизация
    auth_request()
    # отправка данных на шлюз
    periodic_thread = threading.Thread(target=send_data)
    periodic_thread.daemon = True
    periodic_thread.start()
    app.run(host="0.0.0.0", port=GATEWAY_PORT)
