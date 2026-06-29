import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timezone, date
import os
BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")

st.set_page_config(
    page_title="Ballr",
    page_icon="⚽",
    layout="wide"
)

# ── Team colors ────────────────────────────────────────────────────────────
TEAM_COLORS = {
    'Algeria':              '#006233',
    'Argentina':            '#74ACDF',
    'Australia':            '#FFD700',
    'Austria':              '#ED2939',
    'Belgium':              '#000000',
    'Bosnia-Herzegovina':   '#002395',
    'Brazil':               '#F7D116',
    'Canada':               '#FF0000',
    'Cape Verde Islands':   '#003893',
    'Colombia':             '#FCD116',
    'Congo DR':             '#007FFF',
    'Croatia':              '#FF0000',
    'Curaçao':              '#003DA5',
    'Czechia':              '#D7141A',
    'Ecuador':              '#FFD100',
    'Egypt':                '#CE1126',
    'England':              '#CF091D',
    'France':               '#002395',
    'Germany':              '#000000',
    'Ghana':                '#FCD116',
    'Haiti':                '#00209F',
    'Iran':                 '#239F40',
    'Iraq':                 '#007A3D',
    'Ivory Coast':          '#F77F00',
    'Japan':                '#BC002D',
    'Jordan':               '#007A3D',
    'Mexico':               '#006847',
    'Morocco':              '#C1272D',
    'Netherlands':          '#FF6600',
    'New Zealand':          '#000000',
    'Norway':               '#EF2B2D',
    'Panama':               '#DA121A',
    'Paraguay':             '#D52B1E',
    'Portugal':             '#006600',
    'Qatar':                '#8D1B3D',
    'Saudi Arabia':         '#006C35',
    'Scotland':             '#003DA5',
    'Senegal':              '#00853F',
    'South Africa':         '#007A4D',
    'South Korea':          '#CD2E3A',
    'Spain':                '#AA151B',
    'Sweden':               '#006AA7',
    'Switzerland':          '#FF0000',
    'Tunisia':              '#E70013',
    'Turkey':               '#E30A17',
    'United States':        '#002868',
    'Uruguay':              '#5EB6E4',
    'Uzbekistan':           '#1EB53A',
}

TEAM_COLORS_AWAY = {
    'Germany':      '#FFFFFF',
    'Belgium':      '#FFD700',
    'New Zealand':  '#FFFFFF',
    'Ghana':        '#006B3F',
    'Colombia':     '#003087',
}

def get_team_color(team, is_away=False, other_team=None):
    color = TEAM_COLORS.get(team, '#4a9eff')
    if other_team:
        other_color = TEAM_COLORS.get(other_team, '#7dd3fc')
        if color.lower() == other_color.lower():
            color = TEAM_COLORS_AWAY.get(team, '#ffffff')
    return color

def hex_to_rgba(hex_color, alpha=1.0):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'

