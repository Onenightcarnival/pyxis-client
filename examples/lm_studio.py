import asyncio
from typing import List

from pydantic import BaseModel

from src import AsyncClient, BaseClient, BodyMap


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[dict]
    usage: dict


def get_dynamic_lm_studio_token():
    return "Bearer lm-studio"


class LmStudio(BaseClient):
    """
    A Python Client for the LmStudio API.
    """

    @BaseClient.post(endpoint="/v1/chat/completions")
    def chat_completions(self, chat_completions_info: BodyMap) -> ChatCompletionResponse:
        """
        Send a chat history and receive the assistant's response
        """
        pass


class AsyncLmStudio(AsyncClient):
    @AsyncClient.async_post(endpoint="/v1/chat/completions")
    async def chat_completions(self, chat_completions_info: BodyMap) -> ChatCompletionResponse:
        pass


if __name__ == "__main__":
    messages = {
        "model": "qwen2.5-coder-1.5b-instruct",
        "messages": [
            {"role": "system", "content": "Always answer in rhymes. Today is Thursday"},
            {"role": "user", "content": "What day is it today?"}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    lm_studio = LmStudio(
        base_url="http://localhost:1234",
        default_headers={
            "Content-Type": "application/json",
            "Authorization": get_dynamic_lm_studio_token
        }
    )
    print(lm_studio.chat_completions(BodyMap(messages)))

    async_lm_studio = AsyncLmStudio(
        base_url="http://localhost:1234",
        default_headers={
            "Content-Type": "application/json",
            "Authorization": get_dynamic_lm_studio_token
        }
    )
    print(asyncio.run(async_lm_studio.chat_completions(BodyMap(messages))))
