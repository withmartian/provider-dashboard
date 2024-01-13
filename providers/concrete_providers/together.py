from providers.abstract_providers.openai_provider import OpenaiProvider
import os
from typing import Callable
from dotenv import load_dotenv

load_dotenv()


class Together(OpenaiProvider):
    NAME = "Together"
    API_KEY = os.environ["TOGETHER_API_KEY"]
    HTTP_URL = "https://api.together.xyz/inference"
    OPENAI_BASE_URL = "https://api.together.xyz/v1"
    SUPPORTED_MODELS = {
        "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "llama2-70b-chat": "togethercomputer/llama2-70b-chat",
    }

    def together_get_completion_tokens(response):
        return response["output"]["usage"]["completion_tokens"]

    def call_http(
        self,
        llm_name: str,
        prompt: str,
        max_tokens: int,
        url: str = HTTP_URL,
        get_completion_tokens: Callable = together_get_completion_tokens,
    ) -> float:
        return super().call_http(
            llm_name,
            prompt,
            max_tokens,
            url=url,
            get_completion_tokens=get_completion_tokens,
        )
