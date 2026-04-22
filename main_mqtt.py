from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import serial
import pynmea2
import csv
import time
from datetime import datetime
import os
import json
import paho.mqtt.client as mqtt
import subprocess

# 1️⃣ Налаштування

MODEL_PATH = "/home/dend/myenv/best_openvino_model"
CONF_THRESHOLD = 0.8
IMG_SIZE = 416

GPS_PORT = "/dev/serial0"
GPS_BAUD = 9600

SAVE_INTERVAL = 5
CSV_FILE = "detections.csv"

TARGET_CLASS = "debris"

MQTT_BROKER = "192.168.2.145"
MQTT_PORT = 1883
MQTT_TOPIC = "drone/debris"

# 2️⃣ WiFi підключення

print("Connecting WiFi...")

subprocess.run([
    "nmcli","dev","wifi","connect","prol","password","korotkov"
])

# 3️⃣ MQTT підключення

print("Connecting MQTT...")

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected")
    else:
        print("MQTT connection failed")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mqtt_client.loop_start()

# 4️⃣ Завантаження моделі

print("Loading OpenVINO model...")
model = YOLO(MODEL_PATH, task="detect")

# 5️⃣ GPS

print("Initializing GPS...")
gps = serial.Serial(GPS_PORT, baudrate=GPS_BAUD, timeout=1)

def get_gps_coordinates():
    try:
        line = gps.readline().decode('utf-8', errors='ignore')
        if line.startswith("$GPGGA"):
            msg = pynmea2.parse(line)
            return msg.latitude, msg.longitude
    except:
        pass
    return None, None

# 6️⃣ CSV файл

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "latitude", "longitude", "confidence"])

# 7️⃣ Камера

print("Initializing camera...")

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (1280, 720)}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

print("System started...")

last_saved_time = 0
frame_count = 0
start_time = time.time()

# 8️⃣ Основний цикл

while True:

    frame = picam2.capture_array()

    if frame is None:
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    results = model(frame, imgsz=IMG_SIZE, conf=CONF_THRESHOLD, iou=0.4)

    for r in results:
        for box in r.boxes:

            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names[cls_id]

            if class_name == TARGET_CLASS and conf > CONF_THRESHOLD:

                current_time = time.time()

                if current_time - last_saved_time > SAVE_INTERVAL:

                    lat, lon = get_gps_coordinates()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if lat and lon:

                        # запис CSV
                        with open(CSV_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([timestamp, lat, lon, round(conf, 3)])

                        # MQTT повідомлення
                        payload = {
                            "timestamp": timestamp,
                            "latitude": lat,
                            "longitude": lon,
                            "confidence": round(conf,3)
                        }

                        mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))

                        print(f"[MQTT SENT] {payload}")

                        last_saved_time = current_time

    annotated = results[0].plot()
    cv2.imshow("Detection", annotated)

    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 9️⃣ Завершення

picam2.stop()
cv2.destroyAllWindows()

mqtt_client.loop_stop()
mqtt_client.disconnect()

fps = frame_count / (time.time() - start_time)
print(f"Average FPS: {fps:.2f}")
print("System stopped.")
