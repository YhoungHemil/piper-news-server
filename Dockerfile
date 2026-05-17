FROM rhasspy/piper:latest
   RUN mkdir -p /voices
   # Securely fetch optimized, real-time medium quality voice profiles into Koyeb during buildADD https://huggingface.co /voices/en_US-lessac-medium.onnxADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.jsonADD https://huggingface.co /voices/es_ES-sharvard-medium.onnxADD https://huggingface.co.json /voices/es_ES-sharvard-medium.onnx.json
   EXPOSE 5000
   ENTRYPOINT ["/run.sh"]CMD ["--model", "/voices/en_US-lessac-medium.onnx", "--model", "/voices/es_ES-sharvard-medium.onnx", "--port", "5000"]
