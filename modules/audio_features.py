import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt


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


def plot_waveform(audio_path):
    """
    Generate and save waveform image.
    """

    y, sr = librosa.load(audio_path)

    plt.figure(figsize=(10, 3))

    librosa.display.waveshow(
        y,
        sr=sr
    )

    plt.title("Audio Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")

    # Create folder automatically
    os.makedirs("reports/waveforms", exist_ok=True)

    output_path = "reports/waveforms/waveform.png"

    plt.savefig(
        output_path,
        bbox_inches="tight"
    )

    plt.close()

    return output_path