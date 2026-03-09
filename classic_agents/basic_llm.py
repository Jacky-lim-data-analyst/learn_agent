import os
from openai import OpenAI
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

class BasicAgentsLLM:
    """This class is used to call any service compatible with the OpenAI interface and uses streaming responses by default."""
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3) -> None:
        """
        Initialize the client. Prioritize passed parameters; if not provided, load from environment variables.
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")

        if not all([self.model, api_key, base_url]):
            raise ValueError("Model name, api key and base url are required.")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url, max_retries=max_retries)

    def think(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str | None:
        """
        Call the large language model to think and return its response.
        """
        print(f"🤖 Calling {self.model} model...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            print("LLM response successful")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)

            print()
            return "".join(collected_content)
        except Exception as exc:
            print(f"❌ Error occurred when calling LLM API: {exc}")
            return None
        
if __name__ == "__main__":
    try:
        llmClient = BasicAgentsLLM()

        exampleMessages = [
            {
                "role": "system", "content": "You are a helpful assistant in Python codes writing",
            },
            {
                "role": "user", "content": "Write a quicksort algorithm"
            }
        ]

        response = llmClient.think(exampleMessages)
        if response:
            print(response)
    except ValueError as e:
        print(e)
        