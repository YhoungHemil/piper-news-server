import os
import subprocess
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# CHANGED: use writable /tmp directory (fixes read-only error)
VOICES_DIR = "/tmp/voices"
os.makedirs(VOICES_DIR, exist_ok=True)

# REAL working Hugging Face URLs (updated from placeholders)
VOICE_URLS = {
    "en_US-lessac-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    "en_US-lessac-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    "es_ES-sharvard-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx",
    "es_ES-sharvard-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json",
    "fr_FR-siwis-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
    "fr_FR-siwis-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
}

def download_if_missing(model_name):
    """Downloads the model files on demand if they aren't present"""
    onnx_path = os.path.join(VOICES_DIR, model_name)
    json_path = onnx_path + ".json"
    
    # Download ONNX file
    if not os.path.exists(onnx_path):
        print(f"Downloading {model_name}...", flush=True)
        r = requests.get(VOICE_URLS[model_name], stream=True)
        r.raise_for_status()
        with open(onnx_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    # Download JSON configuration file
    if not os.path.exists(json_path):
        json_key = model_name + ".json"
        print(f"Downloading {json_key}...", flush=True)
        r = requests.get(VOICE_URLS[json_key], stream=True)
        r.raise_for_status()
        with open(json_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

@app.route("/api/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    
    if not text: 
        return "Missing text", 400
        
    if lang == "es": 
        model_name = "es_ES-sharvard-medium.onnx"
    elif lang == "fr": 
        model_name = "fr_FR-siwis-medium.onnx"
    else: 
        model_name = "en_US-lessac-medium.onnx"
        
    # Download the voice file right before generating audio
    try:
        download_if_missing(model_name)
    except Exception as e:
        return f"Model download error: {str(e)}", 500
    
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
