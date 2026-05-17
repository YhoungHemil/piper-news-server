import os
import subprocess
import requests
import sys
import logging
from flask import Flask, request, Response

# Force logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CHANGED: use writable /tmp directory
VOICES_DIR = "/tmp/voices"
os.makedirs(VOICES_DIR, exist_ok=True)

# REAL direct download URLs (working as of 2025)
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
    
    logger.info(f"Checking model: {model_name}")
    
    # Download ONNX file
    if not os.path.exists(onnx_path):
        url = VOICE_URLS.get(model_name)
        if not url:
            raise Exception(f"No URL defined for {model_name}")
        logger.info(f"Downloading {model_name} from {url}...")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(onnx_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded {model_name}")
    
    # Download JSON config
    json_key = model_name + ".json"
    if not os.path.exists(json_path):
        url = VOICE_URLS.get(json_key)
        if not url:
            raise Exception(f"No URL defined for {json_key}")
        logger.info(f"Downloading {json_key}...")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(json_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded {json_key}")

@app.route("/api/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    
    logger.info(f"Request: text='{text[:50]}', lang='{lang}'")
    
    if not text:
        return "Missing text", 400
        
    if lang == "es":
        model_name = "es_ES-sharvard-medium.onnx"
    elif lang == "fr":
        model_name = "fr_FR-siwis-medium.onnx"
    else:
        model_name = "en_US-lessac-medium.onnx"
    
    try:
        download_if_missing(model_name)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return f"Model download error: {str(e)}", 500
    
    model_path = os.path.join(VOICES_DIR, model_name)
    cmd = ["piper", "--model", model_path, "--output_raw"]
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=text.encode("utf-8"))
        
        if proc.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='replace')
            logger.error(f"Piper error (code {proc.returncode}): {error_msg}")
            return f"Piper error: {error_msg}", 500
        
        logger.info(f"Generated {len(stdout)} bytes")
        return Response(stdout, mimetype="audio/wav")
        
    except FileNotFoundError:
        logger.error("Piper binary not found")
        return "Engine Error: Piper binary missing", 500
    except Exception as e:
        logger.exception("Unexpected error")
        return f"Engine Error: {str(e)}", 500

if __name__ == "__main__":
    logger.info("Starting server on port 5000")
    app.run(host="0.0.0.0", port=5000)
