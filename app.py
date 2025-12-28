import os
from flask import Flask, request, Response, render_template_string
import io
from datetime import datetime

app = Flask(__name__)

SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'yourpassword')  # ← меняйте через переменные окружения

# Храним последнее изображение + время его загрузки
latest_image = None
last_update_time = None

# HTML с принудительным обновлением каждые 3 секунды + случайный параметр
HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Экран</title>
    <style>
        body { margin:0; background:#000; display:flex; justify-content:center; align-items:center; height:100vh; }
        img { max-width:100vw; max-height:100vh; object-fit:contain; }
    </style>
</head>
<body>
    <img id="screen" src="/latest.jpg">
    <script>
        function updateImage() {
            const img = document.getElementById('screen');
            img.src = '/latest.jpg?t=' + new Date().getTime() + '&rand=' + Math.random();
        }
        setInterval(updateImage, 3000);  // 3 секунды — оптимально
        updateImage();  // Первое обновление сразу
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
    global latest_image, last_update_time
    if 'image' not in request.files:
        return 'Нет изображения', 400
    
    file = request.files['image']
    new_image = file.read()
    
    # Заменяем только если новое изображение больше 1 КБ (защита от пустых кадров)
    if len(new_image) > 1024:
        latest_image = new_image
        last_update_time = datetime.utcnow()
        print(f"[UPLOAD] Новое изображение загружено, размер: {len(new_image)} байт")
    else:
        print("[UPLOAD] Получен пустой кадр — игнорируем")
    
    return 'OK', 200

@app.route('/latest.jpg')
def latest_jpg():
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return 'Неверный пароль', 401
    
    if latest_image is None:
        return 'Нет изображения', 404
    
    response = Response(latest_image, mimetype='image/jpeg')
    # Максимальная защита от кэша
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['ETag'] = str(hash(last_update_time or 0))  # Меняем ETag при каждом обновлении
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
