# Ballr ⚽

Ballr is a World Cup match prediction and analytics platform. Instead of handing you a single win/loss guess, it shows you a full probabilistic breakdown of every fixture, backed by a statistical simulation, a real momentum signal pulled from natural language, and a live dashboard that checks the model's own accuracy as the tournament plays out.

**Live app:** https://ballr-tech.streamlit.app/

## The problem

Most football prediction tools give you a confident-sounding number and nothing else. There's no way to tell if a "70% chance" actually means anything, and most models also ignore the fact that a team's recent form and momentum say something real about how they'll play, beyond just goals scored and conceded. We wanted to build something that combines hard statistics with that softer momentum signal, and then proves whether its own predictions are actually any good.

## Our approach

Ballr pulls live World Cup fixtures, standings, and each team's last 20 matches from the football-data.org API. From that, it builds a weighted form profile for every team: goals for and against, clean sheet rate, win rate, and goal difference, all weighted so that more recent matches and higher-tier competitions (a World Cup match counts more than a friendly) carry more influence.

That profile feeds a Monte Carlo simulation that plays out 50,000 randomized versions of the match using a Poisson goal model, factoring in each team's attacking output, defensive solidity, and recent goal difference. The output is a full win/draw/loss probability split, an expected scoreline, and a score distribution heatmap, not just a single predicted result.

On top of that, the model gets a momentum signal from natural language. For each team, Ballr generates a short plain-English summary of their recent form (results, scoring rate, defensive record) and runs it through IBM Watson Natural Language Understanding for sentiment analysis. That sentiment score becomes a small, capped adjustment on the team's expected goals in the simulation, enough to matter in close matchups, not enough to override what the stats actually say.

Finally, there's a live Model Accuracy & Calibration page. As World Cup matches finish, Ballr automatically re-grades its own pre-match predictions against the real results, tracking overall accuracy, exact scoreline hits, accuracy broken down by outcome type, and a calibration curve that checks whether "70% confident" predictions actually win about 70% of the time. The model has to answer for itself instead of just being trusted.

## How we used AI

The core AI component is **IBM Watson Natural Language Understanding**, used for sentiment analysis on auto-generated team form narratives. Rather than treating NLP as a separate feature, it's wired directly into the prediction engine: the sentiment score Watson returns is applied as a real, bounded adjustment to each team's expected-goals rate inside the Monte Carlo simulation, so language-derived momentum and stats-derived form combine into a single forecast instead of sitting side by side.

## Tech stack

- **Backend:** Python, Flask
- **Simulation engine:** NumPy, SciPy (Poisson-based Monte Carlo, 50,000 trials per match)
- **AI/NLP:** IBM Watson Natural Language Understanding (sentiment analysis)
- **Data source:** football-data.org API
- **Frontend:** Streamlit, Plotly
- **Deployment:** Railway (backend), Streamlit Community Cloud (frontend)

## Project structure
