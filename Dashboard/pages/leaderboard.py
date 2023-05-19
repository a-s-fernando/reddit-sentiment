from dash import register_page, html

register_page(__name__, title="Leaderboard", path='/Leaderboard')

layout = html.Div([
    html.H3('Leaderboard')
])
