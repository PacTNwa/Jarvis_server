import os
from flask import Flask, request, Response, render_template_string
import io
from datetime import datetime

app = Flask(__name__)

SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'JarvisGiminiScreenLook2_5')

# Словарь для изображений по ID
latest_images = {}

# HTML для просмотра MJPEG (30 FPS)
HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Экраны</title>
    <style>
        body { margin:0; background:#000; display:flex; flex-direction:column; align-items:center; padding:20px; }
        .screen-container { margin-bottom:20px; text-align:center; }
        .screen-container h3 { color:#fff; margin-bottom:10px; }
        img { max-width:80vw; max-height:80vh; object-fit:contain; border:1px solid #333; }
    </style>
</head>
<body>
    <div id="screens"></div>
    <script>
        async function updateScreens() {
            try {
                const response = await fetch('/get_ids');
                const ids = await response.json();
                const container = document.getElementById('screens');
                container.innerHTML = '';
                ids.forEach(id => {
                    const div = document.createElement('div');
                    div.className = 'screen-container';
                    div.innerHTML = `<h3>Экран ${id}</h3><img src="/stream?id=${id}" style="width:100%;">`;  # MJPEG-стрим
                    container.appendChild(div);
                });
            } catch (e) {
                console.error(e);
            }
        }
        setInterval(updateScreens, 5000);  # Обновление списка ID
        updateScreens();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return 'Неверный пароль', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
    return render_template_string(HTML)

@app.route('/upload', methods=['POST'])
def upload():
    id = request.form.get('id')
    if not id or 'image' not in request.files:
        return 'Нет ID или изображения', 400
    file = request.files['image']
    latest_images[id] = file.read()
    return 'OK', 200

@app.route('/stream')
def stream():
    id = request.args.get('id')
    if id not in latest_images:
        return 'Нет изображения', 404

    def generate():
        while True:
            with latest_images.lock:  # Если нужно мьютекс для многопоточности
                frame = latest_images[id]
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)  # ~30 FPS

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_ids')
def get_ids():
    return jsonify(list(latest_images.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
