from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_ydl_opts(label, output_template):
    base = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.4430.91 Mobile Safari/537.36'},
        'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}],
    }
    if 'mp3' in label.lower():
        base['format'] = 'bestaudio/best'
        base['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
        base.pop('merge_output_format', None)
    elif 'flac' in label.lower():
        base['format'] = 'bestaudio/best'
        base['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'}]
        base.pop('merge_output_format', None)
    elif '1080' in label:
        base['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best'
    elif '720' in label:
        base['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best'
    elif '360' in label:
        base['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best'
    else:
        base['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
    return base

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
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.4430.91 Mobile Safari/537.36'},
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title', 'Video'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'platform': info.get('extractor_key', 'Unknown'),
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
        uid = str(int(time.time()))
        output_template = os.path.join(DOWNLOAD_FOLDER, f'{uid}.%(ext)s')
        opts = get_ydl_opts(label, output_template)
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        final_file = None
        for f in sorted(os.listdir(DOWNLOAD_FOLDER)):
            if f.startswith(uid):
                final_file = os.path.join(DOWNLOAD_FOLDER, f)
                break
        if not final_file:
            return jsonify({'error': 'Download failed'}), 500
        return send_file(final_file, as_attachment=True, download_name=f'y22mate.{ext}')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
