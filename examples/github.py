import asyncio
from typing import List

from pydantic import BaseModel, HttpUrl

from src.client import AsyncBaseClient, BaseClient, Path, Query


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


class AsyncGitHub(AsyncBaseClient):
    @AsyncBaseClient.async_get("/users/{user}/repos")
    async def get_repos(self, user: Path, sort_by: Query) -> List[Repo]:
        pass


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[dict]
    usage: dict


if __name__ == "__main__":
    github = GitHub(
        base_url="https://api.github.com",
        default_headers={
            "Content-Type": "application/json",
        }
    )
    for repo in github.get_repos(user="octocat", sort_by="updated"):
        print(repo)

    async_client = AsyncGitHub(
        base_url="https://api.github.com",
        default_headers={
            "Content-Type": "application/json",
        }
    )
    for repo in asyncio.run(async_client.get_repos(user="octocat", sort_by="updated")):
        print(repo)
