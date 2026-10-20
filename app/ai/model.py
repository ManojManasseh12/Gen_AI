import asyncio
from google import genai
from groq import Groq
from mistralai.client import Mistral
from app.core.config import settings
from app.ai.prompt.gemini_prompt import SYSTEM_PROMPT

_DONE = object()


async def _iterate(sync_iterable):
    """Consume a blocking iterator in a worker thread so the event loop stays free."""
    it = iter(sync_iterable)
    while True:
        item = await asyncio.to_thread(next, it, _DONE)
        if item is _DONE:
            return
        yield item


class Models:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

        # Clients are optional: a missing key just removes that model from the chain
        self.gemini_client = (
            genai.Client(api_key=settings.GEMINI_API_KEY)
            if settings.GEMINI_API_KEY else None
        )
        self.groq_client = (
            Groq(api_key=settings.GROQ_API_KEY)
            if settings.GROQ_API_KEY else None
        )
        self.mistral_client = (
            Mistral(api_key=settings.MISTRAL_API_KEY)
            if settings.MISTRAL_API_KEY else None
        )

    def _messages(self, prompt: str):
        messages = [{"role": "user", "content": prompt}]
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        return messages

    async def gemini_stream(self, prompt: str):
        response = await asyncio.to_thread(
            self.gemini_client.interactions.create,
            model="gemini-3.5-flash-lite",
            system_instruction=self.system_prompt,
            input=prompt,
            stream=True,
        )
        async for event in _iterate(response):
            if (
                getattr(event, "event_type", None) == "step.delta"
                and getattr(event.delta, "type", None) == "text"
            ):
                yield event.delta.text

    async def groq_stream(self, prompt: str):
        completion = await asyncio.to_thread(
            self.groq_client.chat.completions.create,
            messages=self._messages(prompt),
            model="openai/gpt-oss-20b",
            stream=True,
        )
        async for chunk in _iterate(completion):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def mistral_stream(self, prompt: str):
        response = await asyncio.to_thread(
            self.mistral_client.chat.stream,
            model="ministral-small-2603",
            messages=self._messages(prompt),
        )
        async for event in _iterate(response):
            if event.data.choices:
                content = event.data.choices[0].delta.content
                if content:
                    yield content

    def stream_chain(self):
        chain = []
        if self.gemini_client:
            chain.append(("Google Gemini", self.gemini_stream))
        if self.groq_client:
            chain.append(("Groq", self.groq_stream))
        if self.mistral_client:
            chain.append(("Mistral", self.mistral_stream))
        return chain


models = Models()
