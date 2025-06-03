from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import time
import os
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # 添加跨域支持

# 检查模型文件是否存在
if not os.path.exists('yolov8n.pt'):
    print("错误：模型文件 'yolov8n.pt' 不存在！")
    print("请下载模型：https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt")

# 加载YOLO模型
try:
    model = YOLO('yolov8n.pt')
    print("YOLO模型加载成功")
except Exception as e:
    print(f"模型加载失败: {e}")
    model = None

# 定义类别列表
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


# 高级亮度增强函数
def enhance_brightness(image, alpha=1.2, beta=20, use_hsv=False):  # 调整参数
    """增强图像亮度，支持两种方法"""
    if use_hsv:
        # HSV方法（对亮度通道单独增强）
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)

            # 使用线性变换增强亮度
            v = cv2.add(v, beta)
            v = np.clip(v, 0, 255).astype(hsv.dtype)

            # 可选：调整饱和度
            s = np.clip(s * alpha, 0, 255).astype(hsv.dtype)

            hsv = cv2.merge([h, s, v])
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        except Exception as e:
            print(f"HSV亮度增强失败: {e}，使用BGR方法替代")

    # BGR方法（直接调整对比度和亮度）
    try:
        # 确保alpha和beta在合理范围
        alpha = max(0.1, min(3.0, alpha))  # 限制alpha在0.1-3.0
        beta = max(0, min(100, beta))  # 限制beta在0-100

        # 使用convertScaleAbs安全地调整亮度和对比度
        enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        # 检查是否有像素越界（理论上不会发生）
        if np.any(enhanced < 0) or np.any(enhanced > 255):
            print("警告：像素值超出范围，进行裁剪")
            enhanced = np.clip(enhanced, 0, 255).astype(image.dtype)

        return enhanced
    except Exception as e:
        print(f"BGR亮度增强失败: {e}，返回原始图像")
        return image


def generate_frames():
    """生成处理后的视频帧流"""
    if model is None:
        yield '--frame\r\nContent-Type: text/plain\r\n\r\n模型加载失败，请检查模型路径\r\n\r\n'
        return

    try:
        # 打开摄像头
        cap = cv2.VideoCapture(0)

        # 获取摄像头支持的属性列表
        try:
            print("\n摄像头支持的属性:")
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
            print(f"获取摄像头属性失败: {e}")

        # 尝试设置摄像头参数
        try:
            # 启用自动曝光
            if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
                print("警告: 无法设置自动曝光")

            # 尝试设置曝光值（如果自动曝光不工作）
            # if not cap.set(cv2.CAP_PROP_EXPOSURE, 0.1):
            #     print("警告: 无法设置手动曝光")
        except Exception as e:
            print(f"设置摄像头参数失败: {e}")

        # 获取实际的摄像头分辨率
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"摄像头默认分辨率: {actual_width}x{actual_height}")

        # 尝试设置摄像头分辨率
        if not cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640):
            print("警告: 无法设置帧宽度")
        if not cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480):
            print("警告: 无法设置帧高度")

        # 重新获取分辨率确认设置结果
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"摄像头实际分辨率: {actual_width}x{actual_height}")

        if not cap.isOpened():
            yield '--frame\r\nContent-Type: text/plain\r\n\r\n无法打开摄像头\r\n\r\n'
            return

        print("摄像头已打开，开始处理视频流")

        frame_count = 0
        error_count = 0

        while True:
            frame_count += 1
            try:
                start_time = time.time()

                # 读取一帧
                success, frame = cap.read()
                if not success:
                    error_count += 1
                    print(f"读取帧失败 #{error_count}")
                    if error_count > 5:  # 连续5次失败则退出
                        print("连续多次读取帧失败，退出循环")
                        break
                    # 短暂休眠后继续尝试
                    time.sleep(0.1)
                    continue
                else:
                    error_count = 0  # 读取成功，重置错误计数器

                # 检查帧是否为空
                if frame is None or frame.size == 0:
                    print("警告: 获取到空帧")
                    continue

                # 增强图像亮度（使用HSV方法，参数可调整）
                frame = enhance_brightness(frame, alpha=1.2, beta=20, use_hsv=True)  # 调整参数

                height, width, _ = frame.shape
                print(f"\n处理帧 #{frame_count}: {width}x{height}")

                # 前向传播
                results = model.predict(frame, conf=0.1)

                detections = []
                person_count = 0  # 初始化人数统计
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

                        # 统计人数
                        if classes[class_id] == 'person':
                            person_count += 1

                # 绘制检测结果
                for detection in detections:
                    left = detection['left']
                    top = detection['top']
                    right = detection['right']
                    bottom = detection['bottom']
                    class_id = detection['class_id']
                    confidence = detection['confidence']

                    # 使用HSV颜色空间生成不同颜色
                    hue = int(360 * class_id / len(classes))
                    color = tuple(int(c) for c in cv2.cvtColor(
                        np.array([[[hue, 255, 255]]], dtype=np.uint8),
                        cv2.COLOR_HSV2BGR)[0][0])

                    # 绘制边界框
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 3)

                    # 绘制标签背景和文本
                    label = f"{classes[class_id]}: {confidence:.2f}"
                    (label_width, label_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

                    # 确保标签不会超出图像边界
                    label_x = left
                    label_y = max(top - 10, label_height + 10)

                    cv2.rectangle(frame,
                                  (label_x, label_y - label_height - baseline),
                                  (label_x + label_width, label_y),
                                  color, -1)

                    cv2.putText(frame, label,
                                (label_x, label_y - baseline),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # 计算FPS
                fps = 1.0 / (time.time() - start_time)
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 显示检测数量和人数
                cv2.putText(frame, f"Detections: {len(detections)}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Persons: {person_count}", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 编码并发送帧
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if not ret:
                    print("警告: 帧编码失败")
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                # 发送人数统计信息
                yield (b'--person_count\r\n'
                       b'Content-Type: application/json\r\n\r\n' + str(person_count).encode() + b'\r\n')

            except Exception as e:
                print(f"处理帧 #{frame_count} 时出错: {e}")
                # 继续处理下一帧，避免服务中断
                continue

    except Exception as e:
        print(f"处理视频流时发生严重错误: {e}")
    finally:
        # 释放资源
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            print("摄像头已释放")


@app.route('/video_feed')
def video_feed():
    """视频流接口"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect', methods=['POST'])
def detect():
    """接收图像并返回检测结果"""
    if model is None:
        return jsonify({"error": "模型未加载"}), 500

    try:
        # 获取上传的图像
        file = request.files['image']
        if not file:
            return jsonify({"error": "未提供图像"}), 400

        # 读取图像
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "无法解码图像"}), 400

        height, width, _ = image.shape

        # 前向传播
        results = model.predict(image, conf=0.1)

        detections = []
        person_count = 0  # 初始化人数统计
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

                # 统计人数
                if classes[class_id] == 'person':
                    person_count += 1

        # 转换为可JSON序列化的格式
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
        return jsonify({"error": f"检测过程出错: {str(e)}"}), 500


@app.route('/')
def index():
    """主页"""
    return "YOLOv8 目标检测服务已启动"


if __name__ == '__main__':
    print("启动YOLOv8目标检测服务...")
    app.run(host='0.0.0.0', port=5001, debug=True)