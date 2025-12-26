from flask import Flask, request, Response, render_template_string
import io
from PIL import Image

app = Flask(__name__)

# Пароль для доступа
WEB_PASSWORD = os.environ.get('SITE_PASSWORD')  # Замени на свой

# Последнее изображение (в памяти)
latest_image = None

# HTML страница с автообновлением
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Screen View</title>
<style>
body { margin:0; background:#000; display:flex; justify-content:center; align-items:center; height:100vh; }
img { max-width:100vw; max-height:100vh; object-fit:contain; }
</style>
</head>
<body>
<img id="screen" src="/latest.jpg">
<script>
setInterval(function() {
  document.getElementById('screen').src = '/latest.jpg?t=' + new Date().getTime();
}, 5000);  # Обновление каждые 5 сек
</script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    if request.authorization and request.authorization.password == WEB_PASSWORD:
        return render_template_string(HTML)
    return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

@app.route('/upload', methods=['POST'])
def upload():
    global latest_image
    if 'image' in request.files:
        file = request.files['image']
        latest_image = file.read()
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/latest.jpg')
def latest_jpg():
    if latest_image is None:
        return 'No image', 404
    if request.authorization and request.authorization.password == WEB_PASSWORD:
        return Response(latest_image, mimetype='image/jpeg')
    return 'Unauthorized', 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
