from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp
import os

app = Flask(__name__)
DOWNLOADS_DIR = "videos"
COOKIES_FILE = "cookies_youtube.txt"  # Nome do arquivo de cookies

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/baixar', methods=['POST'])
def baixar_video():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify(success=False, error="URL não fornecida")

    try:
        if not os.path.isfile(COOKIES_FILE):
            raise FileNotFoundError(f"Arquivo de cookies não encontrado: {COOKIES_FILE}")

        # Opções para extração de info
        ydl_opts_info = {
            'outtmpl': f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'cookiefile': COOKIES_FILE,
        }

        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            print("Formatos disponíveis:", formats)

            best_format = None
            for format in formats:
                if format['ext'] == 'mp4' and format['vcodec'] != 'none' and format['acodec'] != 'none':
                    best_format = format
                    break

            if not best_format:
                best_format = max(
                    (f for f in formats if f.get('height') is not None),
                    key=lambda f: f['height'],
                    default=None
                )

            if best_format is None:
                raise ValueError("Nenhum formato válido encontrado para o vídeo.")

        # Opções para download real
        ydl_opts_download = {
            'outtmpl': f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'cookiefile': COOKIES_FILE,
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        }

        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename_only = os.path.basename(filename)

        return jsonify(success=True, filename=f'/videos/{filename_only}')

    except Exception as e:
        print("Erro:", e)
        return jsonify(success=False, error=str(e))

@app.route('/videos/<path:filename>')
def servir_video(filename):
    return send_from_directory(DOWNLOADS_DIR, filename)

if __name__ == '__main__':
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    app.run(debug=True)
