from flask import Flask, render_template, Response
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # 0: default camera
scanned_codes = set()  # halmaz az eddig beolvasott QR-kódok tárolására


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            codes = decode(frame)
            for code in codes:
                code_data = code.data.decode('utf-8')
                if code_data not in scanned_codes:  # ellenőrizzük, hogy új-e az adott QR-kód
                    scanned_codes.add(code_data)  # hozzáadjuk a beolvasott kódokhoz
                    with open('scanned_codes.txt', 'a') as file:  # megnyitjuk a fájlt hozzáfűzés módjában
                        file.write(f'{code_data}\n')  # hozzáfűzzük a QR-kód tartalmát a fájlhoz
                pts = np.array(code.polygon, dtype=np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                cv2.putText(frame, code_data, (pts[0][0][0], pts[0][0][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
