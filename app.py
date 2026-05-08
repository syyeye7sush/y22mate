from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import time
import tempfile

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

COOKIES_CONTENT = """# Netscape HTTP Cookie File
.youtube.com\tTRUE\t/\tFALSE\t1841201179\tSID\tg.a0009ghT5Ox0JcaL6KX1qJWADHbU1tDfd7Ujylj6pFw9pTfcpNSDU7vQLskdJREebAPgtIpb1QACgYKAcoSARASFQHGX2Mi3a-ROwijvC-c-mwNiA3KlxoVAUF8yKofD5AgMa3AQpjuahBdeh8S0076
.youtube.com\tTRUE\t/\tTRUE\t1841201179\tSAPISID\t7Hb23n_godvp3H8l/Aet7qcP8VprT44Yer
.youtube.com\tTRUE\t/\tTRUE\t1841201179\tSSID\tAu01dIK7ZvVeETMSc
.youtube.com\tTRUE\t/\tFALSE\t1841201179\tAPISID\ti7X_Kwea_Anhbw0B/AmYZ2D03KFnnJmPId
.youtube.com\tTRUE\t/\tFALSE\t1841201179\tHSID\tA6UDhq3UN8ftuPvFP
.youtube.com\tTRUE\t/\tTRUE\t1841201179\t__Secure-1PSID\tg.a0009ghT5Ox0JcaL6KX1qJWADHbU1tDfd7Ujylj6pFw9pTfcpNSDOIkcdNcOV9xEz7EyhlH57gACgYKAWgSARASFQHGX2MiSKyDVQiVaXWdFykRzZByShoVAUF8yKqMe5e7l7dMc4oGnDggCUDK0076
.youtube.com\tTRUE\t/\tTRUE\t1841201179\t__Secure-3PSID\tg.a0009ghT5Ox0JcaL6KX1qJWADHbU1tDfd7Ujylj6pFw9pTfcpNSDQk0-14mLMQcKiIIOYc02OAACgYKAaUSARASFQHGX2MiRqrcIQOMYcoCP834s8jgSxoVAUF8yKqOuwDxXLImsUcdZ1StuVTF0076
.youtube.com\tTRUE\t/\tFALSE\t1809665185\tSIDCC\tAKEyXzWIuc53UuK3pBICHy5kVm4NMJttjO-tQTkgXeuM1dXD2XAV58YUV7oLD5O9GEf6TTQN
.youtube.com\tTRUE\t/\tTRUE\t1809665185\t__Secure-1PSIDCC\tAKEyXzVNH6QFz5AqRarWFQasoahskw6KsdJpBcEfwrYkigdZ5z4D4Sw7ri1B2JzHT__Ymhxj
.youtube.com\tTRUE\t/\tTRUE\t1809665185\t__Secure-3PSIDCC\tAKEyXzU-BHd_UHmy24B_cFZPxyBqPm8enyd9qIE4M_gFLTR_rx95SX-4fvFDbVs-RE9aDQq2
.youtube.com\tTRUE\t/\tTRUE\t1793681180\tVISITOR_INFO1_LIVE\tRQiF6Mw9GnQ
.youtube.com\tTRUE\t/\tTRUE\t1841201181\tPREF\ttz=Asia.Kolkata
"""

def get_cookies_file():
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    tmp.write(COOKIES_CONTENT)
    tmp.close()
    return tmp.name

def get_ydl_opts(label, output_template):
    cookies_file = get_cookies_file()
    base = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookies_file,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.4430.91 Mobile Safari/537.36'},
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
        base['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
    elif '720' in label:
        base['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
    elif '360' in label:
        base['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
    else:
        base['format'] = 'bestvideo+bestaudio/best'
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
        cookies_file = get_cookies_file()
        opts = {
            'quiet': True,
            'no_warnings': True,
            'cookiefile': cookies_file,
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
