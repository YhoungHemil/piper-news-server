FROM python:3.10-slim

# Install system dependencies needed for runtime audio execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install the Python wrapper version of Piper TTS
RUN pip install --no-cache-dir flask piper-tts requests

# Create a data directory for your voices
RUN mkdir -p /voices

# 1. Download English Voice Model
ADD https://huggingface.co /voices/en_US-lessac-medium.onnx
ADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.json

# 2. Download Spanish Voice Model
ADD https://huggingface.co /voices/es_ES-sharvard-medium.onnx
ADD https://huggingface.co.json /voices/es_ES-sharvard-medium.onnx.json

# 3. Download French Voice Model
ADD https://huggingface.co /voices/fr_FR-siwis-medium.onnx
ADD https://huggingface.co.json /voices/fr_FR-siwis-medium.onnx.json

# Set full permissions for the downloaded models
RUN chmod -R 777 /voices

# Create a clean app working directory
WORKDIR /app

# Create the Python wrapper code inside the build container directly
RUN echo 'import os, subprocess\n\
from flask import Flask, request, Response\n\
app = Flask(__name__)\n\
@app.route("/api/tts", methods=["GET"])\n\
def tts():\n\
    text = request.args.get("text", "")\n\
    lang = request.args.get("lang", "en")\n\
    if not text: return "Missing text", 400\n\
    if lang == "es": model = "/voices/es_ES-sharvard-medium.onnx"\n\
    elif lang == "fr": model = "/voices/fr_FR-siwis-medium.onnx"\n\
    else: model = "/voices/en_US-lessac-medium.onnx"\n\
    cmd = ["piper", "--model", model, "--output_raw"]\n\
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)\n\
    stdout, _ = proc.communicate(input=text.encode("utf-8"))\n\
    return Response(stdout, mimetype="audio/wav")\n\
if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=5000)' > /app/main.py

# REQUIRED BY CHOREO SECURITY: Create unprivileged user
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app /voices
USER 10014

# Open the proxy routing network port
EXPOSE 5000

# Execute the application
CMD ["python", "/app/main.py"]
