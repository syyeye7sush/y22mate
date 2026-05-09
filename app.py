from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import requests

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://piped-api.garudalinux.org",
    "https://api.piped.projectsegfau.lt",
    "https://pipedapi.tokhmi.xyz",
]

def get_piped_streams(video_id):
    for instance in PIPED_INSTANCES:
        try:
            r = requests.get(f"{instance}/streams/{video_id}", timeout=10)
            if r.status_code == 200:
                return r.json()
        except:
            continue
    return None

def extract_video_id(url):
    import re
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

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
        streams = get_piped_streams(video_id)
        if not streams:
            return jsonify({'error': 'Could not fetch video info'}), 500
        return jsonify({
            'title': streams.get('title', 'Video'),
            'thumbnail': streams.get('thumbnailUrl', ''),
            'duration': streams.get('duration', 0),
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
            # Non-YouTube - use yt-dlp
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

        # YouTube - use Piped
        streams = get_piped_streams(video_id)
        if not streams:
            return jsonify({'error': 'Could not fetch streams'}), 500

        download_url = None

        if 'mp3' in label.lower() or 'flac' in label.lower():
            audio_streams = streams.get('audioStreams', [])
            if audio_streams:
                audio_streams.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
                download_url = audio_streams[0].get('url')
                ext = 'mp3'
        else:
            video_streams = streams.get('videoStreams', [])
            if '1080' in label:
                target = 1080
            elif '720' in label:
                target = 720
            elif '360' in label:
                target = 360
            else:
                target = 1080

            # Find best matching quality
            mp4_streams = [s for s in video_streams if 'mp4' in s.get('mimeType', '').lower() and s.get('videoOnly', False) == False]
            if not mp4_streams:
                mp4_streams = [s for s in video_streams if s.get('videoOnly', False) == False]

            if mp4_streams:
                best = min(mp4_streams, key=lambda x: abs(x.get('height', 0) - target))
                download_url = best.get('url')
            elif video_streams:
                best = min(video_streams, key=lambda x: abs(x.get('height', 0) - target))
                download_url = best.get('url')

        if not download_url:
            return jsonify({'error': 'No stream found'}), 500

        uid = str(int(time.time()))
        filepath = os.path.join(DOWNLOAD_FOLDER, f'{uid}.{ext}')

        r = requests.get(download_url, stream=True, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'
        })
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        return send_file(filepath, as_attachment=True, download_name=f'y22mate.{ext}')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
