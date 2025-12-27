import os  # Для os.environ
from flask import Flask, request, Response, render_template_string
import io

app = Flask(__name__)

# Пароль для сайта (используй Environment Variable на Render)
SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'JarvisGiminiScreenLook2_5')  # Замени 'defaultpassword' на запасной

latest_image = None

# HTML с автообновлением (каждые 2 сек)
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
        setInterval(() => {
            document.getElementById('screen').src = '/latest.jpg?t=' + Date.now();
        }, 2000);  # Обновление каждые 2 сек
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
    global latest_image
    if 'image' not in request.files:
        return 'Нет изображения', 400
    file = request.files['image']
    latest_image = file.read()
    return 'OK', 200

@app.route('/latest.jpg')
@app.route('/latest.jpg')
def latest_jpg():
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return 'Неверный пароль', 401
    if latest_image is None:
        return 'Нет изображения', 404
    response = Response(latest_image, mimetype='image/jpeg')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # ← Добавьте эти 3 строки
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
