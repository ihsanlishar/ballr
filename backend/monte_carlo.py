import numpy as np
from scipy.stats import poisson

def run_simulation(team1_stats, team2_stats, team1_nlu, team2_nlu, n=10000):
    # Base scoring rates from stats
    lam1 = team1_stats['goals_per_game']
    lam2 = team2_stats['goals_per_game']

    # Adjust for defensive strength
    lam1 *= (1 + (1 - team2_stats['conceded_per_game'] / 1.5) * 0.1)
    lam2 *= (1 + (1 - team1_stats['conceded_per_game'] / 1.5) * 0.1)

    # Adjust for NLU sentiment score (-1 to 1 → small multiplier)
    lam1 *= (1 + team1_nlu['score'] * 0.07)
    lam2 *= (1 + team2_nlu['score'] * 0.07)

    # Clamp to reasonable range
    lam1 = max(0.5, min(lam1, 4.0))
    lam2 = max(0.5, min(lam2, 4.0))

    # Run simulation
    goals1 = np.random.poisson(lam1, n)
    goals2 = np.random.poisson(lam2, n)

    team1_wins = int(np.sum(goals1 > goals2))
    draws = int(np.sum(goals1 == goals2))
    team2_wins = int(np.sum(goals1 < goals2))

    # Score distribution (0-0 to 4-4)
    score_dist = {}
    for g1, g2 in zip(goals1, goals2):
        if g1 <= 4 and g2 <= 4:
            key = f'{g1}-{g2}'
            score_dist[key] = score_dist.get(key, 0) + 1

    # Convert to percentages
    total = sum(score_dist.values())
    score_dist = {k: round(v / total * 100, 1) for k, v in score_dist.items()}

    # Top 5 most likely scores
    top_scores = sorted(score_dist.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'team1_win_pct': round(team1_wins / n * 100, 1),
        'draw_pct': round(draws / n * 100, 1),
        'team2_win_pct': round(team2_wins / n * 100, 1),
        'team1_xg': round(lam1, 2),
        'team2_xg': round(lam2, 2),
        'top_scores': top_scores
    }