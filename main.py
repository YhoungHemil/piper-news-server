import os
import subprocess
import requests
import sys
from flask import Flask, request, Response

app = Flask(__name__)

VOICES_DIR = "/tmp/voices"
os.makedirs(VOICES_DIR, exist_ok=True)

# Real Hugging Face URLs (working)
VOICE_URLS = {
    "en_US-lessac-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    "en_US-lessac-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    "es_ES-sharvard-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx",
    "es_ES-sharvard-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json",
    "fr_FR-siwis-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
    "fr_FR-siwis-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
}

def download_file(url, dest_path):
    """Download a file with streaming"""
    print(f"Downloading {dest_path}...", flush=True)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {dest_path}", flush=True)

def ensure_model(model_name):
    """Ensure model file exists, download if missing"""
    onnx_path = os.path.join(VOICES_DIR, model_name)
    json_path = onnx_path + ".json"
    if not os.path.exists(onnx_path):
        download_file(VOICE_URLS[model_name], onnx_path)
    if not os.path.exists(json_path):
        download_file(VOICE_URLS[model_name + ".json"], json_path)

# PRE-DOWNLOAD ALL MODELS AT STARTUP (avoids timeout on first request)
for lang_model in ["en_US-lessac-medium.onnx", "es_ES-sharvard-medium.onnx", "fr_FR-siwis-medium.onnx"]:
    ensure_model(lang_model)

@app.route('/api/tts', methods=['GET'])
def tts():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    
    if not text:
        return "Missing text", 400
        
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
    return {"status": "ok", "models": os.listdir(VOICES_DIR)}

if __name__ == "__main__":
    print("Starting Flask server on port 5000", flush=True)
    app.run(host="0.0.0.0", port=5000, threaded=True)
