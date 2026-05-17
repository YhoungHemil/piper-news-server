FROM python:3.10-slim

# Install the real piper command-line binary and its audio dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install piper binary (Linux x86_64)
RUN wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz && \
    tar -xzf piper_amd64.tar.gz && \
    mv piper/piper /usr/local/bin/ && \
    rm -rf piper piper_amd64.tar.gz

# Install Python dependencies (piper-tts is still needed for Python bindings)
RUN pip install --no-cache-dir flask piper-tts requests

# Create voice directory
RUN mkdir -p /voices

# Set working directory
WORKDIR /app

# Copy your main.py
COPY main.py /app/main.py

# Create unprivileged user (as you originally had)
RUN useradd -u 10014 -m choreouser && \
    chown -R choreouser:choreouser /app /voices

USER 10014

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "/app/main.py"]
