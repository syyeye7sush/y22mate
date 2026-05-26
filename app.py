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
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
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
    label = data.get('label', '')
    ext = data.get('ext', 'mp4')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    try:
        uid = str(int(time.time()))
        out = os.path.join(DOWNLOAD_FOLDER, f'{uid}.%(ext)s')
        opts = dict(YDL_BASE)
        if 'mp3' in label.lower():
            opts.update({'format':'bestaudio[ext=m4a]/bestaudio','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.m4a')
        elif 'flac' in label.lower():
            opts.update({'format':'bestaudio[ext=m4a]/bestaudio','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.m4a')
        elif '1080' in label:
            opts.update({'format':'best[height<=1080][ext=mp4]/best[height<=1080]/best','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')
        elif '720' in label:
            opts.update({'format':'best[height<=720][ext=mp4]/best[height<=720]/best','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')
        elif '360' in label:
            opts.update({'format':'best[height<=360][ext=mp4]/best[height<=360]/best','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')
        else:
            opts.update({'format':'best[ext=mp4]/best','outtmpl':out})
            final = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return send_file(final, as_attachment=True, download_name=f'y22mate.{ext}')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
