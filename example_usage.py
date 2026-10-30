# -*- coding: utf-8 -*-
from client import OpenClawGenParkAlphaLeaderboard

lb = OpenClawGenParkAlphaLeaderboard()

p1 = {"id": "agent_alpha", "mu": 28.5, "sigma": 4.2}
p2 = {"id": "agent_beta", "mu": 26.0, "sigma": 5.1}

# 1. Match Quality
mq = lb.calculate_match_quality(p1, p2)
print(f"Match Quality: {mq['match_quality_score']} ({mq['matchmaking_tier']})")

# 2. Skill Rating Update (p1 wins)
res = lb.update_trueskill_ratings(p1, p2, outcome=1.0)
print(f"\nPost-Match Update:")
print(f"  {res['player1']['id']}: Mu={res['player1']['new_mu']}, Conservative Score={res['player1']['conservative_score']}")
print(f"  {res['player2']['id']}: Mu={res['player2']['new_mu']}, Conservative Score={res['player2']['conservative_score']}")

# 3. Sybil Detection
history = [
    {"p1": "agent_bot_a", "p2": "agent_bot_b", "outcome": 1.0} for _ in range(8)
]
sybil = lb.detect_collusion_sybils(history)
print(f"\nSybil Collusion Flags: {sybil['flagged_sybil_rings_count']}")
for f in sybil['flagged_collusion_pairs']:
    print(f"  Beneficiary: {f['beneficiary_agent']} fed by {f['victim_feed_agent']} (Win Rate: {f['win_rate']*100:.1f}%)")
