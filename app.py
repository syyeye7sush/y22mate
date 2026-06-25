from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp, os, time

app = Flask(__name__)
CORS(app)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

YDL_BASE = {
    'quiet': True,
    'no_warnings': True,
    'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    },
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls'],
            'player_client': ['web', 'android'],
        }
    },
    'socket_timeout': 30,
    'retries': 3,
}

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
        opts = dict(YDL_BASE)
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
    ext = data.get('ext', 'mp4')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    try:
        uid = str(int(time.time()))
        out = os.path.join(DOWNLOAD_FOLDER, f'{uid}.%(ext)s')
        opts = dict(YDL_BASE)
        opts['outtmpl'] = out
        final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return send_file(final, as_attachment=True, download_name=f'y22mate.{ext}')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
