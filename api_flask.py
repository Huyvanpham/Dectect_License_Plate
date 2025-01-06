from flask import Flask, jsonify, request, send_file
import datetime
import requests
from lp_video import handleVideo
import qrcode
import io
import subprocess


app = Flask(__name__)


def message(type, message=""):
    subprocess.Popen(["python", "test.py", type, message])

@app.route("/api/get_status", methods=["POST"])
def getStatus():
    file = request.files['file']
    action = request.form['action']
    path =  datetime.datetime.now().strftime("%Y-%m-%d") +".mp4"
    file.save(f'./result/{path}')
    check = handleVideo(f'./result/{path}')

    if check[0] is None:
        return jsonify({"code": "400", "status":"Khong nhan dien duoc bien so"}), 200

    code = check[0]

    for i in check:
        if len(i) > len(code):
            code = i

    payload = {
        "code": code,
        "action": action,
    }

    header = {
        "Authorization":"Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkBnbWFpbC5jb20iLCJpYXQiOjE3MzYwNTU1ODF9.b5yQEIxqeb6JEaJTuFYpPJVzCQXkl8JyMyJ_uXuWgBI"
    }

    res = requests.post("https://respective-lynnell-quangtx-65b507bd.koyeb.app/action-history", json=payload, headers=header)
    res = res.json()
    print(res)
    if res['status'] == False:
        if res['responseCode'] == 400: 
            message("message", res['message'])
            return jsonify({"message":res['message']})
        return jsonify({"message":"server error"}), 500

    if res['data']['action'] == "OPEN":
        message("message", "Cửa đã mở")
        return jsonify({"code": "200", "status":"Cua da mo"}), 200
    else:
        url = res['data']['url']

        if not url:
            return jsonify({"code":"500", "status": "Khong co url"}), 200
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return send_file(buffer, mimetype='image/png')



@app.route("/api/open_door", methods=["GET"])
def openDoor():
    message("message", "Cửa đã mở")
    return jsonify({"message": "success!"}), 200


#app.run(host='0.0.0.0', port=5111, debug=True)
if __name__ == "__main__":
    app.run(debug=True)
