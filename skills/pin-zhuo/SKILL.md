---
name: pin-zhuo
description: "Group dining constraint solver: collects each member's constraints (time, location, budget, dietary) via private DM, then computes the Pareto-optimal restaurant that satisfies ALL constraints. No voting, just math."
metadata:
  openclaw:
    emoji: "帆"
    requires:
      bins: [python3]
    install:
      - id: pip
        kind: shell
        command: "pip install -e skills/pin-zhuo"
        label: "Install pin-zhuo dependencies"
---

# pin-zhuo · 拼桌

Group dining made effortless. No voting, no arguing — constraint solving.

## When to use

- Someone says "聚餐"/"约饭"/"周末吃啥"/"几个人吃饭" in a group chat
- User asks to plan a group meal

## Commands

```bash
# Start a group plan session
pinzhuo start --group-id grp_001 --members "alice,bob,charlie" --date "2026-06-07"

# Add one member's constraints
pinzhuo constrain --group-id grp_001 --member alice \
  --location "海淀" --budget-max 150 \
  --dietary-exclude "花生,香菜" --time-windows "18:00-20:00"

# Solve: find the optimal restaurant
pinzhuo solve --group-id grp_001

# Show explanation of why this restaurant was chosen
pinzhuo explain --group-id grp_001 --solution-id sol_1
```

## Algorithm

Constraint Satisfaction Problem (CSP):
1. Hard constraints (MUST satisfy all): dietary exclusions, budget ceiling, open hours
2. Soft constraints (optimize): location proximity to geographic midpoint,
   cuisine preference intersection, rating, novelty
3. Solver: backtracking with constraint propagation + Pareto ranking on soft objectives
4. Output: top 3 Pareto-optimal solutions with per-member satisfaction breakdown

## Output format

JSON with solution array containing restaurant info, per-member satisfaction scores (0-1), reasons why each constraint is met or stretched, geographic midpoint distance, and explanation.

## Privacy

- Constraints are collected via **private DM** to each member
- Individual preferences are never shown to other group members
- Only the aggregated solution is posted to the group
- All data stored locally in SQLite, clearable via `pinzhuo clear`
