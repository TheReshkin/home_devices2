import sys

from flask import Flask, request, jsonify, render_template
import logging

app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

device_types = ["humidity sensor", "thermometer", "socket", "switch", "lamp"]


# # Функция для перенаправления print в логи
# def print_to_log(msg):
#     logger.info(msg)
#
#
# # Перенаправление stdout в логи
# sys.stdout.write = print_to_log


@app.route('/', methods=['POST'])
def get_data():
    if request.method == 'POST':
        # Получение данных из POST-запроса
        data = request.json  # Предполагается, что данные в формате JSON

        # Отправка ответа
        response_data = {
            'message': 'Запрос получен и обработан успешно',
            'received_data': data
        }
        print(response_data)
        return jsonify(response_data), 200  # Ответ в формате JSON и статус HTTP 200 (OK)


# управление устройствами
@app.route('/turn_on')
def turn_on():
    global device_state
    device_state = "on"
    return render_template('index.html', device_state=device_state)


@app.route('/turn_off')
def turn_off():
    global device_state
    device_state = "off"
    return render_template('index.html', device_state=device_state)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
