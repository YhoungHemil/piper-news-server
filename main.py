import io
import os
import wave
import traceback
from flask import Flask, request, Response
# Import piper directly as a native code library for ultra-fast response times
from piper import PiperVoice

app = Flask(__name__)

VOICES_DIR = "/voices"

print("Pre-loading neural voice models into RAM for instant generation...", flush=True)

# Pre-initialize and cache the voice structures globally during container boot phase
models = {}
try:
    en_model_path = os.path.join(VOICES_DIR, "en_US-lessac-medium.onnx")
    if os.path.exists(en_model_path):
        models["en"] = PiperVoice.load(en_model_path)
        print("English voice model successfully cached.", flush=True)
        
    es_model_path = os.path.join(VOICES_DIR, "es_ES-sharvard-medium.onnx")
    if os.path.exists(es_model_path):
        models["es"] = PiperVoice.load(es_model_path)
        print("Spanish voice model successfully cached.", flush=True)
except Exception as init_err:
    print(f"Error during voice model pre-loading: {str(init_err)}", flush=True)


@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def tts(path):
    try:
        text = request.args.get("text", "")
        lang = request.args.get("lang", "en")
        
        if not text: 
            return "Server is live! Please add '?text=your+text' to generate speech.", 200
            
        # Match language selection to cached models
        voice = models.get(lang, models.get("en"))
        
        if not voice:
            return "Internal Error: Requested neural voice engine is not initialized.", 500

        # Create a raw memory buffer to compile the audio stream structure
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            # Dynamically extract and assign structural audio configuration markers
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(voice.config.sample_rate)
            
            # Synthesize text directly through RAM without launching system sub-processes
            voice.synthesize(text, wav_file)
            
        # Rewind memory pointer to start of raw wave stream object
        audio_buffer.seek(0)
        return Response(audio_buffer.read(), mimetype="audio/wav")

    except Exception as e:
        return f"CRASH LOG EXCEPTION:\n\n{traceback.format_exc()}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
