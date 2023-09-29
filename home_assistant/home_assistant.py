import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)
global device_state
global gateway_host
device_types = ["humidity sensor", "thermometer", "socket", "switch", "lamp"]


def write_log(log_message, log_file="home_assistant_log.txt"):
    with open(log_file, "a") as log:
        log.write(str(datetime.now().time()) + " -- " + str(log_message) + "\n")


def update_state(state):
    response = requests.post(f"http://{gateway_host}/manage", json={"state": state, "code": 123, "device": "device"},
                             headers={"Content-Type": "application/json"})

    return response.status_code


@app.route('/receive', methods=['POST'])
def get_data():
    data = request.json
    remote_addr = request.remote_addr
    if request.method == 'POST':
        # Получение данных из POST-запроса

        # Отправка ответа
        response_data = {
            'message': 'Запрос получен и обработан успешно',
            'received_data': data
        }
        write_log(str(response_data))
        return jsonify(response_data), 200  # Ответ в формате JSON и статус HTTP 200 (OK)
    else:
        write_log(f" Request from {remote_addr}. Data: {data}")
        return jsonify("Wrong method"), 400


# управление устройствами
@app.route('/turn_on')
def turn_on():
    device_state = "on"
    update_state(device_state)
    return render_template('index.html', device_state=device_state)


@app.route('/turn_off')
def turn_off():
    device_state = "off"
    update_state(device_state)
    return render_template('index.html', device_state=device_state)


@app.route("/auth", methods=["POST"])
def auth():
    global gateway_host
    try:
        # Получаем данные из входящего HTTP запроса
        data = request.json
        remote_addr = request.remote_addr

        try:
            name = data["params"]["auth"]["Name"]
            dev_type = data["params"]["auth"]["Device_type"]
            gateway_host = remote_addr
            write_log(f"Received auth data from {remote_addr}. DeviceName: {name}, Dev_type: {dev_type}")
            write_log("Success 200")

            return "Success", 200
        except Exception:
            write_log(f"Received data from {remote_addr}.")
            return str(f"Received data from {remote_addr}.")

    # добавить создание rsa ключа и токена

    except Exception as e:
        write_log("Все сломалось в аутентификации ")
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
