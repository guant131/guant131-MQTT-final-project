from flask import Flask, request, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading
import json
import time
import random
import datetime
import sqlite3
import re

app = Flask(__name__)
# CORS(app, origins=["http://localhost:8080"], supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:8081"]}}, supports_credentials=True)
# 使用更广泛的 CORS 规则来解决跨域问题
# CORS(app, resources={r"/*": {"origins": ["http://localhost:8080"]}}, supports_credentials=True)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/device/<device>/<action>', methods=['OPTIONS'])
def preflight_handler(device, action):
    response = jsonify({'status': 'preflight ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


@app.route('/api/device/water_heater/on', methods=['OPTIONS'])
def preflight_water_heater_on():
    response = jsonify({'status': 'preflight ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


mqtt_client = None
received_messages = {}


def on_connect(client, userdata, flags, rc):
    print("连接结果: " + mqtt.connack_string(rc))


def update_device_status(device, mode=None, status=None):    #-----------------------------------------
    """
    更新数据库中设备的状态，并且发布 MQTT 消息同步到前端。
    """
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()

    # 更新模式
    if mode:
        cursor.execute("UPDATE device_control SET mode = ?, last_updated = CURRENT_TIMESTAMP WHERE device = ?",
                       (mode, device))

    # 更新状态
    if status:
        cursor.execute("UPDATE device_control SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE device = ?",
                       (status, device))

        # 🔥 发送 MQTT 消息同步
        topic = f"device/{device}/status"
        mqtt_client.publish(topic, status)
        print(f"MQTT Published: {topic} -> {status}")

    # 🔥 新增数据同步
    if status in ['BRIGHTER', 'DIMMER', 'OFF']:
        cursor.execute('''
            INSERT INTO light_control_data (intensity, status, timestamp)
            VALUES (?, ?, ?)
        ''', (random.uniform(100, 800), status.lower(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def on_message(client, userdata, msg):    #-----------------------------------------
    """
    处理接收到的 MQTT 消息并更新数据库状态
    """
    try:
        # 解析消息内容
        payload_str = msg.payload.decode('utf-8')
        payload_dict = json.loads(payload_str)
        topic = msg.topic

        # 添加时间戳（如果原消息未提供）
        if 'timestamp' not in payload_dict:
            payload_dict['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 保存消息记录
        if topic not in received_messages:
            received_messages[topic] = []
        received_messages[topic].append(payload_dict)

        # 处理 Lighting 的状态
        if topic == "device/lighting":
            command = payload_dict.get("command")
            if command == "BRIGHTER":
                update_device_status('lighting', 'on')
                print("[灯光控制] 增加亮度")
            elif command == "DIMMER":
                update_device_status('lighting', 'on')
                print("[灯光控制] 减少亮度")
            elif command == "OFF":
                update_device_status('lighting', 'off')
                print("[灯光控制] 关闭")

        # 处理 Water Heater 的状态
        elif topic == "device/water_heater":
            command = payload_dict.get("command")
            if command == "ON":
                update_device_status('water_heater', 'on')
                print("[热水器控制] 打开")
            elif command == "OFF":
                update_device_status('water_heater', 'off')
                print("[热水器控制] 关闭")

        # 处理 Surveillance Camera 的状态
        elif topic == "device/camera":
            command = payload_dict.get("command")
            if command == "ON":
                update_device_status('camera', 'on')
                print("[摄像头控制] 启动")
            elif command == "OFF":
                update_device_status('camera', 'off')
                print("[摄像头控制] 关闭")

        # 处理 FPS 和摄像头状态数据
        elif topic == "device/fps":
            save_fps_to_db(payload_dict.get("fps"), payload_dict["timestamp"])
        elif topic == "device/surveillance_camera":
            save_surveillance_camera_to_db(payload_dict.get("status"), payload_dict["timestamp"])

        # ✅ 处理 Air Conditioner 数据（确保字段存在）
        elif topic == "device/aircon":
            temperature = payload_dict.get("temperature")
            humidity = payload_dict.get("humidity")
            cooling_status = payload_dict.get("cooling_status")
            dehumidifying_status = payload_dict.get("dehumidifying_status")
            timestamp = payload_dict["timestamp"]

            # 仅当温度和湿度都存在时才写入数据库
            if temperature is not None and humidity is not None:
                save_aircon_to_db(temperature, humidity, cooling_status, dehumidifying_status, timestamp)
                print(f"[空调数据] 温度: {temperature}, 湿度: {humidity}, 冷却: {cooling_status}, 除湿: {dehumidifying_status}")
            else:
                print("[警告] 空调数据缺失，未写入数据库")

        # 输出收到的消息
        print(f"[收到消息] 主题: {topic}, 内容: {payload_dict}")

    except Exception as e:
        print(f"[错误] 解析消息失败: {e}")


def init_device_control_db():     #-----------------------------------------
    """
    Initialize the device_control database with the required schema and default values.
    """
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()

    # 创建表，如果不存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT NOT NULL,
            mode TEXT NOT NULL,
            status TEXT NOT NULL,
            manual_override TEXT DEFAULT 'off',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 查询是否已有数据
    cursor.execute("SELECT COUNT(*) FROM device_control")
    count = cursor.fetchone()[0]

    # 如果没有数据，则插入默认数据
    if count == 0:
        cursor.executemany('''
            INSERT INTO device_control (device, mode, status, manual_override) VALUES (?, ?, ?, ?)
        ''', [
            ('water_heater', 'auto', 'off', 'off'),
            ('lighting', 'auto', 'off', 'off'),
            ('camera', 'auto', 'off', 'off'),
            ('aircon', 'auto', 'off', 'off')
        ])
        print("✅ Database initialized with default device states.")
    else:
        print("✅ Database already initialized.")

    conn.commit()
    conn.close()



@app.route('/api/device/<device>/<action>', methods=['POST'])    #-----------------------------------------
def control_device(device, action):
    try:
        conn = sqlite3.connect('device_control.db')
        cursor = conn.cursor()

        # 修正映射
        status_mapping = {
            'brighter': 'BRIGHTER',
            'dimmer': 'DIMMER',
            'off': 'OFF',
            'on': 'ON'
        }

        new_status = status_mapping.get(action.lower(), None)
        if not new_status:
            conn.close()
            return jsonify({"error": "Invalid action"}), 400

        # 🚀 更新数据库状态
        cursor.execute('''
            UPDATE device_control
            SET status = ?, manual_override = ?
            WHERE device = ?
        ''', (new_status, 'on', device))

        if cursor.rowcount == 0:
            conn.close()
            print(f"[Error] Update failed for device '{device}'")
            return jsonify({"error": f"Update failed for device '{device}'"}), 500

        conn.commit()
        conn.close()

        # 🚀 发布 MQTT 同步消息
        topic = f"device/{device}/status"
        if mqtt_client:
            mqtt_client.publish(topic, new_status)
            print(f"[MQTT] Published: {topic} -> {new_status}")
        else:
            print("[Warning] MQTT Client is not connected.")

        return jsonify({"status": "success", "action": new_status}), 200

    except Exception as e:
        print(f"[Error] Failed to control {device}: {str(e)}")
        return jsonify({"error": str(e)}), 500


def init_db():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temperature_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_user_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            id_number TEXT,
            home_address TEXT,
            company TEXT,
            company_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_aircon_db():    #-----------------------------------------
    conn = sqlite3.connect('aircon.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircon_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            cooling_status TEXT,
            dehumidifying_status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_water_heater_db():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_heater_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_light_control_db():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS light_control_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intensity REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_fps_db():
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fps REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_surveillance_camera_db():
    conn = sqlite3.connect('surveillance_camera.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveillance_camera_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_to_db(value, timestamp):
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO temperature_data (value, timestamp) VALUES (?, ?)', (value, timestamp))
    conn.commit()
    conn.close()


def save_water_heater_to_db(temperature, status, timestamp):
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO water_heater_data (temperature, status, timestamp) VALUES (?, ?, ?)',
                   (temperature, status, timestamp))
    conn.commit()
    conn.close()


def save_light_control_to_db(intensity, status, timestamp):
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO light_control_data (intensity, status, timestamp) VALUES (?, ?, ?)',
                   (intensity, status, timestamp))
    conn.commit()
    conn.close()


def save_fps_to_db(fps, timestamp):
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fps_data (fps, timestamp) VALUES (?, ?)', (fps, timestamp))
    conn.commit()
    conn.close()


def save_surveillance_camera_to_db(status, timestamp):
    conn = sqlite3.connect('surveillance_camera.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO surveillance_camera_data (status, timestamp) VALUES (?, ?)', (status, timestamp))
    conn.commit()
    conn.close()

def save_aircon_to_db(temperature, humidity, cooling_status, dehumidifying_status, timestamp):   #-----------------------------------------
    conn = sqlite3.connect('aircon.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO aircon_data (temperature, humidity, cooling_status, dehumidifying_status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (temperature, humidity, cooling_status, dehumidifying_status, timestamp))
    conn.commit()
    conn.close()

@app.route('/api/device/<device>/save-state', methods=['POST'])    #-----------------------------------------
def save_device_state(device):
    try:
        # 1️⃣ 获取请求体的数据
        data = request.get_json()
        status = data.get('status')
        mode = data.get('mode')

        if not status or not mode:
            return jsonify({"error": "Missing status or mode"}), 400

        conn = sqlite3.connect('device_control.db')
        cursor = conn.cursor()

        # ✅ 修正更新逻辑：使用模式更新
        cursor.execute('''
            UPDATE device_control
            SET status = ?, manual_override = ?
            WHERE device = ?
        ''', (status.upper(), mode, device))

        if cursor.rowcount == 0:
            conn.close()
            print(f"[Error] Device '{device}' not found in database.")
            return jsonify({"error": f"Device '{device}' not found"}), 404

        conn.commit()
        conn.close()
        print(f"[数据库同步] {device} 状态: {status}, 模式: {mode}")

        return jsonify({"message": f"{device} state saved successfully"}), 200

    except Exception as e:
        print(f"[Error] Failed to save state for {device}: {str(e)}")
        return jsonify({"error": str(e)}), 500


USERNAME_REGEX = re.compile(r'^\w{3,20}$')  # 用户名：3-20位，字母数字下划线
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$')  # 密码强度
PHONE_REGEX = re.compile(r'^1[3-9]\d{9}$')  # 中国大陆手机号
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')  # 简单邮箱校验
ID_NUMBER_REGEX = re.compile(r'^\d{15}(\d{2}[\dxX])?$')  # 简单身份证号校验


def validate_registration(data):
    """ 验证注册信息是否符合要求 """
    errors = []

    if not USERNAME_REGEX.match(data.get('username', '')):
        errors.append("Username must be 3-20 characters, letters, numbers, or underscores.")

    if not PASSWORD_REGEX.match(data.get('password', '')):
        errors.append(
            "Password must be at least 8 characters, contain uppercase, lowercase, number, and special character.")

    if not PHONE_REGEX.match(data.get('phone', '')):
        errors.append("Invalid phone number format.")

    if not EMAIL_REGEX.match(data.get('email', '')):
        errors.append("Invalid email address format.")

    if not ID_NUMBER_REGEX.match(data.get('idNumber', '')):
        errors.append("Invalid ID number format.")

    if len(data.get('homeAddress', '')) < 5:
        errors.append("Home address must be at least 5 characters long.")

    if len(data.get('company', '')) < 2:
        errors.append("Company name must be at least 2 characters long.")

    if len(data.get('companyAddress', '')) < 5:
        errors.append("Company address must be at least 5 characters long.")

    return errors


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 🔥 打印接收到的数据
    print("收到的数据:", data)

    if not data:
        print("没有接收到任何数据")
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    # 🔥 打印各个字段
    print("Username:", data.get('username'))
    print("Password:", data.get('password'))
    print("Phone:", data.get('phone'))
    print("Email:", data.get('email'))
    print("ID Number:", data.get('idNumber'))
    print("Home Address:", data.get('homeAddress'))
    print("Company:", data.get('company'))
    print("Company Address:", data.get('companyAddress'))

    # 校验数据格式
    errors = validate_registration(data)
    if errors:
        print("数据校验失败:", errors)  # 👉 这里可以看到校验失败的原因
        return jsonify({'status': 'error', 'message': 'Validation failed', 'errors': errors}), 400

    # 数据提取
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('idNumber')
    home_address = data.get('homeAddress')
    company = data.get('company')
    company_address = data.get('companyAddress')

    # 🔥 打印即将写入数据库的数据
    print("🔥 准备写入数据库:", username, password, phone, email, id_number, home_address, company, company_address)

    # 插入数据库
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password, phone, email, id_number, home_address, company, company_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, phone, email, id_number, home_address, company, company_address))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print("数据库插入失败:", e)
        conn.close()
        return jsonify({'status': 'error', 'message': 'Database Error: ' + str(e)}), 500
    finally:
        conn.close()

    print("用户注册成功:", username)
    return jsonify({'status': 'success', 'message': 'Registration successful'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'message': '登录成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401


@app.route('/api/user', methods=['GET'])
def get_user_info():
    username = request.args.get('username')

    if not username:
        return jsonify({'status': 'error', 'message': '用户名不能为空'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_info = {
            'username': user[1],
            'phone': user[3],
            'email': user[4],
            'idNumber': user[5],
            'homeAddress': user[6],
            'company': user[7],
            'companyAddress': user[8]
        }
        return jsonify({'status': 'success', 'data': user_info})
    else:
        return jsonify({'status': 'error', 'message': '用户未找到'}), 404


@app.route('/api/user', methods=['PUT'])
def update_user_info():
    data = request.get_json()

    username = data.get('username')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('idNumber')
    home_address = data.get('homeAddress')
    company = data.get('company')
    company_address = data.get('companyAddress')

    if not username:
        return jsonify({'status': 'error', 'message': '用户名不能为空'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET phone = ?, email = ?, id_number = ?, home_address = ?, company = ?, company_address = ?
        WHERE username = ?
    ''', (phone, email, id_number, home_address, company, company_address, username))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': '个人信息更新成功'})


@app.route('/connect-mqtt', methods=['POST'])
def connect_mqtt():
    global mqtt_client

    data = request.get_json()
    broker = data.get('brokerUrl')
    port = int(data.get('port'))
    client_id = data.get('clientId')

    if not all([broker, port, client_id]):
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400

    try:
        mqtt_client = mqtt.Client(client_id=client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.connect(broker, port, 60)
        mqtt_client.loop_start()

        return jsonify({'status': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/subscribe', methods=['POST'])
def subscribe():
    global mqtt_client
    data = request.get_json()
    topic = data.get('topic')
    if not topic:
        return jsonify({'status': 'error', 'message': '缺少topic'}), 400

    try:
        mqtt_client.subscribe(topic)
        return jsonify({'status': 'subscribed', 'topic': topic})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/messages/<device_id>', methods=['GET'])   #-----------------------------------------
def get_messages(device_id):
    topic = f"device/{device_id}"
    msgs = received_messages.get(topic, [])
    return jsonify({'topic': topic, 'messages': msgs})


@app.route('/api/device/<device>/mode', methods=['GET'])   #-----------------------------------------
def get_device_mode(device):
    try:
        conn = sqlite3.connect('device_control.db')
        cursor = conn.cursor()

        cursor.execute("SELECT manual_override FROM device_control WHERE device = ?", (device,))
        result = cursor.fetchone()
        conn.close()

        if result:
            mode = result[0]
            return jsonify({"mode": mode}), 200
        else:
            return jsonify({"error": f"No device found with name {device}"}), 404
    except Exception as e:
        print(f"[Error] Failed to get mode for {device}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/device/<device>/current-status', methods=['GET'])   #-----------------------------------------
def get_current_device_status(device):
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, manual_override FROM device_control WHERE device=?", (device,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            "status": result[0],
            "manual_mode": result[1]
        }), 200
    else:
        return jsonify({
            "status": "N/A",
            "manual_mode": "off"
        }), 404


def simulate_temperature():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            temp = round(random.uniform(20.0, 30.0), 2)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/temperature", json.dumps({"temperature": temp, "timestamp": timestamp}))
            save_to_db(temp, timestamp)
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()


def simulate_water_heater():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            temperature = round(random.uniform(30.0, 60.0), 2)
            status = random.choice(['running', 'stopped'])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/water_heater",
                               json.dumps({"temperature": temperature, "status": status, "timestamp": timestamp}))
            save_water_heater_to_db(temperature, status, timestamp)
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()


def simulate_light_control():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1883, 60)
        pub_client.loop_start()
        while True:
            intensity = round(random.uniform(100.0, 800.0), 2)
            status = "on" if intensity < 200.0 or intensity > 600.0 else "off"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/light_control",
                               json.dumps({"intensity": intensity, "status": status, "timestamp": timestamp}))
            save_light_control_to_db(intensity, status, timestamp)
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()


def simulate_fps():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            fps = round(random.uniform(20.0, 60.0), 2)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/fps", json.dumps({"fps": fps, "timestamp": timestamp}))
            save_fps_to_db(fps, timestamp)
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()


def simulate_surveillance_camera():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1883, 60)
        pub_client.loop_start()
        while True:
            status = random.choice(['recording', 'idle'])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish(
                "device/surveillance_camera",
                json.dumps({"status": status, "timestamp": timestamp})
            )
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()
def simulate_aircon():    #-----------------------------------------
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            # ✅ 模拟生成温度和湿度
            temperature = round(random.uniform(22.0, 35.0), 1)
            humidity = round(random.uniform(40.0, 80.0), 1)

            # ✅ 根据温湿度判断状态
            cooling_status = "ON" if temperature > 28 else "OFF"
            dehumidifying_status = "ON" if humidity > 65 else "OFF"

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = {
                "temperature": temperature,
                "humidity": humidity,
                "cooling_status": cooling_status,
                "dehumidifying_status": dehumidifying_status,
                "timestamp": timestamp
            }

            # ✅ 发布到 MQTT
            pub_client.publish("device/aircon", json.dumps(payload))

            # ✅ 保存到数据库
            save_aircon_to_db(temperature, humidity, cooling_status, dehumidifying_status, timestamp)

            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()


@app.route('/api/realtime/fps', methods=['GET'])
def get_latest_fps():
    topic = "device/fps"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'fps': None, 'timestamp': '', 'message': '暂无数据'})


@app.route('/api/history/fps', methods=['GET'])
def get_fps_history():
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, fps FROM fps_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'fps': row[1]} for row in rows]
    return jsonify({'history': history})


@app.route('/api/realtime/temperature', methods=['GET'])
def get_latest_temperature():
    topic = "device/temperature"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'value': None, 'timestamp': '', 'message': '暂无数据'})


@app.route('/api/realtime/water_heater', methods=['GET'])
def get_latest_water_heater():
    topic = "device/water_heater"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'value': None, 'status': None, 'timestamp': '', 'message': '暂无数据'})


@app.route('/api/realtime/light-control', methods=['GET'])
def get_latest_light_control():
    topic = "device/light_control"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'intensity': None, 'status': None, 'timestamp': '', 'message': '暂无数据'})


@app.route('/api/history/temperature', methods=['GET'])
def get_temperature_history():
    """
    API to fetch historical temperature data
    """
    try:
        conn = sqlite3.connect('temperature.db')
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, value FROM temperature_data ORDER BY id DESC LIMIT 100')
        rows = cursor.fetchall()
        conn.close()

        # 映射成前端可以接受的格式
        history = [{'timestamp': row[0], 'temperature': row[1]} for row in rows]
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/aircon', methods=['GET'])
def get_temperature_aircon_history():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, value FROM temperature_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'temperature': row[1]} for row in rows]
    return jsonify({'history': history})


@app.route('/api/history/water_heater', methods=['GET'])
def get_water_heater_history():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, temperature, status FROM water_heater_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'temperature': row[1], 'status': row[2]} for row in rows]
    return jsonify({'history': history})


@app.route('/api/history/light_control', methods=['GET'])
def get_light_control_history():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, intensity, status FROM light_control_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'intensity': row[1], 'status': row[2]} for row in rows]
    return jsonify({'history': history})


@app.route('/api/device/<device>/status', methods=['GET'])   #-----------------------------------------
def get_device_status(device):
    """
    获取设备当前的模式和状态
    """
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mode, status FROM device_control WHERE device = ?", (device,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"mode": result[0], "status": result[1]}
    else:
        return {"mode": "unknown", "status": "unknown"}


@app.route('/api/device/water_heater/on', methods=['POST'])   #-----------------------------------------
def turn_on_water_heater():
    try:
        conn = sqlite3.connect('device_control.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE device_control SET status = 'ON' WHERE device = 'water_heater'")

        # ✅ 检查数据库是否真正更新
        if cursor.rowcount == 0:
            print("[Error] Water Heater not found or update failed.")
            conn.close()
            return jsonify({"message": "Failed to update Water Heater"}), 500

        conn.commit()
        conn.close()

        # 🔥 确认 MQTT 是否连接
        if mqtt_client:
            mqtt_client.publish("device/water_heater/control", "ON")
            print("[MQTT] Published: device/water_heater/control -> ON")
        else:
            print("[Warning] MQTT Client not connected.")

        return jsonify({"message": "Water Heater turned on"}), 200
    except Exception as e:
        print(f"[Error] Failed to turn on water heater: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/device/water_heater/off', methods=['POST'])   #-----------------------------------------
def turn_off_water_heater():
    try:
        conn = sqlite3.connect('device_control.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE device_control SET status = 'OFF' WHERE device = 'water_heater'")

        if cursor.rowcount == 0:
            conn.close()
            print("[Error] Water Heater not found or update failed.")
            return jsonify({"message": "Failed to update Water Heater"}), 500

        conn.commit()
        conn.close()

        # 🔥 确认 MQTT 是否连接
        if mqtt_client:
            mqtt_client.publish("device/water_heater/control", "OFF")
            print("[MQTT] Published: device/water_heater/control -> OFF")
        else:
            print("[Warning] MQTT Client not connected.")

        return jsonify({"message": "Water Heater turned off"}), 200
    except Exception as e:
        print(f"[Error] Failed to turn off water heater: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/device/water_heater/mode', methods=['POST'])   #-----------------------------------------
def switch_water_heater_mode():
    data = request.json
    mode = data.get('mode')
    if mode not in ['manual', 'auto']:
        return jsonify({"message": "Invalid mode"}), 400
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE device_control SET mode = ? WHERE device = 'water_heater'", (mode,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Water Heater mode set to {mode}"}), 200


@app.route('/api/device/lighting/increase', methods=['POST'])   #-----------------------------------------
def increase_lighting():
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mode FROM device_control WHERE device = 'lighting'")
    mode = cursor.fetchone()[0]
    if mode == 'manual':
        mqtt_client.publish("device/lighting/control", "BRIGHTER")
        return jsonify({"message": "Lighting brightness increased"}), 200
    else:
        return jsonify({"message": "Lighting is in auto mode, cannot adjust brightness"}), 400


@app.route('/api/device/lighting/off', methods=['POST'])   #-----------------------------------------
def turn_off_lighting():
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE device_control SET status = 'off' WHERE device = 'lighting'")
    conn.commit()
    conn.close()

    # 防止 mqtt_client 是 None
    if mqtt_client:
        mqtt_client.publish("device/lighting/control", "OFF")
    else:
        print("[警告] MQTT 客户端未初始化，无法发送消息")

    return jsonify({"message": "Lighting turned off"}), 200


@app.route('/api/device/camera/start', methods=['POST'])    #-----------------------------------------
def start_camera():
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE device_control SET status = 'on' WHERE device = 'camera'")
    conn.commit()
    conn.close()
    mqtt_client.publish("device/camera/control", "START")
    return jsonify({"message": "Camera started"}), 200


@app.route('/api/device/camera/stop', methods=['POST'])     #-----------------------------------------
def stop_camera():
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE device_control SET status = 'off' WHERE device = 'camera'")
    conn.commit()
    conn.close()
    mqtt_client.publish("device/camera/control", "STOP")
    return jsonify({"message": "Camera stopped"}), 200


@app.route('/api/device/toggle-mode', methods=['POST'])  #-----------------------------------------
def toggle_mode():
    data = request.get_json()
    manual_mode = data.get('manual_mode')

    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()

    if manual_mode == "on":
        cursor.execute('UPDATE device_control SET manual_override = "on"')
    else:
        cursor.execute('UPDATE device_control SET manual_override = "off"')

    conn.commit()
    conn.close()

    print(f"[数据库同步] 切换模式为: {manual_mode}")
    return jsonify({"message": f"Device mode set to {manual_mode}"}), 200


@app.route('/api/device/status', methods=['GET'])  #--------------------------------------------
def get_all_device_status():
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("SELECT device, mode, status FROM device_control")
    rows = cursor.fetchall()
    conn.close()

    response = []
    for row in rows:
        if row[0] != 'aircon':  # 暂时不返回 aircon 的状态
            response.append({
                "device": row[0],
                "mode": row[1],
                "status": row[2]
            })

    return jsonify(response), 200


@app.route('/api/device/<device>/mode', methods=['POST'])    #---------------------------------------
def set_device_mode(device):
    """
    设置设备的模式 (auto 或 manual)
    """
    data = request.json
    mode = data.get('mode')
    if mode not in ['auto', 'manual']:
        return jsonify({"message": "Invalid mode"}), 400

    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE device_control SET mode = ? WHERE device = ?", (mode, device))
    conn.commit()
    conn.close()

    return jsonify({"message": f"{device} mode set to {mode}"}), 200


@app.route('/api/realtime/surveillance_camera', methods=['GET'])
def get_latest_surveillance_camera():
    topic = "device/surveillance_camera"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'status': None, 'timestamp': '', 'message': '暂无数据'})


# ==================== New API for Database Queries ====================

@app.route('/api/realtime-db/temperature', methods=['GET'])
def get_latest_temperature_from_db():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('SELECT value, timestamp FROM temperature_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'value': row[0],
            'timestamp': row[1],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'value': None,
            'timestamp': '',
            'message': 'No data available'
        })


@app.route('/api/realtime-db/water_heater', methods=['GET'])
def get_latest_water_heater_from_db():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('SELECT temperature, status, timestamp FROM water_heater_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'temperature': row[0],
            'status': row[1],
            'timestamp': row[2],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'temperature': None,
            'status': None,
            'timestamp': '',
            'message': 'No data available'
        })
@app.route('/api/device/aircon/view-data', methods=['GET'])     #-----------------------------------------------
def get_latest_aircon_data():
    try:
        conn = sqlite3.connect('aircon.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT temperature, humidity, cooling_status, dehumidifying_status, timestamp
            FROM aircon_data
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            data = {
                "temperature": row[0],
                "humidity": row[1],
                "cooling_status": row[2],
                "dehumidifying_status": row[3],
                "timestamp": row[4]
            }
        else:
            data = {
                "temperature": None,
                "humidity": None,
                "cooling_status": "N/A",
                "dehumidifying_status": "N/A",
                "timestamp": ""
            }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch aircon data: {str(e)}"}), 500


@app.route('/api/realtime-db/fps', methods=['GET'])
def get_latest_fps_from_db():
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('SELECT fps, timestamp FROM fps_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'fps': row[0],
            'timestamp': row[1],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'fps': None,
            'timestamp': '',
            'message': 'No data available'
        })




@app.route('/api/device/<device>/status', methods=['GET'])  #------------------------------------------
def api_get_device_status(device):
    """
    获取设备的当前状态
    """
    status = get_device_status(device)
    return jsonify(status), 200


@app.route('/api/device/<device>/<action>', methods=['POST'])   #-------------------------------------------
def api_control_device(device, action):
    """
    控制设备的状态，包括开关以及亮度调节
    """
    if action in ['on', 'off', 'brighter', 'dimmer']:
        update_device_status(device, status=action)
        return jsonify({"message": f"{device} is now {action}"}), 200
    elif action == 'manual':
        update_device_status(device, mode='manual')
        return jsonify({"message": f"{device} is now in manual mode"}), 200
    elif action == 'auto':
        update_device_status(device, mode='auto')
        return jsonify({"message": f"{device} is now in auto mode"}), 200
    else:
        return jsonify({"error": "Invalid action"}), 400


@app.route('/api/realtime-db/light_control', methods=['GET'])
def get_latest_light_control_from_db():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('SELECT intensity, status, timestamp FROM light_control_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'intensity': row[0],
            'status': row[1],
            'timestamp': row[2],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'intensity': None,
            'status': None,
            'timestamp': '',
            'message': 'No data available'
        })

@app.route('/api/device/lighting/view-data', methods=['GET'])
def view_lighting_data():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('SELECT intensity, status, timestamp FROM light_control_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'intensity': row[0],
            'status': row[1],
            'timestamp': row[2],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'intensity': None,
            'status': None,
            'timestamp': '',
            'message': 'No data available'
        })

@app.route('/api/device/water_heater/view-data', methods=['GET'])
def view_water_heater_data():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('SELECT temperature, status, timestamp FROM water_heater_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'temperature': row[0],
            'status': row[1],
            'timestamp': row[2],
            'message': 'Data fetched successfully'
        })
    else:
        return jsonify({
            'temperature': None,
            'status': None,
            'timestamp': '',
            'message': 'No data available'
        })

    @app.route('/api/device/aircon/view-data', methods=['GET'])  #---------------------------------------------
    def view_aircon_data():
        conn = sqlite3.connect('aircon.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT temperature, humidity, cooling_status, dehumidifying_status, timestamp FROM aircon_data ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()

        if row:
            return jsonify({
                'temperature': row[0],
                'humidity': row[1],
                'cooling_status': row[2],
                'dehumidifying_status': row[3],
                'timestamp': row[4],
                'message': 'Data fetched successfully'
            })
        else:
            return jsonify({
                'temperature': None,
                'humidity': None,
                'cooling_status': None,
                'dehumidifying_status': None,
                'timestamp': '',
                'message': 'No data available'
            })


@app.route('/api/device/<device>/manual-state', methods=['GET'])  #--------------------------------------
def get_device_manual_override(device):
    """
    查询 device_control 表中该设备当前的状态和是否手动模式
    """
    conn = sqlite3.connect('device_control.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, manual_override FROM device_control WHERE device = ?", (device,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            "status": result[0],
            "manual_override": result[1]
        })
    else:
        return jsonify({
            "status": "unknown",
            "manual_override": "off"
        }), 404


if __name__ == '__main__':
    init_db()
    init_user_db()
    init_water_heater_db()
    init_light_control_db()
    init_fps_db()
    init_surveillance_camera_db()
    simulate_temperature()
    simulate_water_heater()
    simulate_light_control()
    init_aircon_db()      #---------------------------------------------
    simulate_aircon()     #---------------------------------------------
    simulate_fps()
    simulate_surveillance_camera()
    init_device_control_db()
    app.run(host='0.0.0.0', port=5050, debug=True)