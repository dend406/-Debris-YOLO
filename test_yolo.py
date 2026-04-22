from picamera2 import Picamera2
import cv2
from ultralytics import YOLO

# --- Завантаження моделі OpenVINO ---
model = YOLO("/home/dend/myenv/best_openvino_model", task="detect")

# --- Ініціалізація камери ---
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (1280, 720)}
)

picam2.configure(config)
picam2.start()

while True:

    # Отримати кадр з камери
    frame = picam2.capture_array()

    # Picamera2 повертає RGB → перевести у BGR для OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # --- YOLO інференс ---
    results = model(frame, imgsz=416, conf=0.6)

    # Накласти bounding boxes
    annotated = results[0].plot()

    # Показати результат
    cv2.imshow("YOLO Detection", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
picam2.stop()
