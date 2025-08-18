from flask import Flask, request, send_file, jsonify
import pydub
import io

app = Flask(__name__)

@app.route('/convert-to-mp3', methods=['POST'])
def convert_audio():
    # --- 1. Get the raw M4A data from the request body ---
    m4a_bytes = request.data
    if not m4a_bytes:
        return jsonify({"error": "Request body is empty. M4A data is required."}), 400

    print(f"Received {len(m4a_bytes)} bytes of M4A data for conversion.")

    try:
        # --- 2. Convert the audio using pydub ---
        # Use BytesIO to treat the received bytes as an in-memory file
        m4a_in_memory_file = io.BytesIO(m4a_bytes)

        print("Converting M4A to MP3 in memory...")
        sound = pydub.AudioSegment.from_file(m4a_in_memory_file, format="m4a")

        # Create another in-memory file for the MP3 output
        mp3_in_memory_file = io.BytesIO()
        sound.export(mp3_in_memory_file, format="mp3", bitrate="192k")
        mp3_in_memory_file.seek(0)  # Rewind to the beginning

        print("Conversion complete. Sending MP3 data back.")
        
        # --- 3. Send the MP3 data back to the Unity client ---
        return send_file(
            mp3_in_memory_file,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='audio.mp3'
        )
    except pydub.exceptions.CouldntDecodeError:
        print("Error: pydub could not decode the provided audio data.")
        return jsonify({"error": "Invalid or corrupt M4A data provided."}), 400
    except Exception as e:
        print(f"An unexpected error occurred during conversion: {e}")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)