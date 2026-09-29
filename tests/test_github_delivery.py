import httpx
import pytest
from seo_engine.domain.models import FileChange
from seo_engine.github_delivery import GitHubDelivery


@pytest.mark.asyncio
async def test_github_delivery_creates_branch_commit_and_draft_pr() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"object": {"sha": "base-sha"}})
        if request.url.path.endswith("/git/refs"):
            return httpx.Response(201, json={"object": {"sha": "branch-sha"}})
        if request.url.path.endswith("/pulls"):
            return httpx.Response(
                201, json={"number": 7, "html_url": "https://github.com/o/r/pull/7"}
            )
        return httpx.Response(201, json={"content": {"sha": "file-sha"}})

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    delivery = GitHubDelivery("o", "r", "token", client)
    branch = await delivery.create_branch("seo/test", "base-sha")
    commit = await delivery.commit_files(
        branch, [FileChange(path="site/page.html", content="<h1>Page</h1>")], "SEO update"
    )
    pr = await delivery.open_draft_pr(branch, "main", "SEO update", "Evidence")
    await client.aclose()
    assert branch == "seo/test"
    assert commit == "file-sha"
    assert pr.number == 7


@pytest.mark.asyncio
async def test_github_delivery_redacts_auth_errors() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "token invalid"})

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    delivery = GitHubDelivery("o", "r", "secret-token", client)
    with pytest.raises(RuntimeError, match="GitHub request failed"):
        await delivery.create_branch("seo/test", "base-sha")
    await client.aclose()
