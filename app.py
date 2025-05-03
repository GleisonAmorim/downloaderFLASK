from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formats', methods=['POST'])
def get_formats():
    url = request.form['url']

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info['formats']:
                if 'format_id' in f and f.get('vcodec') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('resolution') or f"{f.get('height', 'audio')}p",
                        'ext': f.get('ext'),
                        'filesize': f.get('filesize', 0)
                    })

            return render_template('formats.html', formats=formats, url=url, title=info['title'])
        except Exception as e:
            return f"Erro ao obter formatos: {e}"

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    format_id = request.form['format_id']
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'format': format_id,
        'outtmpl': filepath
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return send_file(filepath, as_attachment=True)
        except Exception as e:
            return f"Erro ao baixar o vídeo: {e}"

if __name__ == '__main__':
    #app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host= '0.0.0.0', port = port)
