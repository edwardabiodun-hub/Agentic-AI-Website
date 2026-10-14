from __future__ import annotations

import base64
import hashlib
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

    async def base_sha(self, base_branch: str) -> str:
        response = await self._request("GET", f"{self.repo_path}/git/ref/heads/{base_branch}")
        return response.json()["object"]["sha"]

    async def commit_files(self, branch_name: str, changes: list[FileChange], message: str) -> str:
        last_sha = ""
        for change in changes:
            current = await self._request("GET", f"{self.repo_path}/contents/{change.path}")
            current_payload = current.json()
            if change.original_sha256 and current_payload.get("content"):
                original = base64.b64decode(current_payload["content"])
                if hashlib.sha256(original).hexdigest() != change.original_sha256:
                    raise RuntimeError("GitHub file has changed since SEO proposal generation")
            response = await self._request(
                "PUT",
                f"{self.repo_path}/contents/{change.path}",
                json={
                    "message": message,
                    "content": base64.b64encode(change.content.encode()).decode(),
                    "branch": branch_name,
                    "sha": current_payload["sha"],
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
