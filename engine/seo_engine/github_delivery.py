from __future__ import annotations

import base64
from dataclasses import dataclass

import httpx

from seo_engine.domain.models import FileChange


@dataclass
class PullRequestRecord:
    number: int
    url: str


class GitHubDelivery:
    def __init__(
        self, owner: str, repository: str, token: str, client: httpx.AsyncClient | None = None
    ) -> None:
        self.owner = owner
        self.repository = repository
        self.token = token
        self.client = client or httpx.AsyncClient(base_url="https://api.github.com")

    @property
    def repo_path(self) -> str:
        return f"/repos/{self.owner}/{self.repository}"

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = await self.client.request(
            method,
            path,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            **kwargs,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub request failed: {response.status_code}")
        return response

    async def create_branch(self, branch_name: str, base_sha: str) -> str:
        response = await self._request(
            "POST",
            f"{self.repo_path}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
        )
        return branch_name if response.status_code == 201 else branch_name

    async def commit_files(self, branch_name: str, changes: list[FileChange], message: str) -> str:
        last_sha = ""
        for change in changes:
            response = await self._request(
                "PUT",
                f"{self.repo_path}/contents/{change.path}",
                json={
                    "message": message,
                    "content": base64.b64encode(change.content.encode()).decode(),
                    "branch": branch_name,
                },
            )
            last_sha = response.json().get("content", {}).get("sha", last_sha)
        return last_sha

    async def open_draft_pr(
        self, branch_name: str, base_branch: str, title: str, body: str
    ) -> PullRequestRecord:
        response = await self._request(
            "POST",
            f"{self.repo_path}/pulls",
            json={
                "title": title,
                "body": body,
                "head": branch_name,
                "base": base_branch,
                "draft": True,
            },
        )
        payload = response.json()
        return PullRequestRecord(number=payload["number"], url=payload["html_url"])

    async def update_pr(self, pr_number: int, body_append: str) -> None:
        await self._request(
            "PATCH", f"{self.repo_path}/issues/{pr_number}", json={"body": body_append}
        )
