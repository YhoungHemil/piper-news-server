FROM rhasspy/piper:latest

RUN mkdir -p /voices

# Download ONLY ONE medium-quality English voice model to protect Render's 512MB RAM limit
ADD https://huggingface.co /voices/en_US-lessac-medium.onnx
ADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.json

EXPOSE 5000

ENTRYPOINT ["/run.sh"]
# Only point the active configuration command boot-up sequence to the single loaded model
CMD ["--model", "/voices/en_US-lessac-medium.onnx", "--port", "5000"]
