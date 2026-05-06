from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/googleb0869499d662e38b.html')
def google_verify():
    return send_file('googleb0869499d662e38b.html')@app.route('/')
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
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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

        if 'mp3' in label.lower():
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp3')

        elif 'flac' in label.lower():
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'}],
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.flac')

        elif '1080' in label:
            ydl_opts = {
                'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')

        elif '720' in label:
            ydl_opts = {
                'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')

        elif '360' in label:
            ydl_opts = {
                'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')

        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
            }
            final_file = os.path.join(DOWNLOAD_FOLDER, f'{uid}.mp4')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(final_file, as_attachment=True, download_name=f'y22mate.{ext}')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

