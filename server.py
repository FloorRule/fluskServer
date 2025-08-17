from flask import Flask, request, jsonify
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Reusable yt-dlp options
YDL_OPTS = {
    # This is the new line. It forces the request to originate from an IPv4 address.
    'source_address': '0.0.0.0', 
    'format': 'best[ext=mp4][vcodec!=h265][acodec!=opus]/best[ext=mp4]/best',
    'quiet': True,
}

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        app.logger.error("URL parameter is missing from request.")
        return jsonify({"error": "URL parameter is missing"}), 400

    app.logger.info(f"Received request for URL: {video_url}")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            
            if not download_url:
                app.logger.warning(f"yt-dlp did not return a download URL for {video_url}")
                return jsonify({"error": "Could not find a direct download URL"}), 404

            video_data = {
                "title": info.get('title', 'Unknown Title'),
                "thumbnail_url": info.get('thumbnail', ''),
                "download_url": download_url
            }
            app.logger.info(f"Successfully found stream for '{info.get('title')}'")
            return jsonify(video_data)

    except yt_dlp.utils.DownloadError as e:
        app.logger.error(f"yt-dlp DownloadError for {video_url}: {str(e)}")
        # Send a user-friendly part of the error back
        if 'confirm you’re not a bot' in str(e):
             return jsonify({"error": "Server is being blocked by YouTube's anti-bot system."}), 503
        return jsonify({"error": "Video is unavailable or private."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected exception occurred for {video_url}: {str(e)}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)