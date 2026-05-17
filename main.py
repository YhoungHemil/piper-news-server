import os
import subprocess
import traceback
from flask import Flask, request, Response

app = Flask(__name__)

VOICES_DIR = "/voices"

# Catch-all routing structure to prevent Choreo path-forwarding conflicts
@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def tts(path):
    try:
        text = request.args.get("text", "")
        lang = request.args.get("lang", "en")
        
        if not text: 
            return "Server is live! Please add '?text=your+text' to generate speech.", 200
            
        if lang == "es":
            model_name = "es_ES-sharvard-medium.onnx"
        else:
            model_name = "en_US-lessac-medium.onnx"
            
        model_path = os.path.join(VOICES_DIR, model_name)
        
        if not os.path.exists(model_path):
            return f"Internal Error: Voice asset file missing at {model_path}", 500

        # Run piper speech generation through the python environment pipeline
        cmd = ["python3", "-m", "piper", "--model", model_path, "--output_raw"]
        
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=text.encode("utf-8"))
        
        if proc.returncode != 0:
            return f"Piper Engine Execution Error: {stderr.decode('utf-8', errors='ignore')}", 500
            
        return Response(stdout, mimetype="audio/wav")

    except Exception as e:
        return f"CRASH LOG EXCEPTION:\n\n{traceback.format_exc()}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
