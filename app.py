import os
import socket
import threading
from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp

app = Flask(__name__, template_folder='.')

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def find_free_port(start=5000, end=6000):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("❌ No free port found!")

def do_download(url, format_id=None):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }

        if format_id and format_id.startswith('audio_'):
            codec = format_id.replace('audio_', '').split('_')[0]
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': '192',
            }]
            ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_FOLDER, f'%(title)s.{codec}')
        elif format_id:
            ydl_opts['format'] = format_id
            if 'video' in format_id or 'bv+ba' in format_id:
                ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bv+ba'
            ydl_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Finished downloading {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    format_id = request.form['format_id']
    try:
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            predicted_filename = ydl.prepare_filename(info)

            if os.path.exists(predicted_filename):
                os.remove(predicted_filename)

            info = ydl.extract_info(url, download=True)
            final_filename = ydl.prepare_filename(info)

        return send_file(final_filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = find_free_port()
    print(f"✅ App running at: http://127.0.0.1:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
