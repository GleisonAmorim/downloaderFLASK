from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp
import os

app = Flask(__name__)
DOWNLOADS_DIR = "videos"
COOKIES_FILE = "cookies.txt"  # Nome do arquivo de cookies

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
        # Definindo opções do yt-dlp para buscar os formatos disponíveis
        ydl_opts = {
            'outtmpl': f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',  # Define o local de saída para o vídeo
            'noplaylist': True,  # Impede o download de playlists
            'quiet': False,  # Habilita log para facilitar o debug, se necessário
            'cookiefile': COOKIES_FILE,  # Refere-se ao arquivo de cookies
        }

        # Inicializando o yt-dlp com as opções definidas
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtendo as informações do vídeo sem baixar inicialmente
            info = ydl.extract_info(url, download=False)

            # Listando todos os formatos disponíveis
            formats = info.get('formats', [])
            print("Formatos disponíveis:", formats)

            # Verificando se existe um formato mp4 de alta qualidade
            best_format = None
            for format in formats:
                if format['ext'] == 'mp4' and format['vcodec'] != 'none' and format['acodec'] != 'none':
                    best_format = format
                    break

            if not best_format:
                # Se não encontrar o formato MP4 com vídeo e áudio, pega o melhor formato disponível
                best_format = max(
                    (f for f in formats if f.get('height') is not None),  # Filtra formatos com 'height' válida
                    key=lambda f: f['height'],  # Compara pela altura
                    default=None
                )

            if best_format is None:
                raise ValueError("Nenhum formato válido encontrado para o vídeo.")

            # Usando o melhor formato encontrado para o download
            ydl_opts['format'] = best_format['format_id']
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Realiza o download do vídeo
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)  # Prepara o nome do arquivo
                filename_only = os.path.basename(filename)  # Extrai o nome do arquivo sem o caminho completo

        return jsonify(success=True, filename=f'/videos/{filename_only}')  # Retorna o caminho para o arquivo baixado

    except Exception as e:
        print("Erro:", e)
        return jsonify(success=False, error=str(e))  # Retorna o erro se houver

@app.route('/videos/<path:filename>')
def servir_video(filename):
    return send_from_directory(DOWNLOADS_DIR, filename)  # Serve o vídeo após o download

if __name__ == '__main__':
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)  # Cria a pasta de vídeos caso não exista
    app.run(debug=True)  # Inicia o servidor Flask
