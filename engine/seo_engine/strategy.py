from __future__ import annotations

from pathlib import Path

import yaml

from seo_engine.domain.models import Opportunity, Strategy, StrategyAlignment


def load_strategy(path: Path) -> Strategy:
    return Strategy.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


def compare_strategy(opportunity: Opportunity, strategy: Strategy) -> StrategyAlignment:
    candidate = " ".join(
        filter(
            None,
            [opportunity.diagnostic.target_url, opportunity.diagnostic.target_query],
        )
    ).lower()
    if any(path and path in candidate for path in strategy.excluded_paths):
        return StrategyAlignment(
            status="excluded", rationale="Target matches an excluded path.", score_delta=-100
        )
    if any(priority.lower() in candidate for priority in strategy.priority_offerings):
        return StrategyAlignment(
            status="aligned", rationale="Target matches a priority offering.", score_delta=25
        )
    return StrategyAlignment(status="neutral", rationale="No configured priority match.")


def adjust_priorities(opportunities: list[Opportunity], strategy: Strategy) -> list[Opportunity]:
    adjusted = []
    for opportunity in opportunities:
        alignment = compare_strategy(opportunity, strategy)
        opportunity.strategy_alignment = alignment.status
        opportunity.diagnostic.score += alignment.score_delta
        adjusted.append(opportunity)
    return sorted(
        (item for item in adjusted if item.strategy_alignment != "excluded"),
        key=lambda item: item.diagnostic.score,
        reverse=True,
    )
