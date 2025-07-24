from flask import Flask, render_template, request, send_file, jsonify
from pydub import AudioSegment
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("audio_files[]")
    order = request.form.getlist("order[]")
    pause_duration = int(request.form.get("pause_duration", 1000))

    # Clear old files
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))
    for f in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, f))

    uploaded_files = {}
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        uploaded_files[filename] = filepath

    ordered_paths = [uploaded_files[name] for name in order]

    combined = None
    for path in ordered_paths:
        audio = AudioSegment.from_file(path)
        if combined is None:
            combined = audio
        else:
            silence = AudioSegment.silent(duration=pause_duration)
            combined += silence + audio

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_FOLDER, f"output_{timestamp}.mp3")
    combined.export(output_file, format="mp3")

    return jsonify({"download_url": f"/download/{os.path.basename(output_file)}"})

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
