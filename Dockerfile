# Stage 1: Borrow the pre-compiled binary layers from Rhasspy
FROM rhasspy/piper:latest AS piper_source

# Stage 2: Build our actual web container
FROM python:3.10-slim

# Copy the exact system binaries and missing libraries into the system paths
COPY --from=piper_source /piper/piper /usr/local/bin/piper
COPY --from=piper_source /piper/lib* /usr/local/lib/

# Refresh the system's dynamic linker cache so it detects the new libraries
RUN ldconfig

# Install only basic python web tools (No compilation needed)
RUN pip install --no-cache-dir flask

# Create a data directory for your voices
RUN mkdir -p /voices

# Download your voice models safely during build time
ADD https://huggingface.co /voices/en_US-lessac-medium.onnx
ADD https://huggingface.co.json /voices/en_US-lessac-medium.onnx.json
ADD https://huggingface.co /voices/es_ES-sharvard-medium.onnx
ADD https://huggingface.co.json /voices/es_ES-sharvard-medium.onnx.json

# Set full read/write permissions
RUN chmod -R 777 /voices

# Copy your backend engine
WORKDIR /app
COPY main.py /app/main.py

# REQUIRED BY CHOREO SECURITY: Switch to an unprivileged user ID
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app /voices
USER 10014

EXPOSE 5000

CMD ["python", "/app/main.py"]
