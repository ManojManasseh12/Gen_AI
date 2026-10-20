import random
import time
import asyncio
import os
from app.ai.prompt.model import models
from fastapi import HTTPException




async def retry_with_jitter(func, *args, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 8.0, **kwargs):
    for attempt in range(1, max_retries + 1):
        
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return await asyncio.to_thread(func, *args, **kwargs)

        except Exception as e:

            if attempt >= max_retries:

                print(f"  [x] Attempt {attempt}/{max_retries} failed: {e}")
                raise e
            
            backoff = min(max_delay, base_delay * (2 ** (attempt - 1)))
            sleep_time = random.uniform(0, backoff)
            
            print(f"  [!] Attempt {attempt}/{max_retries} failed: {e}")
            print(f"      Waiting {sleep_time:.2f}s (exponential backoff + jitter) before next retry...")
            await asyncio.sleep(sleep_time)


async def fallback(prompt: str):

    print("\n" + "=" * 50)
    print("Starting the LLM Inference")
    print("\n" + "=" * 50)

    fallback_models = models.fallback_chain()
        
    for model_name, func in fallback_models:
        print(f"Trying with {model_name} !!")

        try:
            response = await retry_with_jitter(func, prompt)
            return response

        except Exception as e:

            print(f"[Fallback Triggered] {model_name} failed all retries: {e}")
            print(f"                      Switching to the next backup model in chain...")


    raise HTTPException(
        status_code=502,
        detail="All LLM models in the fallback pipeline failed. Please check credentials or network."
    )
