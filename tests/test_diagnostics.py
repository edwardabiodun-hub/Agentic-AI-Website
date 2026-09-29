from datetime import UTC, datetime, timedelta

from seo_engine.diagnostics import (
    DiagnosticConfig,
    EvidenceSet,
    find_content_gaps,
    find_friction,
    find_striking_distance,
    rank_diagnostics,
)
from seo_engine.domain.models import NormalizedObservation, Strategy


def observation(
    source: str, page: str, metrics: dict[str, float], days_ago: int = 0, query: str = ""
) -> NormalizedObservation:
    return NormalizedObservation(
        source=source,
        observed_at=datetime.now(UTC) - timedelta(days=days_ago),
        dimensions={"page": page, "query": query},
        metrics=metrics,
        evidence_ref=f"{source}:{page}:{days_ago}",
    )


def test_striking_distance_requires_position_and_impressions() -> None:
    evidence = EvidenceSet(
        observations=[
            observation(
                "gsc",
                "/service",
                {"position": 9.5, "impressions": 500, "clicks": 20},
                query="seo service",
            ),
            observation(
                "gsc", "/other", {"position": 3, "impressions": 500, "clicks": 20}, query="other"
            ),
        ]
    )
    results = find_striking_distance(evidence, DiagnosticConfig())
    assert len(results) == 1
    assert results[0].target_query == "seo service"


def test_content_gap_uses_search_volume_without_target_page() -> None:
    evidence = EvidenceSet(
        observations=[
            observation("dataforseo", "", {"search_volume": 1000, "rank": 0}, query="missing topic")
        ]
    )
    results = find_content_gaps(evidence, DiagnosticConfig(min_search_volume=100))
    assert results[0].target_query == "missing topic"


def test_friction_joins_traffic_and_rage_clicks() -> None:
    evidence = EvidenceSet(
        observations=[
            observation("ga4", "/service", {"sessions": 100, "engagement_rate": 0.3}),
            observation("clarity", "/service", {"rage_click_count": 8}),
        ]
    )
    results = find_friction(evidence, DiagnosticConfig(min_sessions=50))
    assert results[0].target_url == "/service"


def test_rank_diagnostics_prefers_strategy_aligned_opportunities() -> None:
    evidence = EvidenceSet(
        observations=[
            observation("gsc", "/service", {"position": 9, "impressions": 500}, query="service")
        ]
    )
    diagnostic = find_striking_distance(evidence, DiagnosticConfig())[0]
    ranked = rank_diagnostics([diagnostic], Strategy(priority_offerings=["service"]))
    assert ranked[0].strategy_alignment == "aligned"
