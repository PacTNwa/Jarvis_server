import os
from flask import Flask, request, Response, render_template_string, jsonify
import io
from datetime import datetime

app = Flask(__name__)

SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'JarvisGiminiScreenLook2_5')

# Словарь для изображений: {id: image}
latest_images = {}

# HTML с JS для списка экранов (каждый img под другим)
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
                container.innerHTML = '';  // Очистка
                ids.forEach(id => {
                    const div = document.createElement('div');
                    div.className = 'screen-container';
                    div.innerHTML = `<h3>Экран ${id}</h3><img src="/latest.jpg?id=${id}&t=${Date.now()}">`;
                    container.appendChild(div);
                });
            } catch (e) {
                console.error(e);
            }
        }
        setInterval(updateScreens, 3000);  // Обновление каждые 3 сек
        updateScreens();  // Первое обновление
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
    new_image = file.read()
    if len(new_image) > 1024:  # Защита от пустых
        latest_images[id] = new_image
    return 'OK', 200

@app.route('/latest.jpg')
def latest_jpg():
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return 'Неверный пароль', 401
    id = request.args.get('id')
    if id not in latest_images:
        return 'Нет изображения для этого ID', 404
    response = Response(latest_images[id], mimetype='image/jpeg')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/get_ids')
def get_ids():
    return jsonify(list(latest_images.keys()))  # Список всех ID

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
