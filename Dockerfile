FROM python:3.10-slim

# Install the Python wrapper version of Piper TTS and requests directly
RUN pip install --no-cache-dir flask piper-tts requests

# Create a data directory for your voices
RUN mkdir -p /voices

# Create a clean app working directory
WORKDIR /app

# Copy the main.py file from your repository root into the container image
COPY main.py /app/main.py

# REQUIRED BY CHOREO SECURITY: Create unprivileged user and assign directory permissions
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app /voices
USER 10014

# Open the proxy routing network port
EXPOSE 5000

# Execute the application
CMD ["python", "/app/main.py"]
