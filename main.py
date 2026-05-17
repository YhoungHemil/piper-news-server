import os
import subprocess
import requests
from flask import Flask, request, Response

app = Flask(__name__)

VOICES_DIR = "/voices"

# Absolute direct URLs for the voice models
VOICE_URLS = {
    "en_US-lessac-medium.onnx": "https://huggingface.co",
    "en_US-lessac-medium.onnx.json": "https://huggingface.co.json",
    "es_ES-sharvard-medium.onnx": "https://huggingface.co",
    "es_ES-sharvard-medium.onnx.json": "https://huggingface.co.json",
    "fr_FR-siwis-medium.onnx": "https://huggingface.co",
    "fr_FR-siwis-medium.onnx.json": "https://huggingface.co.json"
}

def download_if_missing(model_name):
    """Downloads the model files on demand if they aren't present"""
    onnx_path = os.path.join(VOICES_DIR, model_name)
    json_path = onnx_path + ".json"
    
    # Download ONNX file
    if not os.path.exists(onnx_path):
        print(f"Downloading {model_name}...", flush=True)
        r = requests.get(VOICE_URLS[model_name], stream=True)
        with open(onnx_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    # Download JSON configuration file
    if not os.path.exists(json_path):
        r = requests.get(VOICE_URLS[model_name + ".json"], stream=True)
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
        
    # Download the voice file right before generating audio to bypass build timeouts
    download_if_missing(model_name)
    
    model_path = os.path.join(VOICES_DIR, model_name)
    cmd = ["piper", "--model", model_path, "--output_raw"]
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        stdout, _ = proc.communicate(input=text.encode("utf-8"))
        return Response(stdout, mimetype="audio/wav")
    except Exception as e:
        return f"Engine Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
