import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from groq import Groq
from app.core.config import settings

# Initialize the Groq client
client = Groq(api_key=settings.GROQ_API_KEY)


def audio_text(filename: str):
    """Transcribes an audio file using Groq Whisper."""
    if not os.path.exists(filename):
        print(f"Audio file not found: {filename}")
        return None

    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            prompt="Specify context or spelling",
            language="en",
            temperature=0.0
        )
        print("\n=== Transcription Result ===")
        print(transcription.text)
        return transcription.text


if __name__ == "__main__":
    sample_file = os.path.join(PROJECT_ROOT, "sample-speech-1m.mp3")
    if os.path.exists(sample_file):
        print(f"Testing transcription on: {sample_file}")
        audio_text(sample_file)
    else:
        print(f"Audio file not found at {sample_file}")
