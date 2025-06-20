from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile
import re

app = Flask(__name__)

def clean_subtitles(subtitle_file):
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
        content = re.sub(r'\n\n+', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)

    except Exception as e:
        return f"Error cleaning subtitles: {str(e)}"

def download_and_clean_subtitles(video_url, languages):
    with tempfile.TemporaryDirectory() as temp_dir:
        for lang in languages:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [lang],
                'skip_download': True,
                'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                'subtitlesformat': 'srt',
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    video_title = info.get('title', 'Unknown')
                    ydl.download([video_url])

                    subtitle_file = None
                    for file in os.listdir(temp_dir):
                        if file.endswith(f'.{lang}.srt'):
                            subtitle_file = os.path.join(temp_dir, file)
                            break

                    if subtitle_file and os.path.exists(subtitle_file):
                        cleaned_text = clean_subtitles(subtitle_file)
                        return {
                            'success': True,
                            'video_title': video_title,
                            'subtitles': cleaned_text,
                            'language': lang
                        }

            except Exception as e:
                return {'success': False, 'error': str(e)}

        return {
            'success': False,
            'error': 'No subtitles found for specified languages.'
        }

@app.route('/')
def home():
    return """
    <h1>🎬 YouTube Subtitle API</h1>
    <p>Use <code>/subtitles?url=...&language=ru</code> to fetch subtitles.</p>
    """

@app.route('/subtitles', methods=['GET'])
def get_subtitles():
    try:
        video_url = request.args.get('url')
        preferred_language = request.args.get('language', 'ru')

        if not video_url:
            return jsonify({
                'success': False,
                'error': 'URL parameter is required.'
            }), 400

        if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL.'
            }), 400

        # Try first with preferred language, then fallback to English
        result = download_and_clean_subtitles(video_url, [preferred_language, 'en'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("🚀 Starting YouTube Subtitle API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
