from flask import Flask, request, Response, render_template_string
import io
import os

app = Flask(__name__)

# Замени на свой пароль (или Environment Variable)
SITE_PASSWORD = "JarvisGiminiScreenLook2_5"

latest_image = None

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
            document.getElementById('screen').src = '/latest.jpg?t=' + new Date().getTime();
        }, 1000);
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
        print("[SERVER] Нет изображения в запросе")  # ← Лог в консоли Render
        return 'Нет изображения', 400
    file = request.files['image']
    latest_image = file.read()
    print(f"[SERVER] Изображение загружено, размер {len(latest_image)} байт")  # ← Лог в консоли Render
    return 'OK', 200

@app.route('/latest.jpg')
def latest_jpg():
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return 'Неверный пароль', 401
    if latest_image is None:
        print("[SERVER] Нет изображения для отображения")  # ← Лог
        return 'Нет изображения', 404
    print(f"[SERVER] Отправка изображения размером {len(latest_image)} байт")  # ← Лог
    return Response(latest_image, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
