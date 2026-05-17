FROM python:3.10-slim

# Install flask and piper text-to-speech bindings
RUN pip install --no-cache-dir flask piper-tts

# Create a permanent internal directory for your voice models
RUN mkdir -p /voices

# Download voice assets safely during build-time (safe from runtime firewalls)
ADD https://huggingface.co /voices/en_US-lessac-medium.onnx
ADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.json
ADD https://huggingface.co /voices/es_ES-sharvard-medium.onnx
ADD https://huggingface.co.json /voices/es_ES-sharvard-medium.onnx.json

# Set up the execution application workspace
WORKDIR /app
COPY main.py /app/main.py

# REQUIRED BY CHOREO SECURITY: Create unprivileged user and fix directory access
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app /voices
USER 10014

EXPOSE 5000

CMD ["python", "/app/main.py"]
