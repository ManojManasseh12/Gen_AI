from app.ai.prompt.falltry import fallback
import os

UPLOAD_DIR = "outputs/"
FILE_NAME = "output.txt"
os.makedirs(UPLOAD_DIR, exist_ok = True)

class FileOps:

    @staticmethod
    def file_write(prompt: str, response: str):

        destiny_path = os.path.join(UPLOAD_DIR, FILE_NAME)

        with open(destiny_path, "a", encoding = "utf-8") as file:
            file.write(f"Prompt: {prompt}\n")
            file.write(f"Output: {response}\n\n")

        return f"Output saved in {FILE_NAME}"

    @staticmethod
    async def prompt_extract(file):

        binary_content = await file.read()
        text_content = binary_content.decode("utf-8")

        prompts = []

        for line in text_content.splitlines():
            if line.startswith("prompt:"):
                prompt = line.removeprefix("prompt:").strip()
                prompts.append(prompt)

        result = []

        for prompt in prompts:
            response = await fallback(prompt)

            FileOps.file_write(prompt, str(response))

            result.append(
                {
                    "Prompt": prompt,
                    "Output": str(response)
                }
            )

        return result

file_ops = FileOps()
