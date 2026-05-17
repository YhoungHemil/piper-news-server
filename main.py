import os
import subprocess
import traceback
from flask import Flask, request, Response

app = Flask(__name__)

# Directory where Choreo allows the unprivileged user to read/write files
VOICES_DIR = "/tmp/voices"
os.makedirs(VOICES_DIR, exist_ok=True)

@app.route("/api/tts", methods=["GET"])
def tts():
    try:
        text = request.args.get("text", "")
        lang = request.args.get("lang", "en")
        
        if not text: 
            return "Missing text parameter", 400
            
        # Define download URLs for the models
        if lang == "es":
            model_name = "es_ES-sharvard-medium.onnx"
            url = "https://huggingface.co"
        else:
            model_name = "en_US-lessac-medium.onnx"
            url = "https://huggingface.co"
            
        model_path = os.path.join(VOICES_DIR, model_name)
        json_path = model_path + ".json"
        
        # Download models safely using Python's built-in tools if they aren't in /tmp yet
        import urllib.request
        if not os.path.exists(model_path):
            urllib.request.urlretrieve(url, model_path)
        if not os.path.exists(json_path):
            urllib.request.urlretrieve(url + ".json", json_path)

        # Call the system module explicitly via the python environment path
        cmd = ["python3", "-m", "piper", "--model", model_path, "--output_raw"]
        
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=text.encode("utf-8"))
        
        if proc.returncode != 0:
            return f"Piper Binary Process Error: {stderr.decode('utf-8', errors='ignore')}", 500
            
        return Response(stdout, mimetype="audio/wav")

    except Exception as e:
        # Professional diagnostic catch: Prints the exact code failure trace directly to the web page
        error_message = traceback.format_exc()
        return f"CRASH LOG EXCEPTION:\n\n{error_message}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
