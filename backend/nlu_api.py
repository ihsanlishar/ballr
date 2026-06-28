import os
import requests
from dotenv import load_dotenv

load_dotenv()

NLU_API_KEY = os.getenv('IBM_NLU_API_KEY')
NLU_URL = os.getenv('IBM_NLU_URL')

def generate_form_text(team_name, stats, form_string):
    """
    Build a form narrative focused on recent WC results.
    Narrative tone is driven by wins/draws/losses — not weighted stats.
    """
    wins   = form_string.count('W')
    draws  = form_string.count('D')
    losses = form_string.count('L')
    total  = len(form_string)

    if total == 0:
        return f"{team_name} have not played recently."

    # Momentum label driven purely by recent results
    if wins >= 3:
        momentum = "excellent recent form"
    elif wins == 2 and draws >= 1:
        momentum = "strong recent form"
    elif wins == 2:
        momentum = "good recent form"
    elif draws >= 2 and losses == 0:
        momentum = "solid unbeaten form"
    elif wins == 1 and draws >= 1:
        momentum = "decent recent form"
    elif draws >= 2:
        momentum = "mixed but unbeaten form"
    elif losses >= 3:
        momentum = "poor recent form"
    elif losses >= 2:
        momentum = "difficult recent form"
    else:
        momentum = "inconsistent recent form"

    # Build result sentence
    result_parts = []
    for r in form_string:
        if r == 'W':   result_parts.append("a win")
        elif r == 'D': result_parts.append("a draw")
        else:          result_parts.append("a loss")
    results_str = ", ".join(result_parts)

    # Attack/defense descriptors from weighted stats
    gpg = stats.get('goals_per_game', 1.2)
    cpg = stats.get('conceded_per_game', 1.2)

    attack_str  = "scoring freely" if gpg >= 2.0 else "finding the net regularly" if gpg >= 1.2 else "struggling to score"
    defense_str = "keeping a tight defense" if cpg <= 0.5 else "defending solidly" if cpg <= 1.2 else "conceding regularly"

    confidence  = "confidence and momentum" if (wins >= 2 or (draws >= 2 and losses == 0)) else "room to improve"

    return (
        f"{team_name} are in {momentum}, with results of {results_str} in their last {total} games. "
        f"They have been {attack_str} and {defense_str}. "
        f"Their recent performances suggest {confidence}."
    )

def analyze_team_form(text):
    """Calls Watson NLU to score sentiment of form narrative."""
    response = requests.post(
        f"{NLU_URL}/v1/analyze?version=2021-03-25",
        auth=('apikey', NLU_API_KEY),
        json={
            'text': text,
            'features': {'sentiment': {}}
        }
    )
    data = response.json()
    score = data['sentiment']['document']['score']
    label = 'Positive' if score > 0.2 else ('Negative' if score < -0.2 else 'Neutral')
    return {'score': score, 'label': label}

def get_both_team_nlu(team1_name, team1_stats, team1_form,
                       team2_name, team2_stats, team2_form):
    # Prefer WC form — more relevant than long-term weighted form
    t1_form = team1_stats.get('wc_form') or team1_form
    t2_form = team2_stats.get('wc_form') or team2_form

    text1 = generate_form_text(team1_name, team1_stats, t1_form)
    text2 = generate_form_text(team2_name, team2_stats, t2_form)

    return {
        'team1': analyze_team_form(text1),
        'team2': analyze_team_form(text2)
    }