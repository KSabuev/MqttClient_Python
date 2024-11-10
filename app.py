# t=69
# u=0.34;0.34;233.06
# i=0.00;0.00;0.00
# c=0.00;0.00;0.00
# f=49.97

import os
from dotenv import load_dotenv
import psycopg2
import paho.mqtt.client as mqtt

load_dotenv()
db_config = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}


def connect_to_db():
    conn = psycopg2.connect(**db_config)
    return conn


def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS e_data (
        id SERIAL PRIMARY KEY,
        timestamp integer,
        current_1 FLOAT,
        current_2 FLOAT,
        current_3 FLOAT,
        voltage_1 FLOAT,
        voltage_2 FLOAT,
        voltage_3 FLOAT,
        cos_phi_1 FLOAT,
        cos_phi_2 FLOAT,
        cos_phi_3 FLOAT,
        frequency FLOAT
    );
    '''

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()


def insert_data(timestamp, currents, voltages, cos_phis, frequency):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = '''
    INSERT INTO e_data (timestamp, current_1, current_2, current_3, voltage_1, voltage_2, voltage_3, cos_phi_1, cos_phi_2, cos_phi_3, frequency) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

    cursor.execute(insert_query, (
        timestamp, currents[0], currents[1], currents[2], voltages[0], voltages[1], voltages[2], cos_phis[0],
        cos_phis[1],
        cos_phis[2], frequency))
    conn.commit()
    cursor.close()
    conn.close()


def parse_message(msg):
    messages = msg.split('\n@')

    parsed_data = []

    for message in messages:
        if not message.strip():
            continue

        lines = message.strip().split('\n')

        timestamp = None
        currents = []
        voltages = []
        cos_phis = []
        frequency = None

        for item in lines:
            if item.startswith('t='):
                timestamp = item[2:].strip()  # Получаем временную метку
            elif item.startswith('i='):
                currents = list(map(float, item[2:].replace(',', '.').split(';')))  # Токи
            elif item.startswith('u='):
                voltages = list(map(float, item[2:].split(';')))  # Напряжения
            elif item.startswith('c='):  # Исправлено: cosF -> c
                cos_phis = list(map(float, item[2:].split(';')))  # Коэффициенты мощности
            elif item.startswith('f='):
                frequency = float(item[2:])  # Частота

        parsed_data.append((timestamp, currents, voltages, cos_phis, frequency))

    return parsed_data


def on_message(client, userdata, msg):
    print(f"Получено сообщение: Топик: {msg.topic}, Сообщение: {msg.payload.decode()}")

    parsed_data = parse_message(msg.payload.decode())

    for data in parsed_data:
        timestamp, currents, voltages, cos_phis, frequency = data
        insert_data(timestamp, currents, voltages, cos_phis, frequency)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Успешное подключение к MQTT брокеру")
        client.subscribe("user_da71e189/Mercury/Confirm")
    else:
        print(f"Ошибка подключения: {rc}")


def main():
    create_table()

    mqtt_broker = os.getenv('MQTT_BROKER')
    mqtt_port = int(os.getenv('MQTT_PORT'))
    mqtt_username = os.getenv('MQTT_USERNAME')
    mqtt_password = os.getenv('MQTT_PASSWORD')

    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_password)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()
