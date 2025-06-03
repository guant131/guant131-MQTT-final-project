from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import time
import os
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Add CORS support

# Check if model file exists
if not os.path.exists('yolov8n.pt'):
    print("Error: Model file 'yolov8n.pt' does not exist!")
    print("Please download model: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt")

# Load YOLO model
try:
    model = YOLO('yolov8n.pt')
    print("YOLO model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")
    model = None

# Define class list
classes = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]

# Advanced brightness enhancement function
def enhance_brightness(image, alpha=1.2, beta=20, use_hsv=False):  # Adjust parameters
    """Enhance image brightness, supports two methods"""
    if use_hsv:
        # HSV method (enhance V channel)
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)

            # Enhance brightness using linear transformation
            v = cv2.add(v, beta)
            v = np.clip(v, 0, 255).astype(hsv.dtype)

            # Optionally adjust saturation
            s = np.clip(s * alpha, 0, 255).astype(hsv.dtype)

            hsv = cv2.merge([h, s, v])
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        except Exception as e:
            print(f"HSV brightness enhancement failed: {e}, fallback to BGR method")

    # BGR method (direct contrast and brightness adjustment)
    try:
        # Ensure alpha and beta are within a reasonable range
        alpha = max(0.1, min(3.0, alpha))
        beta = max(0, min(100, beta))

        # Safely adjust brightness and contrast using convertScaleAbs
        enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        # Check for pixel value overflow (should not happen theoretically)
        if np.any(enhanced < 0) or np.any(enhanced > 255):
            print("Warning: pixel values out of range, clipping")
            enhanced = np.clip(enhanced, 0, 255).astype(image.dtype)

        return enhanced
    except Exception as e:
        print(f"BGR brightness enhancement failed: {e}, returning original image")
        return image

