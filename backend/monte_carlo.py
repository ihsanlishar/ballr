import numpy as np

def run_simulation(home_stats, away_stats, home_nlu, away_nlu, n=50000):
    """
    Improved Monte Carlo with:
    - Weighted goals (recency + competition tier already in stats)
    - Win rate adjustment
    - Clean sheet rate feeds defensive multiplier
    - Goal difference anchors the base rate
    - NLU sentiment as a small final nudge
    - Home advantage (neutral for WC but slight edge)
    """

    # Base attacking rate from weighted goals per game
    lam1 = home_stats['goals_per_game']
    lam2 = away_stats['goals_per_game']

    # Defensive pressure: scale opponent attack down by your clean sheet rate
    # Higher clean sheet rate = better defense = suppress opponent more
    def defensive_factor(cs_rate):
        # cs_rate 0.0 → factor 1.1 (bad defense, opponent scores more)
        # cs_rate 0.5 → factor 0.85
        return 1.1 - (cs_rate * 0.5)

    lam1 *= defensive_factor(away_stats['clean_sheet_rate'])
    lam2 *= defensive_factor(home_stats['clean_sheet_rate'])

    # Win rate adjustment — teams that win more tend to outperform raw xG
    # Applied as a small multiplier around 1.0
    def win_rate_factor(wr):
        # wr 0.2 → 0.93, wr 0.5 → 1.0, wr 0.8 → 1.07
        return 0.93 + (wr * 0.14)

    lam1 *= win_rate_factor(home_stats['win_rate'])
    lam2 *= win_rate_factor(away_stats['win_rate'])

    # Goal difference anchor — teams with better GD get a small boost
    # GD per game: +2 → +6%, -2 → -6%
    lam1 *= (1 + np.clip(home_stats['gd_per_game'] * 0.03, -0.09, 0.09))
    lam2 *= (1 + np.clip(away_stats['gd_per_game'] * 0.03, -0.09, 0.09))

    # NLU sentiment nudge — small final adjustment (-1 to +1 → ±5%)
    lam1 *= (1 + home_nlu['score'] * 0.05)
    lam2 *= (1 + away_nlu['score'] * 0.05)

    # Clamp to realistic range
    lam1 = float(np.clip(lam1, 0.4, 3.5))
    lam2 = float(np.clip(lam2, 0.4, 3.5))

    # Run simulation
    goals1 = np.random.poisson(lam1, n)
    goals2 = np.random.poisson(lam2, n)

    home_wins = int(np.sum(goals1 > goals2))
    draws     = int(np.sum(goals1 == goals2))
    away_wins = int(np.sum(goals1 < goals2))

    # Score distribution heatmap data
    score_dist = {}
    for g1, g2 in zip(goals1, goals2):
        if g1 <= 5 and g2 <= 5:
            key = f'{g1}-{g2}'
            score_dist[key] = score_dist.get(key, 0) + 1

    total = sum(score_dist.values())
    score_dist_pct = {k: round(v / total * 100, 1) for k, v in score_dist.items()}
    top_scores = sorted(score_dist_pct.items(), key=lambda x: x[1], reverse=True)[:5]

    # Expected goals for display
    avg_g1 = float(np.mean(goals1))
    avg_g2 = float(np.mean(goals2))

    return {
        'team1_win_pct': round(home_wins / n * 100, 1),
        'draw_pct':      round(draws / n * 100, 1),
        'team2_win_pct': round(away_wins / n * 100, 1),
        'team1_xg':      round(avg_g1, 2),
        'team2_xg':      round(avg_g2, 2),
        'team1_lambda':  round(lam1, 3),
        'team2_lambda':  round(lam2, 3),
        'top_scores':    top_scores,
        'score_dist':    score_dist_pct,
    }