st.markdown("""
<style>
    .main, [data-testid="stAppViewContainer"], section[data-testid="stMain"] {
        background-color: #080d18 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem !important; max-width: 1400px; }

    .ballr-title { font-size:2.8rem;font-weight:900;color:#ffffff;letter-spacing:-2px;line-height:1; }
    .ballr-sub   { font-size:0.82rem;color:#3d4f6b;letter-spacing:2px;text-transform:uppercase;margin-top:2px;margin-bottom:28px; }

    [data-testid="stTabs"] { border-bottom:1px solid #131e30 !important;margin-bottom:24px; }
    [data-testid="stTabs"] button { font-size:0.8rem !important;font-weight:600 !important;color:#3d4f6b !important;padding:10px 22px !important;border-radius:0 !important;border:none !important;background:transparent !important;letter-spacing:0.5px; }
    [data-testid="stTabs"] button:hover { color:#94a3b8 !important; }
    [data-testid="stTabs"] button[aria-selected="true"] { color:#ffffff !important;border-bottom:2px solid #4a9eff !important; }

    .date-group { font-size:0.68rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#3d4f6b;margin:28px 0 14px 0;display:flex;align-items:center;gap:12px; }
    .date-group::after { content:'';flex:1;height:1px;background:#131e30; }
    .date-group-today { color:#4a9eff; }

    .match-card { background:#0d1526;border:1px solid #131e30;border-radius:14px;padding:18px 20px 14px 20px;margin-bottom:3px; }
    .card-comp  { font-size:0.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b;margin-bottom:12px; }
    .card-body  { display:flex;align-items:center;justify-content:space-between;gap:8px; }
    .card-team-home { font-size:1rem;font-weight:700;color:#e2e8f0;flex:1; }
    .card-team-away { font-size:1rem;font-weight:700;color:#e2e8f0;flex:1;text-align:right; }
    .card-winner { color:#f0fdf4 !important; }
    .card-loser  { color:#3d4f6b !important; }
    .card-score-block { display:flex;flex-direction:column;align-items:center;gap:2px;min-width:72px; }
    .card-score-nums  { display:flex;align-items:center;gap:6px; }
    .card-score-num   { font-size:1.5rem;font-weight:900;color:#ffffff;min-width:20px;text-align:center;line-height:1; }
    .card-score-sep   { font-size:1rem;color:#1e2d45;font-weight:300; }
    .card-vs          { font-size:0.72rem;font-weight:600;color:#1e2d45;letter-spacing:1px; }
    .card-footer      { display:flex;justify-content:space-between;align-items:center;margin-top:12px;padding-top:10px;border-top:1px solid #0f1626; }
    .card-time        { font-size:0.73rem;color:#3d4f6b; }

    .badge-ft       { font-size:0.6rem;font-weight:700;letter-spacing:1.5px;background:#131e30;color:#3d4f6b;border-radius:20px;padding:3px 10px; }
    .badge-live     { font-size:0.6rem;font-weight:700;letter-spacing:1.5px;background:#0f2d1a;color:#4ade80;border-radius:20px;padding:3px 10px; }
    .badge-upcoming { font-size:0.6rem;font-weight:700;letter-spacing:1.5px;background:#0d1a2e;color:#4a9eff;border-radius:20px;padding:3px 10px; }

    .stButton > button { background:transparent !important;border:1px solid #131e30 !important;color:#3d4f6b !important;border-radius:8px !important;font-size:0.75rem !important;font-weight:600 !important;padding:6px 0 !important;width:100% !important;letter-spacing:0.5px;transition:all 0.15s !important; }
    .stButton > button:hover { border-color:#4a9eff !important;color:#4a9eff !important;background:#0d1a2e !important; }

    .match-hero { background:linear-gradient(160deg,#0d1a2e 0%,#080d18 100%);border:1px solid #131e30;border-radius:20px;padding:48px 40px 40px 40px;text-align:center;margin-bottom:32px;position:relative;overflow:hidden; }
    .hero-meta   { font-size:0.72rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b;margin-bottom:16px; }
    .hero-teams  { font-size:2rem;font-weight:900;color:#ffffff;letter-spacing:-0.5px;margin-bottom:4px; }
    .hero-vs     { color:#131e30; }
    .hero-score  { font-size:5rem;font-weight:900;letter-spacing:-4px;line-height:1;margin:8px 0 16px 0; }
    .hero-score-sep { color:#1e2d45;letter-spacing:0; }
    .hero-badges { display:flex;justify-content:center;align-items:center;gap:12px;margin-top:4px; }
    .hero-badge-w { background:#0f2d1a;color:#4ade80;border:1px solid #166534;border-radius:20px;padding:4px 16px;font-size:0.72rem;font-weight:700;letter-spacing:1px; }
    .hero-badge-l { background:#1f0f0f;color:#f87171;border:1px solid #7f1d1d;border-radius:20px;padding:4px 16px;font-size:0.72rem;font-weight:700;letter-spacing:1px; }
    .hero-badge-d { background:#131e30;color:#94a3b8;border:1px solid #1e2d45;border-radius:20px;padding:4px 16px;font-size:0.72rem;font-weight:700;letter-spacing:1px; }
    .hero-result  { font-size:0.85rem;color:#3d4f6b; }

    .sec-header { font-size:0.65rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#3d4f6b;margin:36px 0 16px 0;display:flex;align-items:center;gap:12px; }
    .sec-header::after { content:'';flex:1;height:1px;background:#0f1626; }

    .goal-row        { display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #0f1626; }
    .goal-row:last-child { border-bottom:none; }
    .goal-minute { background:#0f2d1a;color:#4ade80;border-radius:6px;padding:4px 8px;font-size:0.75rem;font-weight:800;min-width:38px;text-align:center; }
    .red-minute  { background:#1f0f0f;color:#f87171;border-radius:6px;padding:4px 8px;font-size:0.75rem;font-weight:800;min-width:38px;text-align:center; }
    .goal-player { font-size:0.9rem;color:#e2e8f0;font-weight:500; }
    .no-goals    { font-size:0.82rem;color:#3d4f6b;padding:8px 0; }

    .timeline-wrap   { background:#0d1526;border:1px solid #131e30;border-radius:10px;padding:16px 20px 12px 20px;margin-top:20px; }
    .timeline-bar    { position:relative;background:#080d18;border-radius:6px;height:40px;margin:8px 0 6px 0; }
    .timeline-labels { display:flex;justify-content:space-between;font-size:0.65rem;color:#3d4f6b;margin-top:4px; }

    .stat-box       { background:#0d1526;border:1px solid #131e30;border-radius:12px;padding:20px 16px;text-align:center; }
    .stat-val       { font-size:1.8rem;font-weight:800;color:#4a9eff;line-height:1;margin-bottom:6px; }
    .stat-val-green { font-size:1.8rem;font-weight:800;color:#4ade80;line-height:1;margin-bottom:6px; }
    .stat-val-red   { font-size:1.8rem;font-weight:800;color:#f87171;line-height:1;margin-bottom:6px; }
    .stat-val-white { font-size:1.8rem;font-weight:800;color:#ffffff;line-height:1;margin-bottom:6px; }
    .stat-lbl       { font-size:0.65rem;color:#3d4f6b;text-transform:uppercase;letter-spacing:1.5px; }

    .form-pill-W { display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;background:#0f2d1a;color:#4ade80;border-radius:6px;font-weight:800;font-size:0.82rem;margin:2px; }
    .form-pill-D { display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;background:#131e30;color:#94a3b8;border-radius:6px;font-weight:800;font-size:0.82rem;margin:2px; }
    .form-pill-L { display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;background:#1f0f0f;color:#f87171;border-radius:6px;font-weight:800;font-size:0.82rem;margin:2px; }

    .form-block      { background:#0d1526;border:1px solid #131e30;border-radius:12px;padding:20px; }
    .form-team-name  { font-size:1rem;font-weight:700;color:#ffffff;margin-bottom:12px; }
    .form-stats-row  { font-size:0.78rem;color:#3d4f6b;margin-top:10px;line-height:1.7; }

    .nlu-explainer { background:#0d1526;border-left:2px solid #1e3a5f;border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:20px;font-size:0.82rem;color:#4b5a75;line-height:1.7; }
    .nlu-card      { background:#0d1526;border:1px solid #131e30;border-radius:12px;padding:20px; }
    .nlu-team-name       { font-size:1rem;font-weight:700;color:#ffffff;margin-bottom:4px; }
    .nlu-sentiment-label { font-size:0.78rem;color:#4b5a75;margin-bottom:12px; }
    .nlu-bar-bg  { background:#080d18;border-radius:6px;height:6px;width:100%;margin:8px 0 6px 0; }
    .nlu-score-row   { display:flex;justify-content:space-between;align-items:center;margin-top:6px; }
    .nlu-score-label { font-size:0.65rem;color:#3d4f6b; }
    .nlu-score-val   { font-size:0.88rem;font-weight:700; }

    .insight-box { background:#0d1526;border-left:3px solid #4a9eff;border-radius:0 10px 10px 0;padding:16px 20px;margin:16px 0;font-size:0.85rem;color:#64748b;line-height:1.7; }
    .insight-box strong { color:#e2e8f0; }

    .key-factors { background:#0d1526;border:1px solid #131e30;border-radius:14px;padding:24px;margin:16px 0; }
    .kf-row      { display:flex;align-items:flex-start;gap:14px;padding:12px 0;border-bottom:1px solid #0f1626; }
    .kf-row:last-child { border-bottom:none; }
    .kf-icon  { font-size:1.1rem;min-width:24px;margin-top:1px; }
    .kf-label { font-size:0.72rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#3d4f6b;margin-bottom:3px; }
    .kf-text  { font-size:0.88rem;color:#94a3b8;line-height:1.5; }
    .kf-text strong { color:#e2e8f0; }
    .kf-badge-pos { display:inline-block;background:#0f2d1a;color:#4ade80;border-radius:4px;padding:1px 7px;font-size:0.72rem;font-weight:700;margin-left:6px; }
    .kf-badge-neg { display:inline-block;background:#1f0f0f;color:#f87171;border-radius:4px;padding:1px 7px;font-size:0.72rem;font-weight:700;margin-left:6px; }
    .kf-badge-neu { display:inline-block;background:#131e30;color:#94a3b8;border-radius:4px;padding:1px 7px;font-size:0.72rem;font-weight:700;margin-left:6px; }

    .heatmap-wrap { background:#0d1526;border:1px solid #131e30;border-radius:14px;padding:24px;margin:8px 0; }

    .empty-state { text-align:center;padding:60px 20px;color:#3d4f6b; }
    .empty-icon  { font-size:2.5rem;margin-bottom:12px; }

    /* Win probability boxes */
    .prob-boxes-col { display:flex; flex-direction:column; gap:8px; height:300px; padding:4px 0; }
    .prob-box {
        background: #0d1526;
        border: 1px solid #131e30;
        border-radius: 12px;
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 8px;
    }
    .prob-box.highlighted { border-color: #1e3a5f; background: #0a1628; }
    .prob-box-label { font-size:0.65rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#3d4f6b; margin-bottom:6px; }
    .prob-box-pct { font-size:2.4rem; font-weight:900; line-height:1; }
    .prob-box-pct.blue { color: #4a9eff; }
    .prob-box-pct.dim  { color: #1e2d45; }
    .prob-box-sub { font-size:0.72rem; color:#3d4f6b; margin-top:6px; }

    [data-testid="stPlotlyChart"] { border-radius:12px;overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None

# ── Helpers ───────────────────────────────────────────────────────────────
def get_local_tz():
    try:
        return datetime.now().astimezone().tzinfo
    except:
        return timezone.utc

def fmt_date_local(iso):
    try:
        dt_utc = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        dt_local = dt_utc.astimezone(get_local_tz())
        return dt_local.strftime('%a %d %b · %H:%M')
    except:
        return iso

def get_match_local_date(iso):
    try:
        dt_utc = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        dt_local = dt_utc.astimezone(get_local_tz())
        return dt_local.date()
    except:
        return None

def fmt_stage(stage):
    return {
        'GROUP_STAGE':'Group Stage','LAST_32':'Round of 32','LAST_16':'Round of 16',
        'QUARTER_FINALS':'Quarter Final','SEMI_FINALS':'Semi Final',
        'THIRD_PLACE':'Third Place','FINAL':'Final',
    }.get(stage, stage.replace('_',' ').title())

def form_pills(form_string):
    return ''.join(f'<span class="form-pill-{c}">{c}</span>' for c in form_string)

def stat_box(val, lbl, color='blue'):
    cls = {'blue':'stat-val','green':'stat-val-green','red':'stat-val-red','white':'stat-val-white'}.get(color,'stat-val')
    return f'<div class="stat-box"><div class="{cls}">{val}</div><div class="stat-lbl">{lbl}</div></div>'

def sec_header(title):
    st.markdown(f'<div class="sec-header">{title}</div>', unsafe_allow_html=True)

def hero_badge(home_score, away_score, side):
    if home_score is None or away_score is None: return ''
    win  = (home_score > away_score) if side == 'home' else (away_score > home_score)
    loss = (home_score < away_score) if side == 'home' else (away_score < home_score)
    if win:   return '<span class="hero-badge-w">WIN</span>'
    if loss:  return '<span class="hero-badge-l">LOSS</span>'
    return '<span class="hero-badge-d">DRAW</span>'

def plotly_base_layout(fig, height=300):
    fig.update_layout(
        height=height,
        paper_bgcolor='#0d1526',
        plot_bgcolor='#0d1526',
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        margin=dict(l=16, r=16, t=40, b=24),
        showlegend=False,
    )
    return fig

# ── Chart: Win Probability Donut ───────────────────────────────────────────
def chart_donut(home_team, away_team, p1, pd_, p2):
    c1 = get_team_color(home_team, other_team=away_team)
    c2 = get_team_color(away_team, other_team=home_team)

    fig = go.Figure(go.Pie(
        labels=[home_team, 'Draw', away_team],
        values=[p1, pd_, p2],
        hole=0.62,
        marker=dict(colors=[c1, '#131e30', c2], line=dict(color='#080d18', width=3)),
        textinfo='none',
        hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>',
        direction='clockwise',
        sort=False,
    ))

    winner     = home_team if p1 > p2 else away_team if p2 > p1 else 'Draw'
    winner_pct = max(p1, p2) if winner != 'Draw' else pd_

    fig.add_annotation(text=f'<b>{winner_pct}%</b>', x=0.5, y=0.56,
        font=dict(size=26, color='#ffffff', family='Inter, sans-serif'),
        showarrow=False, xref='paper', yref='paper')
    fig.add_annotation(text=winner, x=0.5, y=0.40,
        font=dict(size=12, color='#3d4f6b', family='Inter, sans-serif'),
        showarrow=False, xref='paper', yref='paper')

    fig.update_layout(height=300, paper_bgcolor='#0d1526', plot_bgcolor='#0d1526',
        margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    return fig

# ── Donut + prob boxes side by side ────────────────────────────────────────
def render_donut_with_boxes(home_team, away_team, p1, pd_, p2):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(chart_donut(home_team, away_team, p1, pd_, p2),
                        use_container_width=True, config={'displayModeBar': False})
    with col2:
        highlight = 'home' if p1 > p2 else 'away'
        items = [
            (home_team, p1, 'home', 'chance of winning'),
            ('Draw',    pd_, None,  'chance of draw'),
            (away_team, p2, 'away', 'chance of winning'),
        ]
        boxes = []
        for label, pct, side, sub in items:
            is_hl     = side == highlight
            hl_class  = 'prob-box highlighted' if is_hl else 'prob-box'
            pct_class = 'prob-box-pct blue' if is_hl else 'prob-box-pct dim'
            boxes.append(
                f'<div class="{hl_class}">'
                f'<div class="prob-box-label">{label}</div>'
                f'<div class="{pct_class}">{pct}%</div>'
                f'<div class="prob-box-sub">{sub}</div>'
                f'</div>'
            )
        st.markdown(
            '<div class="prob-boxes-col">' + ''.join(boxes) + '</div>',
            unsafe_allow_html=True
        )

# ── Chart: Radar — overall team profile ───────────────────────────────────
def chart_radar(home_team, away_team, home_stats, away_stats):
    c1 = get_team_color(home_team, other_team=away_team)
    c2 = get_team_color(away_team, other_team=home_team)

    def form_points_norm(form_str):
        raw = sum(3 if r == 'W' else 1 if r == 'D' else 0 for r in form_str)
        return round(min(raw / 15 * 10, 10), 2)  # normalise to 0–10

    categories = ['Win Rate', 'Goals Scored', 'Goals Conceded\n(inverted)', 'Clean Sheet Rate', 'Recent Form']

    def scores(s):
        return [
            round(s['win_rate'] * 10, 2),
            round(min(s['goals_per_game'] / 3.5 * 10, 10), 2),
            round(max(0, 10 - (s['conceded_per_game'] / 3.5 * 10)), 2),
            round(s['clean_sheet_rate'] * 10, 2),
            form_points_norm(s.get('form_string', '')),
        ]

    h_scores = scores(home_stats)
    a_scores = scores(away_stats)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=h_scores + [h_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=hex_to_rgba(c1, 0.15),
        line=dict(color=c1, width=2),
        name=home_team,
        hovertemplate='<b>' + home_team + '</b><br>%{theta}: %{r:.1f}/10<extra></extra>',
    ))

    fig.add_trace(go.Scatterpolar(
        r=a_scores + [a_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=hex_to_rgba(c2, 0.15),
        line=dict(color=c2, width=2),
        name=away_team,
        hovertemplate='<b>' + away_team + '</b><br>%{theta}: %{r:.1f}/10<extra></extra>',
    ))

    fig.update_layout(
        height=340,
        paper_bgcolor='#0d1526',
        plot_bgcolor='#0d1526',
        polar=dict(
            bgcolor='#080d18',
            radialaxis=dict(
                visible=True, range=[0, 10],
                tickfont=dict(size=8, color='#3d4f6b'),
                gridcolor='#131e30',
                linecolor='#131e30',
                tickvals=[2, 4, 6, 8, 10],
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color='#64748b', family='Inter, sans-serif'),
                gridcolor='#131e30',
                linecolor='#1e2d45',
            ),
        ),
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        margin=dict(l=48, r=48, t=48, b=48),
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5,
            font=dict(size=11, color='#94a3b8'), bgcolor='rgba(0,0,0,0)',
        ),
    )
    return fig


# ── Chart: Horizontal duel bars — head-to-head stat comparison ─────────────
def chart_duel_bars(home_team, away_team, home_stats, away_stats):
    c1 = get_team_color(home_team, other_team=away_team)
    c2 = get_team_color(away_team, other_team=home_team)

    def form_points(form_str):
        return sum(3 if r == 'W' else 1 if r == 'D' else 0 for r in form_str)

    metrics = [
        ('Win Rate',          round(home_stats['win_rate'] * 100, 1),        round(away_stats['win_rate'] * 100, 1),        '%'),
        ('Goals / Game',      round(home_stats['goals_per_game'], 2),         round(away_stats['goals_per_game'], 2),         ''),
        ('Conceded / Game',   round(home_stats['conceded_per_game'], 2),      round(away_stats['conceded_per_game'], 2),      ''),
        ('Clean Sheet Rate',  round(home_stats['clean_sheet_rate'] * 100, 1), round(away_stats['clean_sheet_rate'] * 100, 1), '%'),
        ('Form Points',       form_points(home_stats.get('form_string', '')), form_points(away_stats.get('form_string', '')), '/15'),
        ('GD / Game',         round(home_stats['gd_per_game'], 2),            round(away_stats['gd_per_game'], 2),            ''),
    ]

    labels   = [m[0] for m in metrics]
    h_vals   = [m[1] for m in metrics]
    a_vals   = [m[2] for m in metrics]
    suffixes = [m[3] for m in metrics]

    # For each metric, work out the "share" of the combined total for proportional bars
    # Conceded/Game is inverted — lower is better
    inverted = {'Conceded / Game'}

    fig = go.Figure()

    for i, (label, hv, av, sfx) in enumerate(metrics):
        total = hv + av if (hv + av) > 0 else 1
        h_pct = hv / total * 100
        a_pct = av / total * 100

        # For inverted metrics, flip the advantage colour
        h_better = (hv < av) if label in inverted else (hv >= av)

        fig.add_trace(go.Bar(
            name=home_team,
            x=[h_pct],
            y=[label],
            orientation='h',
            marker_color=hex_to_rgba(c1, 0.85 if h_better else 0.35),
            marker_line=dict(color=c1, width=0),
            showlegend=(i == 0),
            hovertemplate=f'<b>{home_team}</b> · {label}<br>{hv}{sfx}<extra></extra>',
            width=0.5,
        ))

        fig.add_trace(go.Bar(
            name=away_team,
            x=[a_pct],
            y=[label],
            orientation='h',
            marker_color=hex_to_rgba(c2, 0.85 if not h_better else 0.35),
            marker_line=dict(color=c2, width=0),
            showlegend=(i == 0),
            hovertemplate=f'<b>{away_team}</b> · {label}<br>{av}{sfx}<extra></extra>',
            width=0.5,
        ))

    fig.update_layout(
        height=320,
        paper_bgcolor='#0d1526',
        plot_bgcolor='#0d1526',
        barmode='stack',
        xaxis=dict(
            visible=False, range=[-18, 118],
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='#64748b', family='Inter, sans-serif'),
            showgrid=False,
            autorange='reversed',
        ),
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        margin=dict(l=140, r=70, t=36, b=16),
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=1.04, xanchor='center', x=0.5,
            font=dict(size=11, color='#94a3b8'), bgcolor='rgba(0,0,0,0)',
        ),
    )

    for i, (label, hv, av, sfx) in enumerate(metrics):
        fig.add_annotation(
            x=-1, y=label,
            text=f'<b>{hv}{sfx}</b>',
            xanchor='right',
            font=dict(size=10, color=c1, family='Inter, sans-serif'),
            showarrow=False,
        )
        fig.add_annotation(
            x=101, y=label,
            text=f'<b>{av}{sfx}</b>',
            xanchor='left',
            font=dict(size=10, color=c2, family='Inter, sans-serif'),
            showarrow=False,
        )

    return fig


# ── Chart: Goals scored vs conceded grouped bar ────────────────────────────
def chart_goals_bar(home_team, away_team, home_stats, away_stats):
    c1 = get_team_color(home_team, other_team=away_team)
    c2 = get_team_color(away_team, other_team=home_team)

    categories = ['Goals Scored / Game', 'Goals Conceded / Game']
    h_vals = [round(home_stats['goals_per_game'], 2), round(home_stats['conceded_per_game'], 2)]
    a_vals = [round(away_stats['goals_per_game'], 2), round(away_stats['conceded_per_game'], 2)]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=home_team,
        x=categories,
        y=h_vals,
        marker_color=[hex_to_rgba(c1, 0.85), hex_to_rgba(c1, 0.4)],
        marker_line=dict(color=c1, width=1),
        hovertemplate='<b>' + home_team + '</b><br>%{x}: %{y}<extra></extra>',
        width=0.3,
    ))

    fig.add_trace(go.Bar(
        name=away_team,
        x=categories,
        y=a_vals,
        marker_color=[hex_to_rgba(c2, 0.85), hex_to_rgba(c2, 0.4)],
        marker_line=dict(color=c2, width=1),
        hovertemplate='<b>' + away_team + '</b><br>%{x}: %{y}<extra></extra>',
        width=0.3,
    ))

    # Subtle reference line at 1.2 (average WC goals/game)
    fig.add_hline(
        y=1.2, line_dash='dot', line_color='#1e2d45', line_width=1,
        annotation_text='WC avg', annotation_font_size=9,
        annotation_font_color='#3d4f6b', annotation_position='top right',
    )

    fig.update_layout(
        height=280,
        paper_bgcolor='#0d1526',
        plot_bgcolor='#0d1526',
        barmode='group',
        xaxis=dict(
            tickfont=dict(size=10, color='#64748b', family='Inter, sans-serif'),
            showgrid=False,
        ),
        yaxis=dict(
            tickfont=dict(size=9, color='#3d4f6b'),
            showgrid=True, gridcolor='#0f1626',
            zeroline=False,
        ),
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        margin=dict(l=32, r=16, t=36, b=16),
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=1.04, xanchor='center', x=0.5,
            font=dict(size=11, color='#94a3b8'), bgcolor='rgba(0,0,0,0)',
        ),
    )
    return fig


# ── Render all 3 stat charts with headers ─────────────────────────────────
def chart_stats_comparison(home_team, away_team, home_stats, away_stats):
    """
    Renders three distinct visualisations:
      1. Radar — overall team profile across 5 dimensions
      2. Horizontal duel bars — proportional head-to-head on 6 metrics
      3. Grouped bar — goals scored vs conceded side by side
    Called from show_finished_match and show_upcoming_match.
    Returns nothing — renders directly via st.
    """
    c1 = get_team_color(home_team, other_team=away_team)
    c2 = get_team_color(away_team, other_team=home_team)

    # ── Row 1: Radar + Duel bars side by side ──────────────────────────────
    col_r, col_d = st.columns([1, 1])

    with col_r:
        st.markdown(f"""
        <div style="margin-bottom:4px">
            <span style="font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b">Team Profile Radar</span><br>
            <span style="font-size:0.72rem;color:#2a3a52">Normalised 0–10 across 5 dimensions</span>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(chart_radar(home_team, away_team, home_stats, away_stats),
                        use_container_width=True, config={'displayModeBar': False})

    with col_d:
        st.markdown(f"""
        <div style="margin-bottom:4px">
            <span style="font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b">Head-to-Head Metrics</span><br>
            <span style="font-size:0.72rem;color:#2a3a52">Brighter bar = stronger side · conceded is inverted</span>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(chart_duel_bars(home_team, away_team, home_stats, away_stats),
                        use_container_width=True, config={'displayModeBar': False})

    # ── Row 2: Goals bar full width ────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:8px;margin-bottom:4px">
        <span style="font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b">Goals Scored vs Conceded</span><br>
        <span style="font-size:0.72rem;color:#2a3a52">Per game average · solid = scored, faded = conceded · dotted line = World Cup average (1.2)</span>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(chart_goals_bar(home_team, away_team, home_stats, away_stats),
                    use_container_width=True, config={'displayModeBar': False})

# ── Chart: Score Probability Heatmap ──────────────────────────────────────
def chart_score_heatmap(home_team, away_team, score_dist, actual_score=None):
    c1 = get_team_color(home_team, other_team=away_team)
    h  = c1.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    max_goals = 5
    z, text = [], []
    for away_g in range(max_goals + 1):
        row_z, row_t = [], []
        for home_g in range(max_goals + 1):
            val = score_dist.get(f'{home_g}-{away_g}', 0.0)
            row_z.append(val)
            row_t.append(f'{val:.1f}%')
        z.append(row_z)
        text.append(row_t)

    colorscale = [
        [0.0, 'rgba(8,13,24,1)'],
        [0.3, f'rgba({r},{g},{b},0.2)'],
        [0.6, f'rgba({r},{g},{b},0.55)'],
        [1.0, f'rgba({r},{g},{b},1)'],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(i) for i in range(max_goals + 1)],
        y=[str(i) for i in range(max_goals + 1)],
        text=text,
        texttemplate='%{text}',
        textfont=dict(size=10, color='#ffffff'),
        colorscale=colorscale,
        showscale=False,
        hovertemplate=f'{home_team} %{{x}} – %{{y}} {away_team}<br>Probability: %{{z:.1f}}%<extra></extra>',
        xgap=4, ygap=4,
    ))

    if actual_score and '-' in actual_score:
        try:
            hg, ag = int(actual_score.split('-')[0]), int(actual_score.split('-')[1])
            if hg <= max_goals and ag <= max_goals:
                fig.add_shape(type='rect',
                    x0=hg-0.5, x1=hg+0.5, y0=ag-0.5, y1=ag+0.5,
                    line=dict(color='#4ade80', width=2),
                    fillcolor='rgba(0,0,0,0)')
                fig.add_annotation(x=hg, y=ag, text='✓',
                    font=dict(size=16, color='#4ade80'),
                    showarrow=False, yshift=14)
        except:
            pass

    fig.update_layout(
        xaxis=dict(title=dict(text=home_team, font=dict(size=11, color='#94a3b8')), side='bottom'),
        yaxis=dict(title=dict(text=away_team, font=dict(size=11, color='#94a3b8')), autorange='reversed'),
        height=420, paper_bgcolor='#0d1526', plot_bgcolor='#0d1526',
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        margin=dict(l=48, r=16, t=32, b=48),
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color='#3d4f6b', size=10))
    fig.update_yaxes(showgrid=False, tickfont=dict(color='#3d4f6b', size=10))
    return fig

# ── Key Factors ────────────────────────────────────────────────────────────
def render_key_factors(home_team, away_team, home_stats, away_stats, nlu, sim):
    sec_header("Why the Model Predicted This")
    factors = []

    h_score = nlu['team1']['score']
    a_score = nlu['team2']['score']
    nlu_diff = h_score - a_score
    if abs(nlu_diff) > 0.15:
        better = home_team if nlu_diff > 0 else away_team
        badge_cls = 'kf-badge-pos' if nlu_diff > 0 else 'kf-badge-neg'
        adj = abs(nlu_diff) * 5
        factors.append({'icon':'','label':'Form Sentiment (Watson NLU)',
            'text': f'<strong>{better}</strong> entered this match in measurably better form. NLU sentiment gap of <strong>{abs(nlu_diff):.2f}</strong> translated to a <strong>~{adj:.1f}%</strong> boost in their projected attacking output.',
            'badge': f'<span class="{badge_cls}">{better} advantage</span>'})

    h_cs, a_cs = home_stats['clean_sheet_rate'], away_stats['clean_sheet_rate']
    if abs(h_cs - a_cs) > 0.1:
        stronger_def = home_team if h_cs > a_cs else away_team
        factors.append({'icon':'','label':'Defensive Strength',
            'text': f'<strong>{stronger_def}</strong> kept clean sheets in <strong>{max(h_cs,a_cs)*100:.0f}%</strong> of recent games vs <strong>{min(h_cs,a_cs)*100:.0f}%</strong> — suppressing the opponent\'s expected goals in the simulation.',
            'badge': f'<span class="kf-badge-pos">{stronger_def} tighter defense</span>'})

    h_gpg, a_gpg = home_stats['goals_per_game'], away_stats['goals_per_game']
    if abs(h_gpg - a_gpg) > 0.3:
        sharper = home_team if h_gpg > a_gpg else away_team
        factors.append({'icon':'','label':'Attacking Output',
            'text': f'<strong>{sharper}</strong> averaged <strong>{max(h_gpg,a_gpg):.1f} goals/game</strong> in recent form vs <strong>{min(h_gpg,a_gpg):.1f}</strong> — raising their base xG in the model.',
            'badge': f'<span class="kf-badge-pos">{sharper} more clinical</span>'})

    h_gd, a_gd = home_stats['gd_per_game'], away_stats['gd_per_game']
    if abs(h_gd - a_gd) > 0.5:
        dominant = home_team if h_gd > a_gd else away_team
        factors.append({'icon':'','label':'Goal Difference Per Game',
            'text': f'<strong>{dominant}</strong> carried a GD of <strong>{max(h_gd,a_gd):+.2f} per game</strong>. Teams with sustained positive GD tend to outperform raw scoring — the model applies a small multiplier for this.',
            'badge': f'<span class="kf-badge-pos">{dominant} dominant</span>'})

    h_wr, a_wr = home_stats['win_rate'], away_stats['win_rate']
    if abs(h_wr - a_wr) > 0.15:
        consistent = home_team if h_wr > a_wr else away_team
        factors.append({'icon':'','label':'Win Rate',
            'text': f'<strong>{consistent}</strong> won <strong>{max(h_wr,a_wr)*100:.0f}%</strong> of recent games vs their opponent\'s <strong>{min(h_wr,a_wr)*100:.0f}%</strong>. The model treats consistent winners as slightly more likely to convert chances.',
            'badge': f'<span class="kf-badge-pos">{consistent} more consistent</span>'})

    if not factors:
        factors.append({'icon':'','label':'Evenly Matched',
            'text':'Both teams came in with comparable form, defensive solidity, and attacking output. The model found no dominant statistical edge — a genuinely open match.',
            'badge':'<span class="kf-badge-neu">No clear edge</span>'})

    rows_html = ''.join(f'''
    <div class="kf-row">
        <div class="kf-icon">{f["icon"]}</div>
        <div>
            <div class="kf-label">{f["label"]} {f["badge"]}</div>
            <div class="kf-text">{f["text"]}</div>
        </div>
    </div>''' for f in factors[:4])

    st.markdown(f'<div class="key-factors">{rows_html}</div>', unsafe_allow_html=True)

# ── NLU cards ─────────────────────────────────────────────────────────────
def render_nlu_cards(home_team, away_team, nlu):
    col1, col2 = st.columns(2)
    for col, team_name, nlu_data in [(col1, home_team, nlu['team1']), (col2, away_team, nlu['team2'])]:
        with col:
            score    = nlu_data['score']
            fill_pct = int((score + 1) / 2 * 100)
            color    = '#4ade80' if score > 0.2 else '#f87171' if score < -0.2 else '#94a3b8'
            sent_desc = (
                "Strong momentum coming in" if score > 0.5 else
                "Positive form heading into the match" if score > 0.2 else
                "Neutral — could go either way" if score > -0.2 else
                "Struggling for form going in" if score > -0.5 else
                "Very poor run of form coming in"
            )
            st.markdown(f"""
            <div class="nlu-card">
                <div class="nlu-team-name">{team_name}</div>
                <div class="nlu-sentiment-label">{sent_desc}</div>
                <div class="nlu-bar-bg"><div style="width:{fill_pct}%;background:{color};height:6px;border-radius:6px"></div></div>
                <div class="nlu-score-row">
                    <span class="nlu-score-label">Negative</span>
                    <span class="nlu-score-val" style="color:{color}">{nlu_data['label']} &nbsp;{score:+.2f}</span>
                    <span class="nlu-score-label">Positive</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Form blocks ────────────────────────────────────────────────────────────
def render_form_blocks(home_team, away_team, hs, aws):
    col1, col2 = st.columns(2)
    for col, team, stats in [(col1, home_team, hs), (col2, away_team, aws)]:
        with col:
            wr_color = '#4ade80' if stats.get('win_rate',0) >= 0.5 else '#f87171' if stats.get('win_rate',0) < 0.25 else '#94a3b8'
            st.markdown(f"""
            <div class="form-block">
                <div class="form-team-name">{team}</div>
                <div style="margin-bottom:8px">{form_pills(stats['form_string'])}</div>
                <div class="form-stats-row">
                    <span style="color:{wr_color};font-weight:700">{stats['wins']}W {stats['draws']}D {stats['losses']}L</span>
                    &nbsp;·&nbsp; {stats['played']} games<br>
                    Clean sheet rate: <strong style="color:#e2e8f0">{stats['clean_sheet_rate']*100:.0f}%</strong>
                    &nbsp;·&nbsp; GD/game: <strong style="color:{'#4ade80' if stats['gd_per_game']>=0 else '#f87171'}">{stats['gd_per_game']:+.2f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── HOME PAGE ──────────────────────────────────────────────────────────────
def show_home():
    # CSS background animation
    st.markdown("""
    <style>
        /* Orb container fixed behind everything */
        .ballr-bg {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .ballr-orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.07;
            animation: orb-drift linear infinite;
        }
        .ballr-orb-1 {
            width: 520px; height: 520px;
            background: #1a4a8a;
            top: -120px; left: -80px;
            animation-duration: 28s;
            animation-delay: 0s;
        }
        .ballr-orb-2 {
            width: 380px; height: 380px;
            background: #0a2a5e;
            top: 40%; right: -60px;
            animation-duration: 22s;
            animation-delay: -8s;
        }
        .ballr-orb-3 {
            width: 300px; height: 300px;
            background: #0d3470;
            bottom: -80px; left: 35%;
            animation-duration: 34s;
            animation-delay: -14s;
        }
        .ballr-orb-4 {
            width: 200px; height: 200px;
            background: #4a9eff;
            top: 30%; left: 25%;
            animation-duration: 18s;
            animation-delay: -5s;
            opacity: 0.04;
        }
        /* Star dots — pure CSS, no JS */
        .ballr-stars {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image:
                radial-gradient(1px 1px at 12% 18%, rgba(74,158,255,0.35) 0%, transparent 100%),
                radial-gradient(1px 1px at 28% 72%, rgba(74,158,255,0.25) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 44% 11%, rgba(74,158,255,0.4) 0%, transparent 100%),
                radial-gradient(1px 1px at 67% 55%, rgba(74,158,255,0.3) 0%, transparent 100%),
                radial-gradient(1px 1px at 81% 29%, rgba(74,158,255,0.2) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 91% 78%, rgba(74,158,255,0.35) 0%, transparent 100%),
                radial-gradient(1px 1px at 55% 88%, rgba(74,158,255,0.25) 0%, transparent 100%),
                radial-gradient(1px 1px at 7%  61%, rgba(74,158,255,0.2) 0%, transparent 100%),
                radial-gradient(1px 1px at 38% 43%, rgba(74,158,255,0.15) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 74% 8%,  rgba(74,158,255,0.35) 0%, transparent 100%),
                radial-gradient(1px 1px at 19% 91%, rgba(74,158,255,0.2) 0%, transparent 100%),
                radial-gradient(1px 1px at 62% 34%, rgba(74,158,255,0.25) 0%, transparent 100%),
                radial-gradient(1px 1px at 88% 50%, rgba(74,158,255,0.15) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 33% 25%, rgba(74,158,255,0.3) 0%, transparent 100%),
                radial-gradient(1px 1px at 50% 65%, rgba(74,158,255,0.2) 0%, transparent 100%),
                radial-gradient(1px 1px at 77% 82%, rgba(74,158,255,0.25) 0%, transparent 100%),
                radial-gradient(1px 1px at 4%  38%, rgba(74,158,255,0.2) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 96% 14%, rgba(74,158,255,0.3) 0%, transparent 100%),
                radial-gradient(1px 1px at 15% 50%, rgba(74,158,255,0.15) 0%, transparent 100%),
                radial-gradient(1px 1px at 85% 95%, rgba(74,158,255,0.2) 0%, transparent 100%);
            animation: stars-twinkle 6s ease-in-out infinite alternate;
        }
        @keyframes orb-drift {
            0%   { transform: translate(0px, 0px) scale(1); }
            25%  { transform: translate(30px, -20px) scale(1.04); }
            50%  { transform: translate(15px, 35px) scale(0.97); }
            75%  { transform: translate(-25px, 10px) scale(1.02); }
            100% { transform: translate(0px, 0px) scale(1); }
        }
        @keyframes stars-twinkle {
            0%   { opacity: 0.6; }
            100% { opacity: 1.0; }
        }
    </style>
    <div class="ballr-bg">
        <div class="ballr-stars"></div>
        <div class="ballr-orb ballr-orb-1"></div>
        <div class="ballr-orb ballr-orb-2"></div>
        <div class="ballr-orb ballr-orb-3"></div>
        <div class="ballr-orb ballr-orb-4"></div>
    </div>
    """, unsafe_allow_html=True)

    import os
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=64)
    with col_title:
        st.markdown('<div style="padding-top:6px"><div class="ballr-title">Ballr</div><div class="ballr-sub">2026 FIFA World Cup · AI Match Predictor</div></div>', unsafe_allow_html=True)

    with st.spinner(""):
        try:
            r = requests.get(f"{BACKEND}/fixtures", timeout=10)
            fixtures = r.json()
        except:
            st.error("Can't reach backend. Is Flask running?")
            return

    fixtures = [f for f in fixtures if f['home'] and f['away']]
    today = date.today()
    knockout_stages = {'LAST_32','LAST_16','QUARTER_FINALS','SEMI_FINALS','THIRD_PLACE','FINAL'}

    def render_grid(matches, tab_key):
        if not matches:
            st.markdown('<div class="empty-state"><div class="empty-icon">📅</div>No matches found.</div>', unsafe_allow_html=True)
            return
        cols = st.columns(3)
        for i, m in enumerate(matches):
            with cols[i % 3]:
                finished = m['status'] == 'FINISHED'
                live     = m['status'] in ('IN_PLAY','PAUSED')
                tc       = get_team_color(m['home'], other_team=m['away'])
                accent   = hex_to_rgba(tc, 0.35)

                if finished:
                    hs, aws = m['home_score'], m['away_score']
                    home_cls = 'card-winner' if hs > aws else 'card-loser' if hs < aws else ''
                    away_cls = 'card-winner' if aws > hs else 'card-loser' if aws < hs else ''
                    score_html = f'<div class="card-score-nums"><span class="card-score-num">{hs}</span><span class="card-score-sep">–</span><span class="card-score-num">{aws}</span></div>'
                    badge = '<span class="badge-ft">FT</span>'
                elif live:
                    home_cls = away_cls = ''
                    score_html = '<div class="card-vs" style="color:#4ade80">LIVE</div>'
                    badge = '<span class="badge-live">● LIVE</span>'
                else:
                    home_cls = away_cls = ''
                    score_html = '<div class="card-vs">VS</div>'
                    badge = '<span class="badge-upcoming">Upcoming</span>'

                st.markdown(f"""
                <div class="match-card" style="border-left:3px solid {accent}">
                    <div class="card-comp">{fmt_stage(m['stage'])}</div>
                    <div class="card-body">
                        <div class="card-team-home {home_cls}">{m['home']}</div>
                        <div class="card-score-block">{score_html}</div>
                        <div class="card-team-away {away_cls}">{m['away']}</div>
                    </div>
                    <div class="card-footer">
                        <span class="card-time">{fmt_date_local(m['date'])}</span>
                        {badge}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("View match →", key=f"btn_{tab_key}_{m['id']}_{i}", use_container_width=True):
                    st.session_state.selected_match = m
                    st.session_state.page = 'match'
                    st.rerun()

    tab_today, tab_all, tab_group, tab_knockout = st.tabs([" Today","  All Matches","  Group Stage","  Knockout"])

    with tab_today:
        today_matches = [f for f in fixtures if get_match_local_date(f['date']) == today]
        if today_matches:
            render_grid(today_matches, "today")
        else:
            upcoming = [f for f in fixtures if f['status'] != 'FINISHED']
            if upcoming:
                nearest = min((get_match_local_date(f['date']) for f in upcoming if get_match_local_date(f['date'])), default=None)
                near_matches = [f for f in upcoming if get_match_local_date(f['date']) == nearest]
                st.markdown(f"<div style='color:#3d4f6b;font-size:0.78rem;margin-bottom:16px'>No matches today — next matchday: {nearest.strftime('%a %d %b') if nearest else ''}</div>", unsafe_allow_html=True)
                render_grid(near_matches, "today")
            else:
                render_grid([], "today")

    with tab_all:
        by_date = {}
        for f in fixtures:
            d = get_match_local_date(f['date'])
            if d: by_date.setdefault(d, []).append(f)
        for d in sorted(by_date.keys()):
            is_today = d == today
            label_cls = 'date-group-today' if is_today else ''
            st.markdown(f'<div class="date-group {label_cls}">{"Today · " if is_today else ""}{d.strftime("%A %d %B")}</div>', unsafe_allow_html=True)
            render_grid(by_date[d], f"all_{d}")

    with tab_group:
        render_grid([f for f in fixtures if f['stage'] == 'GROUP_STAGE'], "group")

    with tab_knockout:
        ko = [f for f in fixtures if f['stage'] in knockout_stages]
        if ko:
            by_stage = {}
            for f in ko: by_stage.setdefault(fmt_stage(f['stage']), []).append(f)
            for s, ms in by_stage.items():
                st.markdown(f'<div class="date-group">{s}</div>', unsafe_allow_html=True)
                render_grid(ms, f"ko_{s}")
        else:
            render_grid([], "knockout")

# ── FINISHED MATCH ─────────────────────────────────────────────────────────
def show_finished_match(m, data):
    sim    = data['simulation']
    nlu    = data['nlu']
    hs     = data['home_stats']
    aws    = data['away_stats']
    events = data.get('events') or {}

    home_score   = m['home_score']
    away_score   = m['away_score']
    winner       = m['home'] if home_score > away_score else m['away'] if away_score > home_score else None
    result_text  = f"{winner} won" if winner else "Match drawn"
    venue        = events.get('venue', '')
    stage_label  = events.get('stage', fmt_stage(m['stage']))
    actual_score = f"{home_score}-{away_score}"

    c1_color = get_team_color(m['home'], other_team=m['away'])
    hs_color = '#4ade80' if home_score > away_score else '#f87171' if home_score < away_score else '#ffffff'
    as_color = '#4ade80' if away_score > home_score else '#f87171' if away_score < home_score else '#ffffff'

    st.markdown(f"""
    <div class="match-hero" style="border-top:3px solid {c1_color}">
        <div class="hero-meta">{stage_label}{f' · {venue}' if venue else ''} · {fmt_date_local(m['date'])}</div>
        <div class="hero-teams">{m['home']} <span class="hero-vs">vs</span> {m['away']}</div>
        <div class="hero-score">
            <span style="color:{hs_color}">{home_score}</span>
            <span class="hero-score-sep"> – </span>
            <span style="color:{as_color}">{away_score}</span>
        </div>
        <div class="hero-badges">
            {hero_badge(home_score, away_score, 'home')}
            <span class="hero-result">{result_text}</span>
            {hero_badge(home_score, away_score, 'away')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    home_ev    = events.get(m['home'], {})
    away_ev    = events.get(m['away'], {})
    home_goals = home_ev.get('goals', [])
    away_goals = away_ev.get('goals', [])
    home_reds  = home_ev.get('red_cards', [])
    away_reds  = away_ev.get('red_cards', [])
    c2_color   = get_team_color(m['away'], other_team=m['home'])

    if home_goals or away_goals or home_reds or away_reds:
        sec_header("Goal Scorers & Key Events")
        col1, col2 = st.columns(2)

        def render_scorers(col, team_name, goals, reds):
            with col:
                st.markdown(f'<div style="font-size:0.78rem;font-weight:700;color:#3d4f6b;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px">{team_name}</div>', unsafe_allow_html=True)
                if not goals and not reds:
                    st.markdown('<div class="no-goals">No goals</div>', unsafe_allow_html=True)
                for g in goals:
                    st.markdown(f'<div class="goal-row"><span class="goal-minute">{g["minute"]}\'</span><span>⚽</span><span class="goal-player">{g["player"]}</span></div>', unsafe_allow_html=True)
                for r in reds:
                    st.markdown(f'<div class="goal-row"><span class="red-minute">{r["minute"]}\'</span><span>🟥</span><span class="goal-player" style="color:#f87171">{r["player"]}</span></div>', unsafe_allow_html=True)

        render_scorers(col1, m['home'], home_goals, home_reds)
        render_scorers(col2, m['away'], away_goals, away_reds)

        all_ev = []
        for g in home_goals: all_ev.append({'m': g['minute'] or 0, 'team':'home', 'type':'goal', 'p': g['player']})
        for g in away_goals: all_ev.append({'m': g['minute'] or 0, 'team':'away', 'type':'goal', 'p': g['player']})
        for r in home_reds:  all_ev.append({'m': r['minute'] or 0, 'team':'home', 'type':'red',  'p': r['player']})
        for r in away_reds:  all_ev.append({'m': r['minute'] or 0, 'team':'away', 'type':'red',  'p': r['player']})
        all_ev.sort(key=lambda x: x['m'])

        dots = ''
        for ev in all_ev:
            pct = min(ev['m'] / 95 * 100, 97)
            if ev['type'] == 'goal':
                color = c1_color if ev['team'] == 'home' else c2_color
                top   = '6px' if ev['team'] == 'home' else '22px'
                dots += '<div title="{} {}\'" style="position:absolute;left:{}%;top:{};width:10px;height:10px;background:{};border-radius:50%;transform:translateX(-50%);box-shadow:0 0 6px {}66"></div>'.format(ev['p'], ev['m'], pct, top, color, color)
            else:
                dots += '<div title="{} {} {}\'" style="position:absolute;left:{}%;top:12px;width:3px;height:16px;background:#f87171;transform:translateX(-50%)"></div>'.format(ev['p'], '🟥', ev['m'], pct)

        st.markdown(f"""
        <div class="timeline-wrap">
            <div style="font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3d4f6b;margin-bottom:6px">Match Timeline</div>
            <div style="display:flex;gap:16px;font-size:0.68rem;color:#3d4f6b;margin-bottom:8px">
                <span>● <span style="color:{c1_color}">{m['home']}</span></span>
                <span>● <span style="color:{c2_color}">{m['away']}</span></span>
                <span style="color:#f87171">| Red card</span>
            </div>
            <div class="timeline-bar">
                <div style="position:absolute;left:47.4%;top:0;bottom:0;width:1px;background:#131e30"></div>
                {dots}
            </div>
            <div class="timeline-labels"><span>0'</span><span>HT</span><span>90'</span></div>
        </div>
        """, unsafe_allow_html=True)

        if home_goals or away_goals:
            ht_h = len([g for g in home_goals if (g['minute'] or 0) <= 45])
            ht_a = len([g for g in away_goals if (g['minute'] or 0) <= 45])
            sh_h = home_score - ht_h
            sh_a = away_score - ht_a
            first = sorted(home_goals + away_goals, key=lambda x: x['minute'] or 999)
            sec_header("First Half vs Second Half")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(stat_box(f"{ht_h}–{ht_a}", "Half Time"), unsafe_allow_html=True)
            with c2: st.markdown(stat_box(f"{sh_h}–{sh_a}", "Second Half"), unsafe_allow_html=True)
            with c3: st.markdown(stat_box("1st Half" if (ht_h+ht_a) >= (sh_h+sh_a) else "2nd Half", "Most Goals"), unsafe_allow_html=True)
            with c4:
                if first:
                    st.markdown(stat_box(f"{first[0]['minute']}'", f"First Goal · {first[0]['player']}"), unsafe_allow_html=True)

    sec_header("Form & Statistical Comparison")
    chart_stats_comparison(m['home'], m['away'], hs, aws)
    render_form_blocks(m['home'], m['away'], hs, aws)

    sec_header("Watson NLU · Pre-Match Form Sentiment")
    st.markdown('<div class="nlu-explainer"><strong style="color:#e2e8f0">How does this work?</strong> IBM Watson NLU read a plain-English summary of each team\'s recent results and scored the emotional tone — positive means momentum and confidence, negative means a difficult run. This score directly adjusted each team\'s attacking strength in our simulation.</div>', unsafe_allow_html=True)
    render_nlu_cards(m['home'], m['away'], nlu)

    render_key_factors(m['home'], m['away'], hs, aws, nlu, sim)

    sec_header("What Our AI Predicted Before Kick-Off")
    p1, pd_, p2  = sim['team1_win_pct'], sim['draw_pct'], sim['team2_win_pct']
    predicted_winner = (
        m['home'] if p1 > p2 and p1 > pd_
        else m['away'] if p2 > p1 and p2 > pd_
        else "a draw"
    )
    was_correct   = (predicted_winner == winner) or (predicted_winner == "a draw" and winner is None)
    acc_color     = '#4ade80' if was_correct else '#f87171'
    acc_text      = '✅ Correct prediction' if was_correct else '❌ Incorrect prediction'
    top_pred      = sim['top_scores'][0][0] if sim['top_scores'] else '—'
    score_correct = top_pred == actual_score

    st.markdown(f"""
    <div class="insight-box">
        Watson NLU rated <strong>{m['home']}</strong> at <strong style="color:{'#4ade80' if nlu['team1']['score']>0 else '#f87171'}">{nlu['team1']['score']:+.2f}</strong>
        and <strong>{m['away']}</strong> at <strong style="color:{'#4ade80' if nlu['team2']['score']>0 else '#f87171'}">{nlu['team2']['score']:+.2f}</strong>.
        Across 50,000 Monte Carlo simulations the model gave <strong>{m['home']}</strong> a <strong>{p1}% win chance</strong>,
        <strong>{m['away']}</strong> <strong>{p2}%</strong>, draw <strong>{pd_}%</strong>.
        Most likely score predicted: <strong>{top_pred}</strong>. Actual: <strong>{actual_score}</strong>.
        &nbsp;<span style="color:{acc_color};font-weight:700">{acc_text}</span>
        {'&nbsp;·&nbsp;<span style="color:#4ade80;font-weight:700">✅ Exact score predicted</span>' if score_correct else ''}
    </div>
    """, unsafe_allow_html=True)

    render_donut_with_boxes(m['home'], m['away'], p1, pd_, p2)

    sec_header("Score Probability Heatmap")
    st.markdown('<div class="heatmap-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.plotly_chart(chart_score_heatmap(m['home'], m['away'], sim.get('score_dist', {}), actual_score),
                        use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#3d4f6b;line-height:1.8">
            Each cell = probability of that exact scoreline across 50,000 simulations.<br><br>
            <span style="color:#e2e8f0;font-weight:700">Columns</span> = {m['home']} goals<br>
            <span style="color:#e2e8f0;font-weight:700">Rows</span> = {m['away']} goals<br><br>
            Brighter = more likely.<br><br>
            {'<span style="color:#4ade80;font-weight:700">✓ Green border = actual result</span>' if actual_score else ''}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── UPCOMING MATCH ─────────────────────────────────────────────────────────
def show_upcoming_match(m, data):
    sim = data['simulation']
    nlu = data['nlu']
    hs  = data['home_stats']
    aws = data['away_stats']

    c1_color = get_team_color(m['home'], other_team=m['away'])
    c2_color = get_team_color(m['away'], other_team=m['home'])
    p1, pd_, p2 = sim['team1_win_pct'], sim['draw_pct'], sim['team2_win_pct']
    xg1, xg2   = sim['team1_xg'], sim['team2_xg']

    st.markdown(f"""
    <div class="match-hero" style="border-top:3px solid {c1_color}">
        <div class="hero-meta">{fmt_stage(m['stage'])} · {fmt_date_local(m['date'])}</div>
        <div class="hero-teams">{m['home']} <span class="hero-vs">vs</span> {m['away']}</div>
    </div>
    """, unsafe_allow_html=True)

    sec_header("Win Probability · 50,000 Simulations")
    render_donut_with_boxes(m['home'], m['away'], p1, pd_, p2)

    sec_header("Expected Goals (xG)")
    col1, col2 = st.columns(2)
    with col1: st.markdown(stat_box(xg1, f"{m['home']} xG"), unsafe_allow_html=True)
    with col2: st.markdown(stat_box(xg2, f"{m['away']} xG"), unsafe_allow_html=True)
    total_xg = xg1 + xg2 if (xg1 + xg2) > 0 else 1
    st.markdown(f"""
    <div style="display:flex;border-radius:6px;overflow:hidden;height:6px;margin:8px 0 4px 0">
        <div style="width:{xg1/total_xg*100}%;background:{c1_color}"></div>
        <div style="width:{xg2/total_xg*100}%;background:{c2_color}"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#3d4f6b;margin-bottom:8px">
        <span>{m['home']}</span><span>{m['away']}</span>
    </div>
    """, unsafe_allow_html=True)

    sec_header("Score Probability Heatmap")
    st.markdown('<div class="heatmap-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.plotly_chart(chart_score_heatmap(m['home'], m['away'], sim.get('score_dist', {})),
                        use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#3d4f6b;line-height:1.8">
            Each cell = probability of that exact scoreline across 50,000 simulations.<br><br>
            <span style="color:#e2e8f0;font-weight:700">Columns</span> = {m['home']} goals<br>
            <span style="color:#e2e8f0;font-weight:700">Rows</span> = {m['away']} goals<br><br>
            Brighter = more likely.
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sec_header("Form & Statistical Comparison")
    chart_stats_comparison(m['home'], m['away'], hs, aws)
    render_form_blocks(m['home'], m['away'], hs, aws)

    sec_header("Watson NLU · Form Sentiment Analysis")
    st.markdown('<div class="nlu-explainer"><strong style="color:#e2e8f0">How does this work?</strong> IBM Watson NLU analysed each team\'s recent run of results and scored how positive or negative their form looks. A positive score boosts the team\'s predicted attacking output in our simulation — a negative score reduces it.</div>', unsafe_allow_html=True)
    render_nlu_cards(m['home'], m['away'], nlu)

    render_key_factors(m['home'], m['away'], hs, aws, nlu, sim)

    sec_header("AI Insight")
    stronger     = m['home'] if p1 > p2 else m['away']
    stronger_pct = max(p1, p2)
    st.markdown(f"""
    <div class="insight-box">
        Watson NLU read <strong>{m['home']}</strong>'s recent form as
        <strong style="color:{'#4ade80' if nlu['team1']['score']>0 else '#f87171'}">{nlu['team1']['label'].lower()}</strong> ({nlu['team1']['score']:+.2f})
        and <strong>{m['away']}</strong>'s as
        <strong style="color:{'#4ade80' if nlu['team2']['score']>0 else '#f87171'}">{nlu['team2']['label'].lower()}</strong> ({nlu['team2']['score']:+.2f}).
        Across 50,000 simulations, <strong>{stronger}</strong> came out on top in <strong>{stronger_pct}%</strong> of scenarios
        with an expected <strong>{xg1} – {xg2}</strong> scoreline.
        Most likely result: <strong>{sim['top_scores'][0][0]}</strong> ({sim['top_scores'][0][1]}% of simulations).
    </div>
    """, unsafe_allow_html=True)

# ── MATCH ROUTER ───────────────────────────────────────────────────────────
def show_match():
    m = st.session_state.selected_match
    if not m:
        st.session_state.page = 'home'
        st.rerun()

    if st.button("← Back to fixtures"):
        st.session_state.page = 'home'
        st.rerun()

    with st.spinner("Loading match data..."):
        try:
            r = requests.get(f"{BACKEND}/match/{m['home_id']}/{m['away_id']}", timeout=20)
            data = r.json()
        except:
            st.error("Failed to load match data.")
            return

    if m['status'] == 'FINISHED':
        show_finished_match(m, data)
    else:
        show_upcoming_match(m, data)

# ── ROUTER ─────────────────────────────────────────────────────────────────
if st.session_state.page == 'home':
    show_home()
elif st.session_state.page == 'match':
    show_match()