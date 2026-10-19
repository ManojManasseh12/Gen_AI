import os
import sys

# Ensure project root is in sys.path so 'app' can always be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from groq import Groq
from app.core.config import settings

# Initialize the Groq client
client = Groq(api_key=settings.GROQ_API_KEY)


def audio_text(filename: str):
    """
    Transcribes an audio file using Groq Whisper.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Audio file not found: {filename}")

    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=file,  # Required audio file
            model="whisper-large-v3-turbo",  # Required model to use for transcription
            prompt="Specify context or spelling",  # Optional
            language="en",  # Optional
            temperature=0.0,  # Optimal for Whisper accuracy
        )

        # Print and return transcription text
        print(transcription.text)
        return transcription.text


# Helper function for FastAPI routes
def transcribe_audio(file_or_path, **kwargs):
    if isinstance(file_or_path, tuple):
        return client.audio.transcriptions.create(
            file=file_or_path,
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
        )
    elif hasattr(file_or_path, "read"):
        name = getattr(file_or_path, "name", "audio.wav")
        return client.audio.transcriptions.create(
            file=(name, file_or_path.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
        )
    else:
        return audio_text(str(file_or_path))


if __name__ == "__main__":
    # Test with sample audio file if available
    sample_file = os.path.join(PROJECT_ROOT, "sample-speech-1m.mp3")
    if os.path.exists(sample_file):
        print(f"Transcribing {sample_file}...\n")
        audio_text(sample_file)
    else:
        print("Please provide an audio file path to audio_text(filename)")