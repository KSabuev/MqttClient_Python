# Описание проекта

Данный проект представляет собой Python-скрипт для приема и обработки данных о параметрах электрической сети через MQTT-протокол. Данные сохраняются в базе данных PostgreSQL, а подключение к базе данных и MQTT-брокеру настраивается через `.env` файл.

## Установка и запуск

### Требования

- Python 3.x
- PostgreSQL
- Установленные пакеты из `requirements.txt`

### Настройка окружения

1. Создайте `.env` файл в корне проекта и добавьте следующие переменные:

   ```plaintext
   DB_NAME=название_базы_данных
   DB_USER=пользователь_базы_данных
   DB_PASSWORD=пароль_пользователя
   DB_HOST=хост_базы_данных
   DB_PORT=порт_базы_данных

   MQTT_BROKER=адрес_MQTT_брокера
   MQTT_PORT=порт_MQTT_брокера
   MQTT_USERNAME=имя_пользователя
   MQTT_PASSWORD=пароль
   ```
   
2. Установите необходимые зависимости:

    pip install -r requirements.txt

3. Запустите скрипт:

    python main.py


Скрипт автоматически создает таблицу e_data, если она не существует. Таблица хранит следующие данные:

    id — уникальный идентификатор записи.
    timestamp — временная метка.
    current_1, current_2, current_3 — значения тока для трех фаз.
    voltage_1, voltage_2, voltage_3 — значения напряжения для трех фаз.
    cos_phi_1, cos_phi_2, cos_phi_3 — коэффициенты мощности для каждой фазы.
    frequency — частота сети.

Основные функции:

    connect_to_db(): устанавливает подключение к базе данных.
    create_table(): создает таблицу e_data, если она еще не существует.
    insert_data(): вставляет данные в таблицу e_data.
    parse_message(msg): парсит входящее сообщение и извлекает из него временную метку, токи, напряжения, коэффициенты мощности и частоту.
    on_message(client, userdata, msg): функция-обработчик сообщений, полученных через MQTT. Парсит и вставляет данные в базу.
    on_connect(client, userdata, flags, rc): функция, вызываемая при успешном подключении к MQTT-брокеру.
    main(): основной скрипт, который инициализирует базу, настраивает и запускает MQTT-клиент.

Сообщения, получаемые от MQTT-брокера, имеют следующий формат:
   ```
t=69
u=0.34;0.34;233.06
i=0.00;0.00;0.00
c=0.00;0.00;0.00
f=49.97
   ```
Где:

    t — временная метка,
    u — напряжение (три значения),
    i — ток (три значения),
    c — коэффициенты мощности (три значения),
    f — частота.