from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import requests
import random

app = Flask(__name__)

# Список прокси-серверов (IP:PORT)
PROXIES = [
    "http://181.41.194.186:80",
    "http://168.197.42.74:8082",
    "http://91.103.120.39:80",
    "http://23.247.136.248:80",
    "http://81.22.132.94:15182",
    "http://193.108.119.63:80",
]

def get_transcript_with_random_proxy(video_id):
    # Выбираем случайный прокси из списка
    proxy_url = random.choice(PROXIES)
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    session = requests.Session()
    session.proxies.update(proxies)
    YouTubeTranscriptApi._session = session

    # Получаем субтитры
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript

@app.route('/')
def home():
    return """
    <h1>🎬 YouTube Transcript API with Proxy</h1>
    <p>Use <code>/transcript?url=...</code> to get subtitles.</p>
    """

@app.route('/transcript', methods=['GET'])
def transcript():
    try:
        video_url = request.args.get('url')
        if not video_url:
            return jsonify({'success': False, 'error': 'Missing url param'}), 400

        # Извлечение video_id
        if 'v=' in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
        elif 'youtu.be/' in video_url:
            video_id = video_url.split("youtu.be/")[-1].split("?")[0]
        else:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

        transcript = get_transcript_with_random_proxy(video_id)
        transcript_text = '\n'.join([line['text'] for line in transcript])

        return jsonify({'success': True, 'video_id': video_id, 'transcript': transcript_text}), 200

    except TranscriptsDisabled:
        return jsonify({'success': False, 'error': 'Transcripts are disabled for this video'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("🚀 Starting YouTube Transcript API with Proxy...")
    app.run(host='0.0.0.0', port=5000, debug=True)
