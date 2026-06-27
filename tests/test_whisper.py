from modules.speech_to_text import transcribe_audio

audio_file = "audio/sample.mp3"

text = transcribe_audio(audio_file)

print(text)