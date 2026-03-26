"""
Lotto 6/49 game logic. Entertainment only; random draws are not cryptographically secure.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Iterable

POOL_MIN = 1
POOL_MAX = 49
PICK_COUNT = 6


def validate_selection(nums: Iterable[int]) -> bool:
    """True iff nums is exactly PICK_COUNT distinct integers in [POOL_MIN, POOL_MAX]."""
    try:
        s = set(int(x) for x in nums)
    except (TypeError, ValueError):
        return False
    if len(s) != PICK_COUNT:
        return False
    return all(POOL_MIN <= n <= POOL_MAX for n in s)


def quick_pick() -> list[int]:
    """Return six sorted distinct random numbers from the full pool."""
    return sorted(random.sample(range(POOL_MIN, POOL_MAX + 1), PICK_COUNT))


def draw_winning() -> list[int]:
    """Return six sorted distinct random winning numbers (same distribution as quick_pick)."""
    return sorted(random.sample(range(POOL_MIN, POOL_MAX + 1), PICK_COUNT))


def matches(player: Iterable[int], winning: Iterable[int]) -> int:
    """Count how many numbers appear in both tickets."""
    return len(set(player) & set(winning))


def simulate_match_histogram(player: Iterable[int], n: int) -> dict[int, int]:
    """
    Run n independent draws against the same ticket.
    Returns counts how often 0..6 matches occurred (keys 0 through 6).
    """
    p = set(player)
    ctr: Counter[int] = Counter()
    for _ in range(n):
        ctr[matches(p, draw_winning())] += 1
    return {i: ctr[i] for i in range(7)}


def quick_pick_rounds_fixed_winning(
    n: int, *, max_listed: int = 500
) -> tuple[list[int], list[int], list[str], dict[int, int], bool]:
    """
    Draw one fixed winning line, then n random player lines (quick picks).
    Each round compares a new random ticket to the same winning numbers.
    Returns (winning, last_ticket, detail_lines, histogram 0..6, truncated).
    """
    winning = draw_winning()
    ctr: Counter[int] = Counter()
    lines: list[str] = []
    last_ticket: list[int] = []
    for i in range(n):
        last_ticket = quick_pick()
        m = matches(last_ticket, winning)
        ctr[m] += 1
        if len(lines) < max_listed:
            nums = ", ".join(str(x) for x in last_ticket)
            lines.append(f"Round {i + 1}: {nums}  ->  {m} numbers correct")
    hist = {j: ctr[j] for j in range(7)}
    truncated = n > max_listed
    return winning, last_ticket, lines, hist, truncated


def simulate_histogram_for_tickets(tickets: list[list[int]]) -> dict[int, int]:
    """One fresh winning draw per ticket; histogram of match counts (0..6)."""
    ctr: Counter[int] = Counter()
    for t in tickets:
        w = draw_winning()
        ctr[matches(t, w)] += 1
    return {i: ctr[i] for i in range(7)}

