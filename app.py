from flask import Flask, render_template_string, request, redirect, url_for
import cv2
import os
import base64
import datetime

app = Flask(__name__)

# Папка для сохранения фото
UPLOAD_FOLDER = 'static/photos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML-шаблон с веб-камерой и кнопкой
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Веб-камера → Фото на сервер</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #111; color: #eee; }
        video, img { max-width: 100%; border: 3px solid #444; border-radius: 8px; margin: 10px; }
        button { padding: 12px 24px; font-size: 18px; margin: 10px; cursor: pointer; }
        #photos { display: flex; flex-wrap: wrap; justify-content: center; }
        .photo { margin: 10px; }
    </style>
</head>
<body>
    <h1>Сделай фото с веб-камеры</h1>
    
    <video id="video" autoplay playsinline></video>
    <br>
    <button onclick="snap()">Сфоткать</button>
    
    <canvas id="canvas" style="display:none;"></canvas>
    
    <h2>Последние фото</h2>
    <div id="photos">
        {% for photo in photos %}
        <div class="photo">
            <img src="{{ url_for('static', filename='photos/' + photo) }}" width="320">
            <p>{{ photo }}</p>
        </div>
        {% endfor %}
    </div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');

        // Запуск камеры
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(err => {
                alert("Не удалось открыть камеру: " + err);
            });

        function snap() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Получаем изображение в base64
            const dataUrl = canvas.toDataURL('image/jpeg');
            
            // Отправляем на сервер
            fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataUrl })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();  // перезагрузка для показа нового фото
                } else {
                    alert("Ошибка загрузки");
                }
            })
            .catch(err => alert("Ошибка: " + err));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Список всех сохранённых фото
    photos = sorted([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('.jpg', '.jpeg'))], reverse=True)
    return render_template_string(INDEX_HTML, photos=photos)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # убираем "data:image/jpeg;base64,"
        img_bytes = base64.b64decode(image_data)
        
        # Сохраняем с красивым именем
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        
        return {"success": True, "filename": filename}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    print("Запускаю сервер... Открой в браузере: http://127.0.0.1:5000")
    print("Если с телефона — http://твой_IP_компьютера:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
