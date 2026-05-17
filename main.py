import os
import subprocess
from flask import Flask, request, Response

app = Flask(__name__)

VOICES_DIR = "/voices"

@app.route("/api/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    
    if not text: 
        return "Missing text parameter", 400
        
    if lang == "es": 
        model_name = "es_ES-sharvard-medium.onnx"
    else: 
        model_name = "en_US-lessac-medium.onnx"
        
    model_path = os.path.join(VOICES_DIR, model_name)
    
    # Run the native system executable compiled binary
    cmd = ["/usr/local/bin/piper", "--model", model_path, "--output_raw"]
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        stdout, _ = proc.communicate(input=text.encode("utf-8"))
        return Response(stdout, mimetype="audio/wav")
    except Exception as e:
        return f"System Audio Engine Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
