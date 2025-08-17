from flask import Flask, request, jsonify
from pytube import YouTube
import logging

# Set up basic logging to see errors in Render's logs
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        app.logger.error("URL parameter is missing from request.")
        return jsonify({"error": "URL parameter is missing"}), 400

    app.logger.info(f"Received request for URL: {video_url}")

    try:
        yt = YouTube(video_url)
        
        # We look for a progressive stream (video + audio) in mp4 format.
        # Then we order by resolution and pick the best one.
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            app.logger.warning(f"No suitable MP4 stream found for {video_url}")
            return jsonify({"error": "No suitable MP4 stream found"}), 404

        video_data = {
            "title": yt.title,
            "thumbnail_url": yt.thumbnail_url,
            "download_url": stream.url 
        }
        
        app.logger.info(f"Successfully found stream for '{yt.title}'")
        return jsonify(video_data)

    except Exception as e:
        app.logger.error(f"An exception occurred for URL {video_url}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)