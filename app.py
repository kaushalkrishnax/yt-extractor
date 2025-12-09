from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

def num(x):
    return int(x) if x else 0

@app.route("/extract", methods=["GET"])
def extract_media():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missingUrl"}), 400

    try:
        ydl = yt_dlp.YoutubeDL({"quiet": True, "skip_download": True})
        info = ydl.extract_info(url, download=False)

        audio_webm = []
        audio_m4a = []
        video_webm = []

        thumbs = []
        for t in (info.get("thumbnails") or []):
            h = num(t.get("height"))
            w = num(t.get("width"))
            if h and w:
                thumbs.append({
                    "url": t.get("url"),
                    "width": w,
                    "height": h,
                    "id": t.get("id")
                })

        thumbs.sort(key=lambda x: x["height"])
        thumbs = thumbs[-4:]

        for f in info.get("formats", []):
            if f.get("protocol") in ["m3u8", "m3u8_native", "http_dash_segments"]:
                continue

            ac = f.get("acodec")
            vc = f.get("vcodec")
            ext = f.get("ext")

            item = {
                "url": f.get("url"),
                "ext": ext,
                "filesize": num(f.get("filesize")),
                "acodec": ac,
                "vcodec": vc,
                "fps": f.get("fps"),
                "height": num(f.get("height")),
                "width": num(f.get("width")),
                "bitrateAudio": f.get("abr"),
                "bitrateVideo": f.get("vbr"),
                "mimeType": f.get("mime_type")
            }

            if vc == "none" and ac != "none":
                if ext == "webm":
                    audio_webm.append(item)
                elif ext in ["m4a", "mp4"]:
                    audio_m4a.append(item)

            if vc and vc != "none" and ac in [None, "none"] and ext == "webm":
                video_webm.append(item)

        audio_webm.sort(key=lambda x: x["filesize"])
        audio_m4a.sort(key=lambda x: x["filesize"])
        video_webm.sort(key=lambda x: x["height"])

        return jsonify({
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "channel": info.get("uploader"),
            "channelId": info.get("channel_id"),
            "duration": info.get("duration"),
            "category": info.get("categories"),
            "tags": info.get("tags"),
            "uploadDate": info.get("upload_date"),
            "viewCount": info.get("view_count"),
            "likeCount": info.get("like_count"),
            "thumbnails": thumbs,
            "webpageUrl": info.get("webpage_url"),
            "urls": {
                "audio": {
                    "webm": audio_webm,
                    "m4a": audio_m4a
                },
                "video": video_webm
            }
        })

    except Exception as e:
        return jsonify({"error": "ytDlpFailed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
