import dash
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path='/', name='Main',order=1)

base = pd.read_csv('/data/french_youtube_10_12_23.csv')
base['nbview'] = base['exactViewNumber'].str.extract(
    '([\d|,]+)').replace('\D+', '', regex=True).astype('int')
base['nblikes'] = base['numberLikes'].replace(
    '\D+', '000', regex=True).astype('int')

popular = base.sort_values('nbview', ascending=False).head(5)[[
    'videoTitle',
    'videoThumbnailUrl',
    'nbview',
    'nblikes',
    'videoCreatorName']]
popular['rank'] = [k for k in range(popular.shape[0])]
popular = popular.set_index('rank')


def draw_rank(k):
    row = dbc.Row([
        dbc.Col([
            html.Img(
                src=popular.loc[k, 'videoThumbnailUrl'],
                style={'height': '6em', 'width': '9em'})
        ], width=2),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H3('#{}'.format(k+1), style={'color': '#6D071A'}),
                    html.H6(popular.loc[k, 'videoTitle'])
                ]), style={'height': '6rem'}
            )
        ], width=6),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(
                                'Creator',
                                style={'color': '#6D071A'})], width=4),
                        dbc.Col([
                            html.H6(popular.loc[k, 'videoCreatorName'])])]),
                    dbc.Row([
                        dbc.Col([
                            html.H6(
                                'Views',
                                style={'color': '#6D071A'})], width=4),
                        dbc.Col([html.H6(popular.loc[k, 'nbview'])])]),
                    dbc.Row([
                        dbc.Col([
                            html.H6(
                                'Likes',
                                style={'color': '#6D071A'})], width=4),
                        dbc.Col([html.H6(popular.loc[k, 'nblikes'])])])
                ]), style={'height': '6rem'}
            )
        ])
    ], style={"padding-top": "1rem", "padding-bottom": "1rem"})
    return row


layout = html.Div([
    dbc.Row([
        html.H3(
            "Popular videos at the moment",
            style={'textAlign': 'center', 'color': '#6D071A'})
    ], style={'padding-top': '1rem'}),
    draw_rank(0),
    draw_rank(1),
    draw_rank(2),
    draw_rank(3),
    draw_rank(4)
])
