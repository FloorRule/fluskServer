from flask import Flask, request, jsonify
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Reusable yt-dlp options
YDL_OPTS = {
    'format': 'best[ext=mp4][vcodec!=h265][acodec!=opus]/best[ext=mp4]/best', # Prioritize compatible mp4
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
        # Use yt-dlp to extract information without downloading
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # The 'url' key contains the direct download link
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
        # Handle specific yt-dlp errors (e.g., video unavailable)
        app.logger.error(f"yt-dlp DownloadError for {video_url}: {str(e)}")
        return jsonify({"error": "Video is unavailable or private."}), 500
    except Exception as e:
        # Handle all other errors
        app.logger.error(f"An unexpected exception occurred for {video_url}: {str(e)}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)