import os
import requests
from dotenv import load_dotenv

load_dotenv()

NLU_API_KEY = os.getenv('IBM_NLU_API_KEY')
NLU_URL = os.getenv('IBM_NLU_URL')

def generate_form_text(team_name, stats, form_string):
    """Fallback: builds form narrative without Granite."""
    wins = form_string.count('W')
    losses = form_string.count('L')
    label = 'excellent' if wins >= 4 else ('good' if wins == 3 else 'mixed' if wins == 2 else 'poor')
    return (
        f"{team_name} have won {stats['wins']} of their last 10 games, "
        f"scoring {stats['goals_per_game']:.1f} goals per game and "
        f"conceding {stats['conceded_per_game']:.1f}. "
        f"Their last 5 results are {form_string}, putting them in {label} form."
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
    text1 = generate_form_text(team1_name, team1_stats, team1_form)
    text2 = generate_form_text(team2_name, team2_stats, team2_form)
    return {
        'team1': analyze_team_form(text1),
        'team2': analyze_team_form(text2)
    }