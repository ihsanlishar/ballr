from flask import Flask, jsonify
from football_api import get_fixtures, get_team_stats, get_standings, get_top_scorers, parse_team_form
from nlu_api import get_both_team_nlu
from monte_carlo import run_simulation

app = Flask(__name__)

@app.route('/fixtures')
def fixtures():
    matches = get_fixtures()
    result = []
    for m in matches:
        result.append({
            'id': m['id'],
            'home': m['homeTeam']['name'],
            'away': m['awayTeam']['name'],
            'home_id': m['homeTeam']['id'],
            'away_id': m['awayTeam']['id'],
            'date': m['utcDate'],
            'status': m['status'],
            'home_score': m['score']['fullTime']['home'],
            'away_score': m['score']['fullTime']['away'],
            'stage': m['stage']
        })
    return jsonify(result)

@app.route('/match/<int:home_id>/<int:away_id>')
def match(home_id, away_id):
    home_matches = get_team_stats(home_id)
    away_matches = get_team_stats(away_id)

    home_stats = parse_team_form(home_matches, home_id)
    away_stats = parse_team_form(away_matches, away_id)

    nlu = get_both_team_nlu(
        'Home', home_stats, home_stats['form_string'],
        'Away', away_stats, away_stats['form_string']
    )

    simulation = run_simulation(home_stats, away_stats, nlu['team1'], nlu['team2'])

    return jsonify({
        'home_stats': home_stats,
        'away_stats': away_stats,
        'nlu': nlu,
        'simulation': simulation
    })

@app.route('/standings')
def standings():
    return jsonify(get_standings())

@app.route('/top-scorers')
def top_scorers():
    return jsonify(get_top_scorers())

if __name__ == '__main__':
    app.run(debug=True, port=5000)