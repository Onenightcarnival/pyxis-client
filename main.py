from typing import List

from pydantic import BaseModel, HttpUrl

from src.client import BaseClient, Body, Path, Query


class Owner(BaseModel):
    id: int
    avatar_url: HttpUrl
    organizations_url: HttpUrl


class Repo(BaseModel):
    id: int
    full_name: str
    owner: Owner


class GitHub(BaseClient):
    """
    A Python Client for the GitHub API.
    """

    @BaseClient.get(endpoint="/users/{user}/repos")
    def get_repos(self, user: Path, sort_by: Query) -> List[Repo]:
        """
        Get user's public repositories.
        """
        pass


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
    def chat_completions(self, **chat_completions_info: Body) -> ChatCompletionResponse:
        """
        Send a chat history and receive the assistant's response
        """


if __name__ == "__main__":
    client = GitHub(
        base_url="https://api.github.com",
        default_headers={
            "Content-Type": "application/json",
        }
    )
    repos = client.get_repos(user="octocat", sort_by="updated")
    for repo in repos:
        print(repo)

    lm_studio = LmStudio(
        base_url="http://localhost:1234",
        default_headers={
            "Content-Type": "application/json",
            "Authorization": get_dynamic_lm_studio_token
        }
    )
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
    full_chat = lm_studio.chat_completions(**messages)
    print(full_chat)
