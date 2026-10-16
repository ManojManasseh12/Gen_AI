import os
import sys
import json
from typing import Optional, Union, BinaryIO
import sounddevice as sd
import soundfile as sf
import numpy as np

# Ensure project root is in sys.path so 'app' can always be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from groq import Groq
from app.core.config import Settings

# Initialize the Groq client
client = Groq(api_key=Settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"))


def record_live_audio(duration: int = 5, filename: Optional[str] = None) -> str:
    """
    Records live audio from your microphone for the specified duration (seconds)
    and saves it to a WAV file.
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "live_audio.wav")

    sample_rate = 16000  # 16kHz is optimal for Whisper
    print(f"\n🎙️  [RECORDING] Listening from microphone for {duration} seconds... Speak now!")
    
    # Record from microphone
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()  # Wait until the recording finishes
    
    print("⏹️  [RECORDING STOPPED] Saving and transcribing with Groq Whisper...\n")
    sf.write(filename, audio_data, sample_rate, subtype="PCM_16")
    return filename


def transcribe_audio(
    file_or_path: Union[str, BinaryIO, tuple],
    model: str = "whisper-large-v3-turbo",
    prompt: Optional[str] = None,
    response_format: str = "verbose_json",
    language: str = "en",
    temperature: float = 0.0,
    timestamp_granularities: Optional[list] = None,
):
    """
    Transcribes an audio file or stream using Groq Whisper API.
    """
    if timestamp_granularities is None and response_format == "verbose_json":
        timestamp_granularities = ["word", "segment"]

    params = {
        "model": model,
        "response_format": response_format,
        "language": language,
        "temperature": temperature,
    }
    if prompt:
        params["prompt"] = prompt
    if timestamp_granularities and response_format == "verbose_json":
        params["timestamp_granularities"] = timestamp_granularities

    if isinstance(file_or_path, str):
        if not os.path.exists(file_or_path):
            raise FileNotFoundError(f"Audio file not found: {file_or_path}")
        with open(file_or_path, "rb") as audio_file:
            params["file"] = audio_file
            return client.audio.transcriptions.create(**params)
    elif isinstance(file_or_path, tuple):
        params["file"] = file_or_path
        return client.audio.transcriptions.create(**params)
    elif hasattr(file_or_path, "read"):
        filename = getattr(file_or_path, "name", "audio.wav")
        params["file"] = (filename, file_or_path.read())
        return client.audio.transcriptions.create(**params)
    else:
        params["file"] = file_or_path
        return client.audio.transcriptions.create(**params)


if __name__ == "__main__":
    # 1. Record live audio from your microphone for 5 seconds
    # (Feel free to change duration=5 to whatever seconds you like)
    filename = record_live_audio(duration=5)

    # 2. Open the audio file and transcribe with Groq Whisper
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,  # Required audio file
            model="whisper-large-v3-turbo",  # Required model to use for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="verbose_json",  # Optional
            timestamp_granularities=["word", "segment"],  # Optional
            language="en",  # Optional
            temperature=0.0  # Optional
        )

        # Print the transcription text
        print("=== Transcription Text ===")
        print(transcription.text)

        # Print the entire transcription object (including timestamps)
        print("\n=== Full Details (JSON) ===")
        print(json.dumps(transcription, indent=2, default=str))