FROM python:3.10-slim

# Install standard web server and speech utilities safely
RUN pip install --no-cache-dir flask piper-tts

# Create working app workspace
WORKDIR /app
COPY main.py /app/main.py

# REQUIRED BY CHOREO SECURITY: Assign unprivileged user context permissions
RUN useradd -u 10014 -m choreouser
RUN chown -R choreouser:choreouser /app
USER 10014

EXPOSE 5000

CMD ["python", "/app/main.py"]
