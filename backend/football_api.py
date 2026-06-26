import os
import requests
from cachetools import TTLCache, cached
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'
HEADERS = {'X-Auth-Token': API_KEY}

cache = TTLCache(maxsize=128, ttl=300)

@cached(cache)
def get_fixtures():
    r = requests.get(f'{BASE_URL}/competitions/WC/matches', headers=HEADERS)
    data = r.json()
    return data.get('matches', [])

@cached(cache)
def get_team_stats(team_id):
    r = requests.get(f'{BASE_URL}/teams/{team_id}/matches?limit=10', headers=HEADERS)
    return r.json()

@cached(cache)
def get_standings():
    r = requests.get(f'{BASE_URL}/competitions/WC/standings', headers=HEADERS)
    return r.json()

@cached(cache)
def get_top_scorers():
    r = requests.get(f'{BASE_URL}/competitions/WC/scorers', headers=HEADERS)
    return r.json()

def parse_team_form(matches, team_id):
    results = []
    goals_scored = []
    goals_conceded = []

    for m in matches.get('matches', []):
        if m['status'] != 'FINISHED':
            continue
        home = m['homeTeam']['id'] == team_id
        score = m['score']['fullTime']
        gf = score['home'] if home else score['away']
        ga = score['away'] if home else score['home']
        if gf is None or ga is None:
            continue
        goals_scored.append(gf)
        goals_conceded.append(ga)
        if gf > ga:
            results.append('W')
        elif gf == ga:
            results.append('D')
        else:
            results.append('L')

    last5 = ''.join(results[-5:]) if len(results) >= 5 else ''.join(results)
    wins = results.count('W')
    draws = results.count('D')
    losses = results.count('L')
    gpg = sum(goals_scored) / len(goals_scored) if goals_scored else 1.2
    cpg = sum(goals_conceded) / len(goals_conceded) if goals_conceded else 1.0

    return {
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_per_game': gpg,
        'conceded_per_game': cpg,
        'form_string': last5
    }