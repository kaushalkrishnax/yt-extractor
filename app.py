from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/extract", methods=["GET"])
def extract_audio_urls():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url"}), 400

    ydl_opts = {
        "quiet": True,
        "extract_flat": False,
        "skip_download": True,
        "format": "bestaudio/best"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        audio_urls = [
            f["url"] for f in formats
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        return jsonify(audio_urls)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
