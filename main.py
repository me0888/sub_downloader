from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

def clean_transcript(transcript):
    lines = [entry['text'].strip() for entry in transcript if entry['text'].strip()]
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    return cleaned

def extract_video_id(url):
    import re
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

@app.route('/')
def home():
    return "<h2>Use /subtitles?url=...&language=ru</h2>"

@app.route('/subtitles', methods=['GET'])
def get_subtitles():
    url = request.args.get('url')
    preferred = request.args.get('language', 'ru')
    fallback = 'en'

    if not url:
        return jsonify({'success': False, 'error': 'Missing URL'}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[preferred])
        return jsonify({
            'success': True,
            'language': preferred,
            'subtitles': clean_transcript(transcript)
        })
    except NoTranscriptFound:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[fallback])
            return jsonify({
                'success': True,
                'language': fallback,
                'subtitles': clean_transcript(transcript),
                'note': 'Fallback to English was used'
            })
        except NoTranscriptFound:
            return jsonify({'success': False, 'error': 'No subtitles found in any language'}), 404
    except TranscriptsDisabled:
        return jsonify({'success': False, 'error': 'Subtitles are disabled for this video'}), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
