FROM rhasspy/piper:latest

RUN mkdir -p /voices

# Download real-time English and Spanish Piper models directly into the container
ADD https://huggingface.co /voices/en_US-lessac-medium.onnx
ADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.json

ADD https://huggingface.co /voices/es_ES-sharvard-medium.onnx
ADD https://huggingface.co.json /voices/es_ES-sharvard-medium.onnx.json

# Expose the streaming network port
EXPOSE 5000

ENTRYPOINT ["/run.sh"]
CMD ["--model", "/voices/en_US-lessac-medium.onnx", "--model", "/voices/es_ES-sharvard-medium.onnx", "--port", "5000"]
