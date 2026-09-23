from modules.speech_to_text import transcribe_audio
from modules.audio_features import extract_audio_features

audio = "audio/sample.mp3"

text = transcribe_audio(audio)

features = extract_audio_features(audio, text)

print("Transcript:")
print(text)

print("\nAudio Features:")
print(features)