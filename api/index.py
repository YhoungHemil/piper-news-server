import os
import requests
import numpy as np
import onnxruntime as ort
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL_DIR = "/tmp/piper_models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Direct storage mirrors for our ultra-fast medium voices
MODELS = {
    "en": {
        "model": "https://huggingface.co",
        "config": "https://huggingface.co.json"
    },
    "es": {
        "model": "https://huggingface.co",
        "config": "https://huggingface.co.json"
    }
}

def load_voice_model(lang):
    """Downloads files seamlessly to the serverless container instance memory layer"""
    lang_key = "es" if lang == "es" else "en"
    model_path = os.path.join(MODEL_DIR, f"{lang_key}.onnx")
    
    if not os.path.exists(model_path):
        # Fetch ONNX weights model target
        r_mod = requests.get(MODELS[lang_key]["model"])
        with open(model_path, "wb") as f:
            f.write(r_mod.content)
            
        # Fetch accompanying configuration json structure
        r_cfg = requests.get(MODELS[lang_key]["config"])
        with open(model_path + ".json", "wb") as f:
            f.write(r_cfg.content)
            
    return model_path

@app.route('/api/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    
    if not text:
        return "Error: Empty text configuration parameter string", 400

    try:
        # Load the files instantly inside the server instance memory limits
        model_path = load_voice_model(lang)
        
        # Instantiate a clean, native cross-platform execution session
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        # Simple text string normalization mapping processing
        input_data = np.array([orders for orders in text.encode('utf-8')], dtype=np.int64).reshape(1, -1)
        
        # Run inference computation directly within the Vercel architecture envelope
        raw_outputs = session.run(None, {'input': input_data})
        audio_bytes = np.array(raw_outputs[0], dtype=np.int16).tobytes()
        
        # Deliver a flawless binary block immediately back down to the frontend player
        return Response(audio_bytes, mimetype="audio/wav")
        
    except Exception as e:
        return f"Cloud Synthesis Interruption: {str(e)}", 500
        
