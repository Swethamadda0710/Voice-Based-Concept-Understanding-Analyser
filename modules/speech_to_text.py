import whisper
import subprocess
import os


# Load the model only once
model = whisper.load_model("base")


def transcribe_audio(audio_path):
    temp_audio = "temp.wav"

    # Convert audio to WAV format
    command = [
        "ffmpeg",
        "-y",
        "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        temp_audio
    ]

    subprocess.run(command, check=True)

    # Transcribe the converted audio
    result = model.transcribe(temp_audio)

    # Remove temporary file
    if os.path.exists(temp_audio):
        os.remove(temp_audio)

    return result["text"]