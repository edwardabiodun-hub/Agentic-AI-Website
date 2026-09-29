from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from seo_engine.domain.models import Diagnostic, EvidenceItem, Opportunity, Strategy


@dataclass
class DiagnosticConfig:
    min_impressions: float = 100
    min_search_volume: float = 100
    min_sessions: float = 10
    min_decay_ratio: float = 0.2


@dataclass
class EvidenceSet:
    observations: list = field(default_factory=list)


def _evidence(item, summary: str) -> EvidenceItem:
    return EvidenceItem(
        source=item.source,
        reference=item.evidence_ref,
        summary=summary,
        data={"dimensions": item.dimensions, "metrics": item.metrics},
    )


def find_striking_distance(evidence: EvidenceSet, config: DiagnosticConfig) -> list[Diagnostic]:
    results = []
    for item in evidence.observations:
        position = item.metrics.get("position")
        impressions = item.metrics.get("impressions") or 0
        if (
            item.source == "gsc"
            and position is not None
            and 8 <= position <= 20
            and impressions >= config.min_impressions
        ):
            results.append(
                Diagnostic(
                    kind="striking_distance",
                    target_url=item.dimensions.get("page"),
                    target_query=item.dimensions.get("query"),
                    summary="Page is ranking near page one with meaningful impressions.",
                    evidence=[_evidence(item, "GSC position and impression threshold met")],
                    confidence=0.9,
                    score=impressions / max(position, 1),
                )
            )
    return results


def find_content_gaps(evidence: EvidenceSet, config: DiagnosticConfig) -> list[Diagnostic]:
    results = []
    for item in evidence.observations:
        volume = item.metrics.get("search_volume") or 0
        if (
            item.source == "dataforseo"
            and volume >= config.min_search_volume
            and not item.dimensions.get("url")
        ):
            results.append(
                Diagnostic(
                    kind="content_gap",
                    target_query=item.dimensions.get("query") or item.dimensions.get("keyword"),
                    summary="Demand exists without a mapped target page.",
                    evidence=[_evidence(item, "SERP demand has no target URL")],
                    confidence=0.8,
                    score=volume,
                )
            )
    return results


def find_friction(evidence: EvidenceSet, config: DiagnosticConfig) -> list[Diagnostic]:
    traffic = {}
    rage = {}
    for item in evidence.observations:
        page = item.dimensions.get("page") or item.dimensions.get("url")
        if item.source == "ga4":
            traffic[page] = item
        if item.source == "clarity":
            rage[page] = item
    results = []
    for page, ga4_item in traffic.items():
        clarity_item = rage.get(page)
        if clarity_item is None:
            continue
        sessions = ga4_item.metrics.get("sessions") or 0
        rage_count = clarity_item.metrics.get("rage_click_count") or 0
        if sessions >= config.min_sessions and rage_count > 0:
            results.append(
                Diagnostic(
                    kind="friction",
                    target_url=page,
                    summary="High-traffic page has user-friction signals.",
                    evidence=[
                        _evidence(ga4_item, "GA4 traffic threshold met"),
                        _evidence(clarity_item, "Clarity rage clicks detected"),
                    ],
                    confidence=0.85,
                    score=sessions * rage_count,
                    risk="medium",
                )
            )
    return results


def find_decay(evidence: EvidenceSet, config: DiagnosticConfig) -> list[Diagnostic]:
    grouped = defaultdict(list)
    for item in evidence.observations:
        if item.source == "gsc":
            grouped[(item.dimensions.get("page"), item.dimensions.get("query"))].append(item)
    results = []
    for (page, query), items in grouped.items():
        items.sort(key=lambda item: item.observed_at)
        if len(items) < 2:
            continue
        previous = items[0].metrics.get("clicks") or 0
        current = items[-1].metrics.get("clicks") or 0
        if previous and (previous - current) / previous >= config.min_decay_ratio:
            results.append(
                Diagnostic(
                    kind="decay",
                    target_url=page,
                    target_query=query,
                    summary="Comparable-window clicks declined materially.",
                    evidence=[
                        _evidence(items[0], "Previous comparison window"),
                        _evidence(items[-1], "Current comparison window"),
                    ],
                    confidence=0.75,
                    score=(previous - current) / previous,
                    risk="medium",
                )
            )
    return results


def find_architecture_issues(crawl) -> list[Diagnostic]:
    return []


def rank_diagnostics(diagnostics: list[Diagnostic], strategy: Strategy) -> list[Opportunity]:
    ranked = []
    for diagnostic in diagnostics:
        candidate = " ".join(filter(None, [diagnostic.target_url, diagnostic.target_query])).lower()
        aligned = any(priority.lower() in candidate for priority in strategy.priority_offerings)
        alignment = "aligned" if aligned else "neutral"
        ranked.append(
            Opportunity(
                diagnostic=diagnostic,
                page_archetype="service" if diagnostic.target_url else "guide",
                strategy_alignment=alignment,
                fingerprint=f"{diagnostic.kind}:{diagnostic.target_url}:{diagnostic.target_query}",
            )
        )
    return sorted(ranked, key=lambda opportunity: opportunity.diagnostic.score, reverse=True)
