"""Tool allowlist + registry.

The allowlist is the strongest guardrail (report 4.3): a capability that does not
exist cannot be injected into existence. There is deliberately NO order-placement
tool anywhere in the codebase. The planner's proposed plan is filtered through
`filter_plan` so anything off this list is discarded before execution.
"""
from __future__ import annotations

# The ONLY tool names the agent may ever run.
ALLOWLIST: tuple[str, ...] = (
    "resolve_ticker",
    "fetch_quote",
    "fetch_series",
    "fetch_news",
    "retrieve",
    "speak",
)

# Capabilities that must never exist. Asserted by a unit test on this module.
FORBIDDEN: tuple[str, ...] = (
    "place_order", "buy", "sell", "trade", "cancel_order", "modify_order",
)


def filter_plan(names: list[str]) -> list[str]:
    """Keep only allowlisted tool names, preserving order and de-duplicating."""
    seen: set[str] = set()
    out: list[str] = []
    for n in names or []:
        n = (n or "").strip()
        if n in ALLOWLIST and n not in seen:
            seen.add(n)
            out.append(n)
    return out
