# MQTT Final Project: Smart Home System

This project is a web-based smart home dashboard developed using MQTT protocol. It enables real-time monitoring and control of various IoT devices in a simulated smart home environment.

## 🌟 Features

- 📡 Real-time device data transmission via MQTT
- 📈 Live visualization of temperature, lighting, and device states
- 🔧 Manual and automatic control modes for smart devices
- 🧩 Modular design: each device has its own control and display module
- 🗃️ Data persistence using SQLite for historical analysis

## 🧱 Project Structure

```
NewSmartHome/
├── mqtt-dashboard1/        # Main frontend and backend codebase
│   ├── frontend/           # Vue.js interface for user interaction
│   ├── backend/            # Flask + MQTT server code
│   └── database/           # SQLite databases for devices
├── .gitignore              # Ignore unnecessary files (e.g., .DS_Store)
└── README.md               # Project overview and usage guide
```

## 🔧 Tech Stack

- **Frontend**: Vue.js + Element UI + Axios
- **Backend**: Python Flask + paho-mqtt
- **Database**: SQLite
- **Communication**: MQTT (using Mosquitto Broker)

## 🚀 How to Run

### 1. Start MQTT Broker
Make sure Mosquitto MQTT broker is running locally on port `9001` with WebSocket enabled.

### 2. Run Backend
```bash
cd mqtt-dashboard1
python BackencodeEnglish.py
```

### 3. Run Frontend
```bash
cd mqtt-dashboard1
npm install -g @vue/cli
npm run serve
```

### 4. Access
Open `http://localhost:8080` in your browser.

## 📝 Notes

- All MQTT messages are published/subscribed using topics like `device/temperature`, `device/light`, etc.
- Device states are saved locally in `.db` files within the `database/` folder.
- Manual mode changes are persisted across refreshes.

## 👤 Author

**guant131**  
Communication University of China  
Course: Activity Led Learning Project – MQTT Smart Home System

## Team number
Tianxin Guan(Leader)
Haoxun Li
Ruihan Wang
Minzhi Fang
Shunping Lin 

## 📄 License

MIT License
