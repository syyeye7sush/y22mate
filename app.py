 from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import time
import requests
import tempfile

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

COBALT_API = "https://api.cobalt.tools/api/json"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def cobalt_download(url, quality="1080", audio_only=False, audio_format="mp3"):
    payload = {
        "url": url,
        "vQuality": quality,
        "aFormat": audio_format,
        "isAudioOnly": audio_only,
        "isNoTTWatermark": True,
        "isTTFullAudio": False,
        "isAudioMuted": False,
        "dubLang": False,
        "disableMetadata": False,
    }
    try:
        r = requests.post(COBALT_API, json=payload, headers=HEADERS, timeout=30)
        data = r.json()
        return data
    except Exception as e:
        return {"status": "error", "text": str(e)}

@app.route('/googleb0869499d662e38b.html')
def google_verify():
    return send_file('googleb0869499d662e38b.html')

@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    try:
        result = cobalt_download(url, quality="1080")
        if result.get('status') in ['stream', 'redirect', 'tunnel', 'picker']:
            return jsonify({
                'title': 'Video Ready',
                'thumbnail': '',
                'duration': 0,
                'platform': 'YouTube',
            })
        else:
            return jsonify({'error': result.get('text', 'Could not analyze')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url', '')
    label = data.get('label', '')
    ext = data.get('ext', 'mp4')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    try:
        audio_only = 'mp3' in label.lower() or 'flac' in label.lower()
        audio_format = 'flac' if 'flac' in label.lower() else 'mp3'

        if '1080' in label:
            quality = '1080'
        elif '720' in label:
            quality = '720'
        elif '360' in label:
            quality = '360'
        else:
            quality = '1080'

        result = cobalt_download(url, quality=quality, audio_only=audio_only, audio_format=audio_format)

        status = result.get('status')

        if status in ['redirect', 'stream', 'tunnel']:
            download_url = result.get('url')
            if not download_url:
                return jsonify({'error': 'No download URL'}), 500

            uid = str(int(time.time()))
            filepath = os.path.join(DOWNLOAD_FOLDER, f'{uid}.{ext}')

            r = requests.get(download_url, stream=True, timeout=60)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            return send_file(filepath, as_attachment=True, download_name=f'y22mate.{ext}')

        elif status == 'picker':
            picker = result.get('picker', [])
            if picker:
                download_url = picker[0].get('url')
                uid = str(int(time.time()))
                filepath = os.path.join(DOWNLOAD_FOLDER, f'{uid}.{ext}')
                r = requests.get(download_url, stream=True, timeout=60)
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return send_file(filepath, as_attachment=True, download_name=f'y22mate.{ext}')
            else:
                return jsonify({'error': 'No video found'}), 500
        else:
            return jsonify({'error': result.get('text', 'Download failed')}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
