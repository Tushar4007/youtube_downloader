import os
from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    url = request.form['url']
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            video_title = info_dict.get('title')
            thumbnail = info_dict.get('thumbnail')

            video_audio = []
            video_only = []
            audio_only = []

            for f in formats:
                format_id = f.get('format_id')
                ext = f.get('ext')
                acodec = f.get('acodec')
                vcodec = f.get('vcodec')
                height = f.get('height')
                filesize = f.get('filesize') or 0

                if not format_id or not ext:
                    continue

                label = f"{ext.upper()} - "
                if height:
                    label += f"{height}p"
                elif acodec != 'none':
                    label += "Audio"

                size_str = f"{round(filesize / 1024 / 1024, 1)} MB" if filesize > 0 else ""
                if size_str:
                    label += f" - {size_str}"

                format_info = {
                    'format_id': format_id,
                    'ext': ext,
                    'label': label,
                    'filesize': filesize
                }

                if acodec != 'none' and vcodec != 'none':
                    video_audio.append(format_info)
                elif acodec == 'none' and vcodec != 'none':
                    video_only.append(format_info)
                elif acodec != 'none' and vcodec == 'none':
                    audio_only.append(format_info)

            return jsonify({
                'title': video_title,
                'thumbnail': thumbnail,
                'video_audio': video_audio,
                'video_only': video_only,
                'audio_only': audio_only
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/download_high_quality', methods=['POST'])
def download_high_quality():
    url = request.form['url']
    try:
        ydl_opts = {
            'format': 'bv+ba',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s_best.%(ext)s'),
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            predicted_filename = ydl.prepare_filename(info).replace('.webm', '.mp4')

            if os.path.exists(predicted_filename):
                os.remove(predicted_filename)

            info = ydl.extract_info(url, download=True)
            final_filename = ydl.prepare_filename(info).replace('.webm', '.mp4')

        return send_file(final_filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    url = request.form['url']
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename_base = os.path.splitext(ydl.prepare_filename(info))[0]
            mp3_filename = filename_base + ".mp3"

            if os.path.exists(mp3_filename):
                os.remove(mp3_filename)

            ydl.download([url])

        return send_file(mp3_filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
