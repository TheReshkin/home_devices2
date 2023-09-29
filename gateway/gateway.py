import sys

from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime

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

devices = {"pupa_lamp": "device"}


def write_log(log_message, log_file="gateway_log.txt"):
    with open(log_file, "a") as log:
        log.write(str(datetime.now().time()) + " -- " + str(log_message) + "\n")


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
            write_log(f"Received data from {remote_addr}. DeviceName: {dev_name}, Data: {req}")
        except Exception:
            print(f"Received data from {remote_addr}. ")

        # Отправляем данные на головной контроллер Home Assistant
        response = requests.post(
            f"http://{HOME_ASSISTANT_HOST}:{HOME_ASSISTANT_PORT}/",
            json=data
        )
        write_log(data)

        if response.status_code == 200:
            return "Success. connected to Home Assistant", 200
        else:
            return "Failed to communicate with Home Assistant", 500

    except Exception as e:
        print(e)
        return str(e), 500


# обработчик запросов от home_assistant
@app.route("/manage", methods=["POST"])
def receive_data():
    global state
    try:
        data = request.json
        remote_addr = request.remote_addr
        try:
            state_req = data.get('state')
            code = data.get('code')
            # скорее как затычка, должен сравнивать с данными в бд, которой нет :)
            device = data.get('device')
            write_log(code)
            if code is None or code != 123 or remote_addr != HOME_ASSISTANT_HOST:
                write_log("/manage" + "Auth error")
                return jsonify(result="Auth error")
            else:
                if state_req == 'off':
                    state = "OFF"
                    result = 'State: off'
                    response = requests.post(f"http://{device}/manage", json={
                        "state": "OFF",
                        "code": 123
                    }, headers={
                        "Content-Type": "application/json"
                    })
                    write_log(f"Send data to {device} code: " + str(response.status_code))
                    write_log("curr state" + str(state))
                elif state_req == 'on':
                    state = "ON"
                    result = 'State: On'
                    response = requests.post(f"http://{device}/manage", json={
                        "state": "ON",
                        "code": 123
                    }, headers={
                        "Content-Type": "application/json"
                    })
                    write_log(f"Send data to {device} code: " + str(response.status_code))
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
            write_log(f"Received auth data from {remote_addr}. DeviceName: {name}, Dev_type: {dev_type}")
            write_log("Success 200")
            devices[name] = remote_addr
            return "Success", 200
        except Exception:
            write_log(f"Received data from {remote_addr}.")
            return str(f"Received data from {remote_addr}.")

    # добавить создание rsa ключа и токена

    except Exception as e:
        write_log("Все сломалось в аутентификации ")
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=GATEWAY_PORT)  # Замените на нужный вам порт шлюза
