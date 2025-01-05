from flask import Flask, jsonify, request, send_file
import datetime
import requests
from lp_video import hanleVideo
import qrcode
import io


app = Flask(__name__)


@app.route("/api/get_status", methods=["POST"])
def getStatus():
    file = request.files['file']
    action = request.form['action']
    path =  datetime.datetime.now().strftime("%Y-%m-%d") +".mp4"
    file.save(f'./test_video/{path}')
    check = hanleVideo(f'./test_video/{path}')

    if check[0] is None:
        return jsonify({"code": "400", "status":"Khong nhan dien duoc bien so"}), 200

    payload = {
        "code":check[0],
        "action":action,
    }

    header = {
        "Authorization":"Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkBnbWFpbC5jb20iLCJpYXQiOjE3MzYwMTIzMTksImV4cCI6MTczNjAxNTkxOX0.wU5etsKxUiSq9yFj0bFCEvl4Yvu-EuK6g-f9a5B2nic"
    }

    res = requests.post("https://respective-lynnell-quangtx-65b507bd.koyeb.app/action-history", json=payload, headers=header)
    res =res.json()
    if res['status'] == False:
        return jsonify({"message":res['message'], "code":res['responseCode']})

    url = res['data']['url']

    if not url:
        return jsonify({"code":"500", "status": "Khong co url"}), 200
    # Tạo QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Lưu QR code vào bộ nhớ
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')



@app.route("/api/open_door", methods=["GET"])
def openDoor():
    print("Cua da mo")
    return jsonify({"code": "200", "status":"12312312"}), 200


#app.run(host='0.0.0.0', port=5111, debug=True)
if __name__ == "__main__":
    app.run(debug=True)
