from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import requests
import re

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

INVIDIOUS_INSTANCES = [
    "https://invidious.snopyta.org",
    "https://yewtu.be",
    "https://invidious.kavin.rocks",
    "https://vid.puffyan.us",
    "https://invidious.lunar.icu",
    "https://inv.riverside.rocks",
    "https://invidious.nerdvpn.de",
    "https://invidious.privacydev.net",
]

def extract_video_id(url):
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_invidious_data(video_id):
    for instance in INVIDIOUS_INSTANCES:
        try:
            r = requests.get(
                f"{instance}/api/v1/videos/{video_id}",
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if r.status_code == 200:
                return r.json(), instance
        except:
            continue
    return None, None

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
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        video_data, instance = get_invidious_data(video_id)
        if not video_data:
            return jsonify({'error': 'Could not fetch video info'}), 500
        return jsonify({
            'title': video_data.get('title', 'Video'),
            'thumbnail': video_data.get('videoThumbnails', [{}])[0].get('url', ''),
            'duration': video_data.get('lengthSeconds', 0),
            'platform': 'YouTube',
        })
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
        video_id = extract_video_id(url)

        if not video_id:
            import yt_dlp
            uid = str(int(time.time()))
            output_template = os.path.join(DOWNLOAD_FOLDER, f'{uid}.%(ext)s')
            ydl_opts = {
                'quiet': True,
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'format': 'bestvideo+bestaudio/best',
            }
            if 'mp3' in label.lower():
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            final_file = None
            for f in sorted(os.listdir(DOWNLOAD_FOLDER)):
                if f.startswith(uid):
                    final_file = os.path.join(DOWNLOAD_FOLDER, f)
                    break
            return send_file(final_file, as_attachment=True, download_name=f'y22mate.{ext}')

        video_data, instance = get_invidious_data(video_id)
        if not video_data:
            return jsonify({'error': 'Could not fetch video'}), 500

        adaptive_formats = video_data.get('adaptiveFormats', [])
        format_streams = video_data.get('formatStreams', [])

        if 'mp3' in label.lower() or 'flac' in label.lower():
            audio_formats = [f for f in adaptive_formats if f.get('type', '').startswith('audio')]
            audio_formats.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
            if audio_formats:
                download_url = audio_formats[0].get('url')
                ext = 'mp3'
            else:
                return jsonify({'error': 'No audio found'}), 500
        else:
            if '1080' in label:
                target = 1080
            elif '720' in label:
                target = 720
            elif '360' in label:
                target = 360
            else:
                target = 1080

            combined = [f for f in format_streams if f.get('type', '').startswith('video')]
            if combined:
                best = min(combined, key=lambda x: abs(int(x.get('resolution', '0p').replace('p','')) - target))
                download_url = best.get('url')
            else:
                video_formats = [f for f in adaptive_formats if f.get('type', '').startswith('video')]
                video_formats = [f for f in video_formats if 'mp4' in f.get('type', '')]
                if video_formats:
                    best = min(video_formats, key=lambda x: abs(x.get('height', 0) - target))
                    download_url = best.get('url')
                else:
                    return jsonify({'error': 'No video found'}), 500

        if not download_url:
            return jsonify({'error': 'No download URL'}), 500

        uid = str(int(time.time()))
        filepath = os.path.join(DOWNLOAD_FOLDER, f'{uid}.{ext}')

        r = requests.get(download_url, stream=True, timeout=120, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'
        })
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return send_file(filepath, as_attachment=True, download_name=f'y22mate.{ext}')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
