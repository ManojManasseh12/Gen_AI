import os
from dotenv import load_dotenv
from mistralai.client import Mistral
from groq import Groq

load_dotenv()

settings = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
}

Groq_client = Groq(api_key=settings["GROQ_API_KEY"]) if settings["GROQ_API_KEY"] else None
api_key = settings["MISTRAL_API_KEY"]
model = "ministral-small-2603"
Mistral_client = Mistral(api_key=api_key) if api_key else None


def Groq_llm(prompt: str):
    if Groq_client is None:
        raise ValueError("GROQ_API_KEY is not set")

    chat_completion = Groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="openai/gpt-oss-20b",
    )

    return chat_completion.choices[0].message.content


def Mistral_llm(prompt: str):
    if Mistral_client is None:
        raise ValueError("MISTRAL_API_KEY is not set")

    chat_response = Mistral_client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return chat_response.choices[0].message.content


def gemini_llm(prompt: str):
    if not settings["GEMINI_API_KEY"]:
        raise ValueError("GEMINI_API_KEY is not set")

    from google import genai

    client = genai.Client(api_key=settings["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
    )

    return response.text
