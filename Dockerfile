FROM python:3.10-slim

# Install system utilities needed to fetch and unpack the binary archive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tar \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Install the basic Python web server framework
RUN pip install --no-cache-dir flask

# Download the standalone pre-compiled AMD64 Linux Linux Piper binary package archive directly from the source repository releases
RUN curl -L "https://github.com" -o /tmp/piper.tar.gz && \
    tar -xf /tmp/piper.tar.gz -C /usr/local/ && \
    rm /tmp/piper.tar.gz

# Create a permanent data directory for your voice models
RUN mkdir -p /voices

# Download English and Spanish Voice Models during compilation safely
RUN curl -L "https://huggingface.co" -o /voices/en_US-lessac-medium.onnx && \
    curl -L "https://huggingface.co.json" -o /voices/en_US-lessac-medium.onnx.json

RUN curl -L "https://huggingface.co" -o /voices/es_ES-sharvard-medium.onnx && \
    curl -L "https://huggingface.co.json" -o /voices/es_ES-sharvard-medium.onnx.json

# Grant complete access permissions to the voice assets directory
RUN chmod -R 777 /voices

# Copy the execution execution application script files
WORKDIR /app
COPY main.py /app/main.py

# REQUIRED BY CHOREO SECURITY: Create unprivileged user
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app /voices
USER 10014

EXPOSE 5000

CMD ["python", "/app/main.py"]
