import whisper
import subprocess

def transcribe_audio(audio_path):
    model = whisper.load_model("base")

    # Convert audio safely for Streamlit Cloud
    command = [
        "ffmpeg",
        "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        "temp.wav",
        "-y"
    ]

    subprocess.run(command, check=True)

    result = model.transcribe("temp.mp3")
    return result["text"]