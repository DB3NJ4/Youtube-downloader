from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

## Configuración de la aplicación

## INICIO
@app.route("/")
def index():
    return render_template("index.html")

## Obtener información del video
@app.route("/info")
def info():
    video_url = request.args.get("url")
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            data = {
                "title": info_dict.get("title", "Sin título"),
                "duration": f"{int(info_dict['duration'] // 60)}:{int(info_dict['duration'] % 60):02} min",
                "thumbnail": info_dict.get("thumbnail", ""),
            }
            return data
    except Exception as e:
        print("Error al obtener info:", e)
        return {"error": "No se pudo obtener info"}, 400

## Descargar el video
@app.route("/download", methods=["POST"])
def download():
    video_url = request.form["url"]
    video_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, video_id + ".%(ext)s")
    final_path = os.path.join(DOWNLOAD_FOLDER, video_id + ".mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,  # No termina en .mp3 directamente
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,
        "noprogress": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print("❌ Error durante la descarga:")
        print(e)
        return f"❌ Error al descargar el audio: {str(e)}", 500

    if not os.path.exists(final_path):
        return "❌ No se generó el archivo MP3. Verifica que ffmpeg esté instalado y funcionando.", 500

    return send_file(final_path, as_attachment=True, download_name="mi_cancion.mp3")

if __name__ == "__main__":
    app.run(debug=True)
