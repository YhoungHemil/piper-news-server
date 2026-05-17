import os
import subprocess
import requests
import sys
import logging
from flask import Flask, request, Response

# Force logging to stdout so Choreo can capture it
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

VOICES_DIR = "/voices"

# ------------------------------------------------------------------
# WARNING: The URLs below are placeholders. Replace them with actual
# direct download links from Hugging Face or your storage.
# Example real URL:
# "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
# ------------------------------------------------------------------
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
    logger.debug(f"ONNX path: {onnx_path}, JSON path: {json_path}")
    
    # Download ONNX file
    if not os.path.exists(onnx_path):
        logger.info(f"Downloading {model_name}...")
        url = VOICE_URLS.get(model_name)
        if not url or url in ["https://huggingface.co", "https://huggingface.co.json"]:
            error_msg = f"Invalid URL for {model_name}. Please set a real download link."
            logger.error(error_msg)
            raise Exception(error_msg)
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(onnx_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded {model_name} successfully")
        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            raise
                
    # Download JSON configuration file
    json_url_key = model_name + ".json"
    if not os.path.exists(json_path):
        logger.info(f"Downloading {json_url_key}...")
        url = VOICE_URLS.get(json_url_key)
        if not url or url in ["https://huggingface.co", "https://huggingface.co.json"]:
            error_msg = f"Invalid URL for {json_url_key}. Please set a real download link."
            logger.error(error_msg)
            raise Exception(error_msg)
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(json_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded {json_url_key} successfully")
        except Exception as e:
            logger.error(f"Failed to download {json_url_key}: {e}")
            raise

@app.route("/api/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    
    logger.info(f"Request received: text='{text[:50]}...', lang='{lang}'")
    
    if not text: 
        logger.warning("Empty text parameter")
        return "Missing text", 400
        
    if lang == "es": 
        model_name = "es_ES-sharvard-medium.onnx"
    elif lang == "fr": 
        model_name = "fr_FR-siwis-medium.onnx"
    else: 
        model_name = "en_US-lessac-medium.onnx"
    
    logger.info(f"Selected model: {model_name}")
    
    try:
        # Download the voice file if missing
        download_if_missing(model_name)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return f"Model download error: {str(e)}", 500
    
    model_path = os.path.join(VOICES_DIR, model_name)
    cmd = ["piper", "--model", model_path, "--output_raw"]
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run piper, capturing stderr for debugging
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=text.encode("utf-8"))
        
        if proc.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='replace')
            logger.error(f"Piper exited with code {proc.returncode}: {error_msg}")
            return f"Piper error (code {proc.returncode}): {error_msg}", 500
        
        logger.info(f"Successfully generated {len(stdout)} bytes of audio")
        return Response(stdout, mimetype="audio/wav")
        
    except FileNotFoundError:
        logger.error("Piper command not found. Is the binary installed and in PATH?")
        return "Engine Error: Piper binary not found. Please check Dockerfile.", 500
    except Exception as e:
        logger.exception("Unexpected error in TTS generation")
        return f"Engine Error: {str(e)}", 500

if __name__ == "__main__":
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False for production
