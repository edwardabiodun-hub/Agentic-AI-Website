from pathlib import Path


def test_package_cli_and_demo_site_contract() -> None:
    import seo_engine
    from seo_engine.cli import build_cli

    assert seo_engine.__version__
    assert build_cli().info.name == "seo-engine"

    page = Path("site/pages/example-service.html")
    assert page.exists()
    html = page.read_text(encoding="utf-8")
    assert "<h1>" in html
    assert 'rel="canonical"' in html