# Generate processed video frame stream
def generate_frames():
    """Generate processed video frames"""
    if model is None:
        yield '--frame\r\nContent-Type: text/plain\r\n\r\nModel failed to load, check model path\r\n\r\n'
        return

    try:
        # Open the camera
        cap = cv2.VideoCapture(0)

        # Get list of supported camera properties
        try:
            print("\nSupported camera properties:")
            for prop in [
                cv2.CAP_PROP_BRIGHTNESS,
                cv2.CAP_PROP_CONTRAST,
                cv2.CAP_PROP_SATURATION,
                cv2.CAP_PROP_HUE,
                cv2.CAP_PROP_GAIN,
                cv2.CAP_PROP_EXPOSURE
            ]:
                value = cap.get(prop)
                print(f"  {prop}: {value}")
        except Exception as e:
            print(f"Failed to get camera properties: {e}")

        # Try to set camera parameters
        try:
            # Enable auto exposure
            if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
                print("Warning: failed to set auto exposure")
        except Exception as e:
            print(f"Failed to set camera parameters: {e}")

        # Get actual camera resolution
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera default resolution: {actual_width}x{actual_height}")

        # Try to set camera resolution
        if not cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640):
            print("Warning: failed to set frame width")
        if not cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480):
            print("Warning: failed to set frame height")

        # Re-check resolution to confirm
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera actual resolution: {actual_width}x{actual_height}")

        if not cap.isOpened():
            yield '--frame\r\nContent-Type: text/plain\r\n\r\nCannot open camera\r\n\r\n'
            return

        print("Camera opened, starting video stream processing")

        frame_count = 0
        error_count = 0

        while True:
            frame_count += 1
            try:
                start_time = time.time()

                # Read frame
                success, frame = cap.read()
                if not success:
                    error_count += 1
                    print(f"Failed to read frame #{error_count}")
                    if error_count > 5:  # Exit loop after 5 consecutive failures
                        print("Too many failed frames, exiting loop")
                        break
                    # Wait briefly before retrying
                    time.sleep(0.1)
                    continue
                else:
                    # Reset error counter on successful read
                    error_count = 0

                # Check if frame is empty
                if frame is None or frame.size == 0:
                    print("Warning: empty frame")
                    continue

                # Enhance image brightness (using HSV method, adjustable parameters)
                frame = enhance_brightness(frame, alpha=1.2, beta=20, use_hsv=True)

                height, width, _ = frame.shape
                print(f"\nProcessing frame #{frame_count}: {width}x{height}")

                # Forward inference
                results = model.predict(frame, conf=0.1)

                detections = []
                person_count = 0  # Initialize person count
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        left, top, right, bottom = xyxy
                        width = right - left
                        height = bottom - top

                        detections.append({
                            'class_id': class_id,
                            'confidence': confidence,
                            'left': left,
                            'top': top,
                            'right': right,
                            'bottom': bottom,
                            'width': width,
                            'height': height
                        })

                        # Count number of people
                        if classes[class_id] == 'person':
                            person_count += 1

                # Draw detection boxes
                for detection in detections:
                    left = detection['left']
                    top = detection['top']
                    right = detection['right']
                    bottom = detection['bottom']
                    class_id = detection['class_id']
                    confidence = detection['confidence']

                    # Use HSV color space to generate unique color
                    hue = int(360 * class_id / len(classes))
                    color = tuple(int(c) for c in cv2.cvtColor(
                        np.array([[[hue, 255, 255]]], dtype=np.uint8),
                        cv2.COLOR_HSV2BGR)[0][0])

                    # Draw bounding box
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 3)

                    # Draw label background and text
                    label = f"{classes[class_id]}: {confidence:.2f}"
                    (label_width, label_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

                    # Ensure label does not overflow image
                    label_x = left
                    label_y = max(top - 10, label_height + 10)

                    cv2.rectangle(frame,
                                  (label_x, label_y - label_height - baseline),
                                  (label_x + label_width, label_y),
                                  color, -1)

                    cv2.putText(frame, label,
                                (label_x, label_y - baseline),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Calculate FPS
                fps = 1.0 / (time.time() - start_time)
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Display detection count and person count
                cv2.putText(frame, f"Detections: {len(detections)}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Persons: {person_count}", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Encode and send frame
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if not ret:
                    print("Warning: failed to encode frame")
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                # Send person count info
                yield (b'--person_count\r\n'
                       b'Content-Type: application/json\r\n\r\n' + str(person_count).encode() + b'\r\n')

            except Exception as e:
                print(f"Error processing frame #{frame_count}: {e}")
                # Continue processing next frame to avoid service interruption
                continue

    except Exception as e:
        print(f"Fatal error while processing video stream: {e}")
    finally:
        # Release resources
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            print("Camera released")

# The remainder of the file includes routes and main section...

@app.route('/video_feed')
def video_feed():
    """Video stream endpoint"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect', methods=['POST'])
def detect():
    """Receive image and return detection results"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get uploaded image
        file = request.files['image']
        if not file:
            return jsonify({"error": "No image provided"}), 400

        # Read image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Failed to decode image"}), 400

        height, width, _ = image.shape

        # Forward inference
        results = model.predict(image, conf=0.1)

        detections = []
        person_count = 0  # Initialize person count
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                left, top, right, bottom = xyxy
                width = right - left
                height = bottom - top

                detections.append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'left': left,
                    'top': top,
                    'right': right,
                    'bottom': bottom,
                    'width': width,
                    'height': height
                })

                # Count number of people
                if classes[class_id] == 'person':
                    person_count += 1

        # Convert to JSON-serializable format
        results = []
        for detection in detections:
            results.append({
                'class_id': detection['class_id'],
                'class_name': classes[detection['class_id']],
                'confidence': detection['confidence'],
                'bounding_box': {
                    'left': detection['left'],
                    'top': detection['top'],
                    'width': detection['width'],
                    'height': detection['height']
                }
            })

        return jsonify({"detections": results, "person_count": person_count})

    except Exception as e:
        return jsonify({"error": f"Detection error: {str(e)}"}), 500


@app.route('/')
def index():
    """Home page"""
    return "YOLOv8 object detection service is running"


if __name__ == '__main__':
    print("Starting YOLOv8 object detection service...")
    app.run(host='0.0.0.0', port=5001, debug=True)
