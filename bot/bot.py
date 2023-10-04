import paho.mqtt.client as mqtt
import telebot

MQTT_BROKER_HOST = "mosquitto"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "device"

# Здесь укажите токен вашего Telegram бота
TELEGRAM_BOT_TOKEN = "BOT_API"

# Создаем MQTT клиент
mqtt_client = mqtt.Client(client_id="telebot", clean_session=True, transport="tcp")

# Создаем Telegram бот
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Функция, которая будет вызываться при получении сообщения от MQTT
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    # Обработка полученных данных
    if payload == "ON":
        send_message("Устройство включено")
    elif payload == "OFF":
        send_message("Устройство выключено")


# Подключаем функцию on_message к MQTT клиенту
mqtt_client.on_message = on_message


def send_message(text):
    bot.send_message(chat_id, text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Вы можете управлять устройством с помощью этого бота.")

@bot.message_handler(commands=['on'])
def turn_on(message):
    mqtt_client.publish(MQTT_TOPIC, '{"device":"lamp", "state": "ON"}')

@bot.message_handler(commands=['off'])
def turn_off(message):
    # Отправляем команду выключения в MQTT
    mqtt_client.publish(MQTT_TOPIC, '{"device":"lamp", "state": "OFF"}')


# Запускаем MQTT клиент
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()

# Запускаем Telegram бота
bot.polling()
