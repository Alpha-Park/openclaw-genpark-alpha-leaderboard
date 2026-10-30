# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Alpha Leaderboard - Bayesian TrueSkill Glicko-2 Matchmaker & Anti-Sybil Auditor
Standard Library only: math, typing.
Calculates Bayesian TrueSkill skill updates (mu and sigma), evaluates competitive match quality,
and detects anomalous pairwise win-trading and anti-collusion Sybil rings.
"""

import math
from typing import Dict, List, Any

class OpenClawGenParkAlphaLeaderboard:
    def __init__(self, default_beta: float = 4.167):
        self.default_beta = default_beta

    def update_trueskill_ratings(self, player1: Dict[str, Any],
                                 player2: Dict[str, Any],
                                 outcome: float,
                                 beta: float = None) -> Dict[str, Any]:
        """
        Updates Bayesian skill belief (mu, sigma) following a match:
        outcome: 1.0 = Player 1 wins, 0.5 = Draw, 0.0 = Player 2 wins.
        Conservative skill rank score: mu - 3 * sigma
        """
        b = beta if beta is not None else self.default_beta
        mu1 = float(player1.get("mu", 25.0))
        sig1 = float(player1.get("sigma", 8.333))
        mu2 = float(player2.get("mu", 25.0))
        sig2 = float(player2.get("sigma", 8.333))

        c = math.sqrt(2.0 * (b ** 2) + (sig1 ** 2) + (sig2 ** 2))
        t = (mu1 - mu2) / c

        # Logistic win probability approximation
        expected_win_p1 = 1.0 / (1.0 + math.exp(-1.702 * t))
        v = outcome - expected_win_p1

        # Skill updates
        new_mu1 = mu1 + ((sig1 ** 2) / c) * v
        new_mu2 = mu2 - ((sig2 ** 2) / c) * v

        # Uncertainty decay (measurements increase precision)
        decay_factor1 = 1.0 - ((sig1 ** 2) / (c ** 2)) * 0.25
        decay_factor2 = 1.0 - ((sig2 ** 2) / (c ** 2)) * 0.25
        new_sig1 = max(0.5, sig1 * math.sqrt(max(0.1, decay_factor1)))
        new_sig2 = max(0.5, sig2 * math.sqrt(max(0.1, decay_factor2)))

        score1 = new_mu1 - 3.0 * new_sig1
        score2 = new_mu2 - 3.0 * new_sig2

        return {
            "match_outcome": outcome,
            "expected_win_p1": round(expected_win_p1, 4),
            "player1": {
                "id": player1.get("id", "p1"),
                "new_mu": round(new_mu1, 4),
                "new_sigma": round(new_sig1, 4),
                "conservative_score": round(score1, 4)
            },
            "player2": {
                "id": player2.get("id", "p2"),
                "new_mu": round(new_mu2, 4),
                "new_sigma": round(new_sig2, 4),
                "conservative_score": round(score2, 4)
            }
        }

    def calculate_match_quality(self, player1: Dict[str, Any],
                                player2: Dict[str, Any],
                                beta: float = None) -> Dict[str, Any]:
        """
        Calculates competitive match quality q in (0, 1].
        Matches with q close to 1.0 are evenly matched and yield highest information gain.
        """
        b = beta if beta is not None else self.default_beta
        mu1, sig1 = float(player1.get("mu", 25.0)), float(player1.get("sigma", 8.333))
        mu2, sig2 = float(player2.get("mu", 25.0)), float(player2.get("sigma", 8.333))

        denom = 2.0 * (b ** 2) + (sig1 ** 2) + (sig2 ** 2)
        factor = math.sqrt(2.0 * (b ** 2) / denom)
        exponent = - ((mu1 - mu2) ** 2) / (2.0 * denom)
        match_quality = factor * math.exp(exponent)

        if match_quality >= 0.70:
            tier = "OPTIMAL_HIGH_STAKES_MATCH"
        elif match_quality >= 0.40:
            tier = "ACCEPTABLE_BALANCED_MATCH"
        else:
            tier = "MISMATCH_LOW_INFORMATION_VALUE"

        return {
            "player1_id": player1.get("id", "p1"),
            "player2_id": player2.get("id", "p2"),
            "match_quality_score": round(match_quality, 4),
            "matchmaking_tier": tier
        }

    def detect_collusion_sybils(self, match_history: List[Dict[str, Any]],
                                win_rate_threshold: float = 0.90) -> Dict[str, Any]:
        """
        Detects anomalous pairwise win-farming collusion patterns between agents.
        """
        pair_stats = {} # (p1, p2) -> {"p1_wins": 0, "p2_wins": 0, "draws": 0}

        for m in match_history:
            p1, p2 = m["p1"], m["p2"]
            outcome = m.get("outcome", 0.5)
            key = tuple(sorted([p1, p2]))
            if key not in pair_stats:
                pair_stats[key] = {"total_matches": 0, "wins": {p1: 0, p2: 0}, "draws": 0}
            
            pair_stats[key]["total_matches"] += 1
            if outcome == 1.0:
                pair_stats[key]["wins"][p1] += 1
            elif outcome == 0.0:
                pair_stats[key]["wins"][p2] += 1
            else:
                pair_stats[key]["draws"] += 1

        flagged_pairs = []
        for (a, b), stats in pair_stats.items():
            tot = stats["total_matches"]
            if tot >= 5: # Threshold for sample significance
                w_a = stats["wins"].get(a, 0)
                w_b = stats["wins"].get(b, 0)
                dominant_win_rate = max(w_a, w_b) / tot
                if dominant_win_rate >= win_rate_threshold:
                    victim = b if w_a > w_b else a
                    beneficiary = a if w_a > w_b else b
                    flagged_pairs.append({
                        "beneficiary_agent": beneficiary,
                        "victim_feed_agent": victim,
                        "total_pairwise_matches": tot,
                        "win_rate": round(dominant_win_rate, 3),
                        "verdict": "COLLUSIVE_WIN_TRADING_SYBIL_DETECTED"
                    })

        return {
            "pairs_evaluated_count": len(pair_stats),
            "flagged_sybil_rings_count": len(flagged_pairs),
            "flagged_collusion_pairs": flagged_pairs
        }
