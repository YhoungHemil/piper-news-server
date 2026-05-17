import os
import subprocess
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# Temporary directory space provided for free by Serverless platforms
VOICE_DIR = "/tmp/voices"
os.makedirs(VOICE_DIR, exist_ok=True)

# Pre-defined download links for the fast medium-quality voices
VOICE_FILES = {
    "en.onnx": "https://huggingface.co",
    "en.json": "https://huggingface.co.json",
    "es.onnx": "https://huggingface.co",
    "es.json": "https://huggingface.co.json",
    "fr.onnx": "https://huggingface.co",
    "fr.json": "https://huggingface.co.json"
}

def ensure_voices_downloaded():
    """Download models into temporary storage during the function's initial call"""
    for name, url in VOICE_FILES.items():
        path = os.path.join(VOICE_DIR, name)
        if not os.path.exists(path):
            r = requests.get(url, stream=True)
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

@app.route('/api/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    
    if not text:
        return "Missing text parameter", 400

    ensure_voices_downloaded()

    # Route request to selected file path
    if lang == "es":
        model_path = os.path.join(VOICE_DIR, "es.onnx")
    elif lang == "fr":
        model_path = os.path.join(VOICE_DIR, "fr.onnx")
    else:
        model_path = os.path.join(VOICE_DIR, "en.onnx")

    command = ["piper", "--model", model_path, "--output_raw"]

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        stdout, _ = process.communicate(input=text.encode('utf-8'))
        return Response(stdout, mimetype="audio/wav")
    except Exception as e:
        return f"Engine Error: {str(e)}", 500
                  
