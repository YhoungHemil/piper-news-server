FROM python:3.10-slim

# Install system dependencies: piper binary + audio library
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install the real piper binary
RUN wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz && \
    tar -xzf piper_amd64.tar.gz && \
    mv piper/piper /usr/local/bin/ && \
    chmod +x /usr/local/bin/piper && \
    rm -rf piper piper_amd64.tar.gz

# Install Python dependencies
RUN pip install --no-cache-dir flask requests

# Create app directory and copy files
WORKDIR /app
COPY . .

# Download models during build
RUN python models/download_models.py

# Create unprivileged user and set ownership
RUN useradd -u 10014 -m choreouser && \
    chown -R choreouser:choreouser /app /tmp/voices

USER 10014

EXPOSE 5000
CMD ["python", "/app/main.py"]
