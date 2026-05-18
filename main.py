import os
import subprocess
from flask import Flask, request, Response

app = Flask(__name__)

# Models are pre-downloaded to this directory by download_models.py
VOICES_DIR = "/tmp/voices"

@app.route('/api/tts', methods=['GET'])
def tts():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    
    if not text:
        return "Missing text", 400

    # Model selection logic is preserved
    if lang == "es":
        model_name = "es_ES-sharvard-medium.onnx"
    elif lang == "fr":
        model_name = "fr_FR-siwis-medium.onnx"
    else:
        model_name = "en_US-lessac-medium.onnx"
    
    model_path = os.path.join(VOICES_DIR, model_name)
    cmd = ["piper", "--model", model_path, "--output_raw"]
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=text.encode("utf-8"))
        if proc.returncode != 0:
            return f"Piper error: {stderr.decode()}", 500
        return Response(stdout, mimetype="audio/wav")
    except Exception as e:
        return f"Engine Error: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health():
    # This endpoint helps Choreo confirm the container is ready
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
