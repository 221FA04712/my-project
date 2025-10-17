from typing import Dict, List


def optimize_budget(
    departments: List[str],
    impact_per_dollar: Dict[str, float],
    total_budget: float,
    min_per_dept: Dict[str, float] | None = None,
    max_per_dept: Dict[str, float] | None = None,
) -> Dict[str, float]:
    n = len(departments)
    if n == 0:
        return {}

    # Initialize with minimums
    allocations: Dict[str, float] = {}
    remaining = total_budget
    for d in departments:
        minimum = float(min_per_dept.get(d, 0.0)) if min_per_dept else 0.0
        allocations[d] = max(0.0, minimum)
        remaining -= allocations[d]

    if remaining < 0:
        # Normalize down proportionally to fit total_budget
        current_total = sum(allocations.values())
        if current_total == 0:
            return {d: 0.0 for d in departments}
        factor = total_budget / current_total
        return {d: allocations[d] * factor for d in departments}

    # Greedy distribute remaining by impact weight until max caps hit
    caps = {d: float(max_per_dept[d]) if (max_per_dept and d in max_per_dept) else float("inf") for d in departments}

    # Avoid infinite loops: iterate at most a fixed number of steps
    steps = 1000
    while remaining > 1e-6 and steps > 0:
        steps -= 1
        # Choose department with highest marginal impact not at cap
        candidates = [d for d in departments if allocations[d] < caps[d]]
        if not candidates:
            break
        best = max(candidates, key=lambda d: impact_per_dollar.get(d, 0.0))
        if impact_per_dollar.get(best, 0.0) <= 0:
            break

        # Allocate a small chunk to the best department
        chunk = max(remaining * 0.2, min(10.0, remaining))  # heuristic step
        room = caps[best] - allocations[best]
        delta = min(chunk, room, remaining)
        if delta <= 0:
            # No room to allocate
            caps[best] = allocations[best]
            continue
        allocations[best] += delta
        remaining -= delta

    # If still remaining and no positive impact, distribute evenly within caps
    if remaining > 1e-6:
        open_depts = [d for d in departments if allocations[d] < caps[d]]
        if open_depts:
            per = remaining / len(open_depts)
            for d in open_depts:
                allocations[d] += min(per, caps[d] - allocations[d])

    return {d: float(allocations[d]) for d in departments}
