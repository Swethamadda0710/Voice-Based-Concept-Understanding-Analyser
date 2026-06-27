import whisper

# Load Whisper model once
model = whisper.load_model("base")


def transcribe_audio(audio_path):
    """
    Convert speech in an audio file to text.
    """
    result = model.transcribe(audio_path)
    return result["text"]