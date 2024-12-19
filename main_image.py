import argparse
import cv2
from detect_vehicle_image import detect_vehicle  # Gọi file detect_vehicle_image.py
from lp_image import helper, yolo_license_plate  # Gọi file lp_image.py

def main(image_path):
    # Phát hiện ô tô từ ảnh
    cars = detect_vehicle(image_path)

    if not cars:
        print("Không tìm thấy xe trong ảnh.")
        return

    plate_found = False  # Biến kiểm tra có biển số hợp lệ hay không

    for car_crop in cars:
        # Chuyển sang nhận diện biển số
        lp = helper.read_plate(yolo_license_plate, car_crop)
        if lp != "unknown":
            plate_found = True
            print("Biển số xe ô tô:", lp)
            cv2.imshow("License Plate", car_crop)
            cv2.waitKey(0)

    # if not plate_found:
    #     print("Không tìm thấy biển số xe hợp lệ.")

if __name__ == "__main__":
    # Sử dụng argparse để nhận tham số từ terminal
    parser = argparse.ArgumentParser(description="Phát hiện ô tô và biển số từ ảnh")
    parser.add_argument('--i', '--image', required=True, help="Đường dẫn tới ảnh")
    args = parser.parse_args()

    # Chạy hàm chính với đường dẫn ảnh từ tham số
    main(args.i)
