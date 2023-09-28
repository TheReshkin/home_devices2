import sys

from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Адрес и порт головного контроллера Home Assistant
HOME_ASSISTANT_HOST = os.environ.get('HOME_ASSISTANT_HOST')
HOME_ASSISTANT_PORT = os.environ.get('HOME_ASSISTANT_PORT')

GATEWAY_PORT = os.environ.get('GATEWAY_PORT')
# Путь, на который будут поступать запросы к шлюзу
GATEWAY_ENDPOINT = "/gateway"
AUTH_ENDPOINT = "/auth"


# device_types = ["humidity sensor", "thermometer", "socket", "switch", "lamp"]
# # Функция для перенаправления print в логи
# def print_to_log(msg):
#     logger.info(msg)
#
#
# # Перенаправление stdout в логи
# sys.stdout.write = print_to_log


@app.route(GATEWAY_ENDPOINT, methods=["POST"])
def gateway():
    try:
        # Получаем данные из входящего HTTP запроса
        data = request.json
        args = request.args
        headers = request.headers
        remote_addr = request.remote_addr
        try:
            dev_name = data["params"]["device_name"]
            req = data["params"]["request"]
            print(f"Received data from {remote_addr}. DeviceName: {dev_name}, Data: {req}")
        except Exception:
            print(f"Received data from {remote_addr}. ")

        # Отправляем данные на головной контроллер Home Assistant
        response = requests.post(
            f"http://{HOME_ASSISTANT_HOST}:{HOME_ASSISTANT_PORT}/",
            json=data
        )
        print(data)

        if response.status_code == 200:
            return "Success", 200
        else:
            return "Failed to communicate with Home Assistant", 500

    except Exception as e:
        print(e)
        return str(e), 500


@app.route(AUTH_ENDPOINT, methods=["POST"])
def auth():
    try:
        # Получаем данные из входящего HTTP запроса
        data = request.json
        remote_addr = request.remote_addr
        print(data)
        print(data["params"]["auth"]["Name"])
        try:
            name = data["params"]["auth"]["Name"]
            dev_type = data["params"]["auth"]["Device_type"]
            print(f"Received auth data from {remote_addr}. DeviceName: {name}, Dev_type: {dev_type}")
            return "Success", 200
        except Exception:
           return str(f"Received data from {remote_addr}.")

    # добавить создание rsa ключа и токена

    except Exception as e:
        print("Все сломалось в аутентификации ")
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=GATEWAY_PORT)  # Замените на нужный вам порт шлюза
