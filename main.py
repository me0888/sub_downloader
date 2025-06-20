
from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile
import re

app = Flask(__name__)

def clean_subtitles(subtitle_file):
    """
    Очищает субтитры от временных отрезков и оставляет только текст
    """
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Удаляем номера строк
        content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)
        
        # Удаляем временные метки (формат: 00:00:00,000 --> 00:00:00,000)
        content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
        
        # Удаляем лишние пустые строки
        content = re.sub(r'\n\n+', '\n', content)
        
        # Убираем HTML теги если есть
        content = re.sub(r'<[^>]+>', '', content)
        
        # Убираем лишние пробелы
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    except Exception as e:
        return f"Ошибка при очистке субтитров: {str(e)}"

def download_and_clean_subtitles(video_url, language='ru'):
    """
    Скачивает и очищает субтитры
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Настройки для yt-dlp
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language],
            'skip_download': True,
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'subtitlesformat': 'srt',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Unknown')
                
                # Скачиваем субтитры
                ydl.download([video_url])
                
                # Ищем скачанный файл субтитров
                subtitle_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith(f'.{language}.srt'):
                        subtitle_file = os.path.join(temp_dir, file)
                        break
                
                if subtitle_file and os.path.exists(subtitle_file):
                    cleaned_text = clean_subtitles(subtitle_file)
                    return {
                        'success': True,
                        'video_title': video_title,
                        'subtitles': cleaned_text,
                        'language': language
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Субтитры на языке {language} не найдены'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

@app.route('/', methods=['GET'])
def home():
    """
    Главная страница с инструкциями
    """
    return """
    <h1>🎬 YouTube Subtitle API</h1>
    <h2>Как использовать:</h2>
    <p><strong>POST запрос на /subtitles</strong></p>
    <p>Параметры JSON:</p>
    <ul>
        <li><code>url</code> - URL YouTube видео (обязательно)</li>
        <li><code>language</code> - код языка субтитров (по умолчанию: ru)</li>
    </ul>
    
    <h3>Пример запроса:</h3>
    <pre>
POST /subtitles
Content-Type: application/json

{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ru"
}
    </pre>
    
    <h3>Пример ответа:</h3>
    <pre>
{
    "success": true,
    "video_title": "Название видео",
    "subtitles": "Очищенный текст субтитров...",
    "language": "ru"
}
    </pre>
    
    <h3>Коды языков:</h3>
    <ul>
        <li>ru - русский</li>
        <li>en - английский</li>
        <li>es - испанский</li>
        <li>fr - французский</li>
        <li>de - немецкий</li>
    </ul>
    """

@app.route('/subtitles', methods=['POST'])
def get_subtitles():
    """
    API endpoint для получения субтитров
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL параметр обязателен'
            }), 400
        
        video_url = data['url']
        language = data.get('language', 'ru')
        
        # Простая валидация URL
        if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
            return jsonify({
                'success': False,
                'error': 'Неверный YouTube URL'
            }), 400
        
        result = download_and_clean_subtitles(video_url, language)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Проверка состояния сервиса
    """
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("🚀 Запуск YouTube Subtitle API сервера...")
    print("📝 Документация доступна на: http://0.0.0.0:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)
