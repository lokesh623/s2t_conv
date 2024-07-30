from flask import Flask, render_template, request, jsonify
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import mediainfo_json
import traceback

# Set the FFMPEG_BINARY and FFMPEG_PROBE environment variables to point to the local ffmpeg binaries
ffmpeg_path = "/usr/bin/ffmpeg"
ffprobe_path = "/usr/bin/ffprobe"

# Debugging: Print paths to ensure they are correct
print(f"ffmpeg_path: {ffmpeg_path}")
print(f"ffprobe_path: {ffprobe_path}")

# Check if the ffmpeg and ffprobe binaries exist
if not os.path.isfile(ffmpeg_path):
    print(f"Error: ffmpeg binary not found at {ffmpeg_path}")
else:
    print(f"ffmpeg binary found at {ffmpeg_path}")

if not os.path.isfile(ffprobe_path):
    print(f"Error: ffprobe binary not found at {ffprobe_path}")
else:
    print(f"ffprobe binary found at {ffprobe_path}")

# Set the environment variables for ffmpeg and ffprobe
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path

# Ensure pydub can find the ffmpeg and ffprobe binaries
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

print(f"AudioSegment.converter: {AudioSegment.converter}")
print(f"AudioSegment.ffprobe: {AudioSegment.ffprobe}")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"})
        
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Debugging: Print the file path to ensure the file is saved correctly
        print(f"Saved file to {file_path}")
        
        # Debugging: Check if the file exists
        if not os.path.isfile(file_path):
            print(f"Error: File not found at {file_path}")
            return jsonify({"error": f"File not found at {file_path}"})

        # Debugging: Print the content of the uploads directory
        print(f"Contents of uploads directory: {os.listdir('uploads')}")

        # Debugging: Check if ffmpeg and ffprobe are accessible
        ffmpeg_test = os.system(f'"{ffmpeg_path}" -version')
        ffprobe_test = os.system(f'"{ffprobe_path}" -version')
        print(f"ffmpeg test result: {ffmpeg_test}")
        print(f"ffprobe test result: {ffprobe_test}")

        # Debugging: Call mediainfo_json directly and print the command
        command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
        print(f"mediainfo_json command: {command}")
        
        media_info = mediainfo_json(file_path)
        print(f"media_info: {media_info}")
        
        audio = AudioSegment.from_file(file_path)
        audio.export(file_path, format="wav")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                return jsonify({"transcription": text})
            except sr.UnknownValueError:
                return jsonify({"error": "Google Speech Recognition could not understand audio"})
            except sr.RequestError as e:
                return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"})
    except Exception as e:
        # Debugging: Print stack trace to diagnose any other issues
        print("Exception occurred while processing upload:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    os.makedirs(r'uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
