---
name: openclaw-genpark-alpha-leaderboard
description: OpenClaw GenPark Alpha Leaderboard - Bayesian TrueSkill Glicko-2 matchmaker and anti-Sybil collusion auditor with conservative rating scores.
category: Service
version: 1.0.0
license: MIT
tools:
  - update_trueskill_ratings
  - calculate_match_quality
  - detect_collusion_sybils
---

# Openclaw Genpark Alpha Leaderboard

## Overview & Agent Behavioral Directives
You are an autonomous agent specialized in **Openclaw Genpark Alpha Leaderboard**.
Your primary directive is to execute: OpenClaw GenPark Alpha Leaderboard - Bayesian TrueSkill Glicko-2 matchmaker and anti-Sybil collusion auditor with conservative rating scores.
Always ensure mathematical precision, parameter validation, and deterministic outputs.

## When to Activate This Skill
- Activate when an agent workflow or user instruction requires:
- `update_trueskill_ratings`
- `calculate_match_quality`
- `detect_collusion_sybils`
- Activate when operating in zero-dependency environments requiring pure Python standard library execution.

## How to Execute

### Option 1: Direct Python Execution (Zero-Dependency)
```python
from client import *

# Client operates purely on standard Python library:
# Initialized and ready for direct function invocation.
```

### Option 2: FastMCP Tool Calling
Tools registered in `mcp_server.py`:
- `update_trueskill_ratings`
- `calculate_match_quality`
- `detect_collusion_sybils`

## Core Mathematical & Algorithmic Guardrails
- **Zero-Dependency Policy**: 100% Python standard library only (`math`, `heapq`, `hashlib`, `urllib`, `collections`, `itertools`, `typing`).
- **Zero-Mock Policy**: Pure deterministic algorithms with full validation and error bounds.
