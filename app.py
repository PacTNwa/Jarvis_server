from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import base64
from datetime import datetime

app = Flask(__name__)

# Папка для фото (Render.com сохраняет в /tmp или используй persistent storage если нужно)
PHOTOS_DIR = 'static/photos'
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

# HTML + JS — всё в одной строке
INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Просто камера</title>
    <style>
        body { margin:0; padding:20px; background:#000; color:#0f0; font-family:monospace; text-align:center; }
        video { max-width:100%; border:2px solid #0f0; border-radius:8px; margin:20px 0; }
        button { padding:15px 40px; font-size:22px; background:#0f0; color:#000; border:none; border-radius:8px; cursor:pointer; margin:20px; }
        #photos { display:flex; flex-wrap:wrap; justify-content:center; }
        .photo { margin:15px; background:#111; padding:10px; border-radius:8px; }
        .photo img { max-width:320px; border:1px solid #0f0; border-radius:6px; }
        h1 { color:#0f0; text-shadow:0 0 10px #0f0; }
    </style>
</head>
<body>
    <h1>Камера → Фото</h1>
    
    <video id="video" autoplay playsinline></video>
    <br>
    <button onclick="snap()">Сфоткать</button>
    
    <canvas id="canvas" style="display:none;"></canvas>
    
    <h2>Сохранённые фото</h2>
    <div id="photos">
        {% for photo in photos %}
        <div class="photo">
            <img src="/photos/{{ photo }}">
            <p>{{ photo }}</p>
        </div>
        {% endfor %}
    </div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(stream => video.srcObject = stream)
            .catch(err => alert("Камера не открылась: " + err));

        function snap() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const dataUrl = canvas.toDataURL('image/jpeg');
            
            fetch('/snap', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: dataUrl})
            })
            .then(r => r.json())
            .then(res => {
                if (res.ok) location.reload();
                else alert("Ошибка: " + res.error);
            })
            .catch(err => alert("Сеть: " + err));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    photos = sorted(os.listdir(PHOTOS_DIR), reverse=True)
    return render_template_string(INDEX_HTML, photos=photos)

@app.route('/snap', methods=['POST'])
def snap():
    try:
        data = request.json['data']
        img_data = base64.b64decode(data.split(',')[1])

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{ts}.jpg"
        path = os.path.join(PHOTOS_DIR, filename)

        with open(path, 'wb') as f:
            f.write(img_data)

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/photos/<path:filename>')
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
