import asyncio
import random
from fastapi import HTTPException
from app.ai.model import models


def is_retryable(e: Exception) -> bool:
    """Retry only on temporary errors: rate limits, timeouts, server errors, network drops."""
    status = getattr(e, "status_code", None) or getattr(e, "code", None)
    if not isinstance(status, int):
        return True                          # no HTTP status -> likely network/timeout
    return status in (408, 429) or status >= 500


async def fallback_stream(
    prompt: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 8.0,
):
    print("\n" + "=" * 50)
    print("Starting the LLM Inference")
    print("=" * 50)

    for model_name, func in models.stream_chain():
        print(f"Trying with {model_name} !!")

        for attempt in range(1, max_retries + 1):
            started = False
            try:
                async for piece in func(prompt):
                    started = True
                    yield piece
                return                       # finished cleanly

            except Exception as e:
                # Text was already sent to the client: a retry would restart the answer
                if started:
                    print(f"  [x] {model_name} failed mid-stream: {e}")
                    raise

                print(f"  [!] {model_name} attempt {attempt}/{max_retries} failed: {e}")

                # Permanent error (bad key, bad model name) or out of retries -> next model
                if not is_retryable(e) or attempt >= max_retries:
                    print(f"[Fallback Triggered] {model_name} gave up. Switching to next model...")
                    break

                backoff = min(max_delay, base_delay * (2 ** (attempt - 1)))
                sleep_time = random.uniform(0, backoff)
                print(f"      Waiting {sleep_time:.2f}s (exponential backoff + jitter)...")
                await asyncio.sleep(sleep_time)

    raise HTTPException(
        status_code=502,
        detail="All LLM models in the fallback pipeline failed. Please check credentials or network.",
    )


async def fallback(prompt: str) -> str:
    """Non-streaming version: collects the whole answer. Used by /llm and /file."""
    return "".join([piece async for piece in fallback_stream(prompt)])
