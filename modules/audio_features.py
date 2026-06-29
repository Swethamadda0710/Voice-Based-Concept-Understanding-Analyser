import librosa
import numpy as np


def extract_audio_features(audio_path, transcript):
    """
    Extract basic audio features.
    """

    y, sr = librosa.load(audio_path)

    duration = librosa.get_duration(y=y, sr=sr)

    words = len(transcript.split())

    speech_rate = (words / duration) * 60 if duration > 0 else 0

    rms = librosa.feature.rms(y=y)[0]

    avg_energy = float(np.mean(rms))

    return {
        "duration": round(duration, 2),
        "speech_rate": round(speech_rate, 2),
        "energy": round(avg_energy, 4)
    }