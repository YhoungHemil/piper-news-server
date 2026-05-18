FROM python:3.10-slim

# --- System Dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# --- Install Piper Binary ---
RUN wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz && \
    tar -xzf piper_amd64.tar.gz && \
    mv piper/piper /usr/local/bin/ && \
    chmod +x /usr/local/bin/piper && \
    rm -rf piper piper_amd64.tar.gz

# --- Install Python Dependencies (Only 'flask' and 'requests' needed) ---
RUN pip install --no-cache-dir flask requests

# --- Project Setup ---
WORKDIR /app
COPY . .

# >>> KEY CHANGE 1: Download models during image build <<<
# The 'download_models.py' script runs here, embedding models into the image.
RUN python models/download_models.py

# --- User Permissions ---
RUN useradd -u 10014 -m choreouser && \
    chown -R choreouser:choreouser /app

USER 10014

EXPOSE 5000
# >>> KEY CHANGE 2: Startup command only starts the app (no downloads) <<<
# The 'CMD' now only starts the Flask server.
CMD ["python", "/app/main.py"]
