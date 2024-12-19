from PIL import Image
import cv2
import torch
import argparse
import function.utils_rotate as utils_rotate
import function.helper as helper

# Xử lý tham số đầu vào
ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True, help='Path to input image')
args = ap.parse_args()

# Tải mô hình YOLOv5
yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector.pt', force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
yolo_license_plate.conf = 0.60

# Đọc ảnh đầu vào
img = cv2.imread(args.image)

# Nhận diện biển số xe
plates = yolo_LP_detect(img, size=640)
list_plates = plates.pandas().xyxy[0].values.tolist()
list_read_plates = set()

if len(list_plates) == 0:
    # Không phát hiện được khung biển số
    lp = helper.read_plate(yolo_license_plate, img)
    if lp != "unknown":
        print("Biển số xe vào bãi:", lp)
        cv2.putText(img, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        list_read_plates.add(lp)
    else:
        print("Không tìm thấy biển số xe hợp lệ.")
else:
    # Duyệt qua từng khung biển số được phát hiện
    for plate in list_plates:
        flag = 0
        x = int(plate[0])  # xmin
        y = int(plate[1])  # ymin
        w = int(plate[2] - plate[0])  # xmax - xmin
        h = int(plate[3] - plate[1])  # ymax - ymin
        crop_img = img[y:y+h, x:x+w]
        cv2.rectangle(img, (int(plate[0]), int(plate[1])), (int(plate[2]), int(plate[3])), color=(0, 0, 225), thickness=2)

        # Cố gắng nhận diện biển số trong từng khung
        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp)
                    print("Biển số xe vào bãi:", lp)
                    cv2.putText(img, lp, (int(plate[0]), int(plate[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    flag = 1
                    break
            if flag == 1:
                break

# # Nếu không có biển số nào hợp lệ
# if not list_read_plates:
#     print("Không tìm thấy biển số xe hợp lệ.")

# Hiển thị ảnh kết quả
width, height = 800, 800  # Kích thước mong muốn
resized_img = cv2.resize(img, (width, height))

cv2.imshow('frame', resized_img)
cv2.waitKey()
cv2.destroyAllWindows()
