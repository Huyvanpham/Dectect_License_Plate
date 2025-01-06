from PIL import Image
import cv2
import torch
import function.utils_rotate as utils_rotate
from IPython.display import display
import function.helper as helper
import re


yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector.pt', force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
yolo_license_plate.conf = 0.60

def formatCode(bien_so):
    bien_so = bien_so.replace(" ", "")
    bien_so = bien_so.upper()
    bien_so = bien_so.replace("-", "")
    pattern = re.compile(r"([A-Z])(?=\d)") 
    bien_so = pattern.sub(r"\1-", bien_so) 
    return bien_so

def handleVideo(video_path):

    cap = cv2.VideoCapture(video_path)
    listCode = []

    checkEnd = False
    rep = int(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc frame từ video.")
            break

        plates = yolo_LP_detect(frame, size=640)
        list_plates = plates.pandas().xyxy[0].values.tolist()
        list_read_plates = set()

        if len(list_plates) == 0:
            lp = helper.read_plate(yolo_license_plate, frame)
            if lp != "unknown":
                cv2.putText(frame, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                list_read_plates.add(lp)
        else:
            for plate in list_plates:
                flag = 0
                x = int(plate[0]) 
                y = int(plate[1])
                w = int(plate[2] - plate[0])
                h = int(plate[3] - plate[1])
                crop_img = frame[y:y+h, x:x+w]
                cv2.rectangle(frame, (int(plate[0]),int(plate[1])), (int(plate[2]),int(plate[3])), color = (0,0,225), thickness = 2)
                cv2.imwrite("crop.jpg", crop_img)
                rc_image = cv2.imread("crop.jpg")
                lp = ""
                for cc in range(0,2):
                    for ct in range(0,2):
                        lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                        if lp != "unknown":
                            list_read_plates.add(lp)
                            cv2.putText(frame, lp, (int(plate[0]), int(plate[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                            flag = 1
                            break
                    if flag == 1:
                        break
        
        if list_read_plates and rep < 5:
            checkEnd = True
            rep += 1

            code = list(list_read_plates)[0]
            code = formatCode(code)

            print("Biển số xe vào bãi:", code)
            listCode.append(code)
        else:
            if checkEnd:
                cap.release()
                cv2.destroyAllWindows()
            
        width, height = 800, 800 
        resized_frame = cv2.resize(frame, (width, height))

        cv2.imshow('frame', resized_frame)
        cv2.setWindowProperty('frame', cv2.WND_PROP_TOPMOST, 1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return listCode

