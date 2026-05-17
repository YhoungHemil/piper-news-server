FROM rhasspy/piper:latest

# Create a clean data directory inside the container
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

# Ensure the container system has full read/write permissions to the voice assets
RUN chmod -R 777 /voices

# REQUIRED BY CHOREO SECURITY: Create an unprivileged user ID between 10000-20000 and switch to it
RUN (useradd -u 10014 -m choreouser || adduser -D -u 10014 choreouser)
USER 10014

# Open the network port required by Choreo's proxy routing
EXPOSE 5000

# Fire up the built-in rhasspy/piper web server, loading all 3 models into memory simultaneously
ENTRYPOINT ["/run.sh"]
CMD [ \
  "--model", "/voices/en_US-lessac-medium.onnx", \
  "--model", "/voices/es_ES-sharvard-medium.onnx", \
  "--model", "/voices/fr_FR-siwis-medium.onnx", \
  "--port", "5000" \
]
