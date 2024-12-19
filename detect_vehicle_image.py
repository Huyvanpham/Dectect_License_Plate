import cv2
import torch

# Tải mô hình YOLOv5 được huấn luyện trước để nhận diện ô tô
yolo_vehicle_detect = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
yolo_vehicle_detect.conf = 0.5  # Độ tự tin tối thiểu

def detect_vehicle(image_path):
    """
    Hàm phát hiện ô tô từ một ảnh đầu vào.
    :param image_path: Đường dẫn đến ảnh đầu vào
    :return: Danh sách khung hình cắt chứa ô tô
    """
    img = cv2.imread(image_path)
    results = yolo_vehicle_detect(img)

    # Lọc các đối tượng thuộc lớp "car" (ô tô)
    cars = []
    for _, row in results.pandas().xyxy[0].iterrows():
        if row['name'] == 'car':  # Lớp 'car' trong tập COCO
            x_min, y_min, x_max, y_max = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            car_crop = img[y_min:y_max, x_min:x_max]
            cars.append(car_crop)
    
    return cars
