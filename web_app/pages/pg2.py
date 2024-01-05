import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
# import pandas as pd
# import plotly.express as px
import plotly.graph_objects as go
import re
import datetime

dash.register_page(__name__, name='Duration Model')

with open("pages/scripts/utils.py") as f:
    exec(f.read())

# with open("pages/scripts/utils.py") as f:
#     exec(f.read())

with open("pages/scripts/make_prediction.py") as f:
    exec(f.read())


layout = html.Div([
    html.Br(),
    dbc.Row([
        html.H3('Duration Model', style={'color': '#6D071A', 'textAlign': 'center'})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input_link',
                placeholder='Enter video link...',
                type='url',
                style={'width': '100%'}
            )
        ], width=9)
    ], justify='center'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Button('Submit', id='button1', n_clicks=0)
        ], width=1)
    ], justify='center'),
    html.Br(),
    html.Div(id='card_info_video'),
    html.Br(),
    html.Div(id='title_compute_proba'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Div(id='layout_proba')
        ], width=6),
        dbc.Col([
            html.Div(id='card_proba')
        ], width=6)
    ]),
    html.Br(),
    html.Div(id='title_plot_proba'),
    html.Br(),
    html.Div(id='layout_plot'),
    html.Br(),
    html.Div(id='plot_proba')
])


@callback(
    Output('card_info_video', 'children'),
    State('input_link', 'value'),
    Input('button1', 'n_clicks'),
    prevent_initial_call=True
)
def check_and_find_video(link, btn1):
    to_match1 = "https://www.youtube.com/watch\?v="
    if re.search(to_match1, link) is None:
        return None, None
    else:
        video_id = get_video_id(link)
        df = get_video_details2(video_id)
    
    res = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5('Video Id', style={'color': '#6D071A'}),
                    html.H6(video_id)
                ], width=3),
                dbc.Col([
                    html.H5('Title', style={'color': '#6D071A'}),
                    html.H6(df.loc[0, 'Titre'])
                ], width=9)
            ]),
        ])
    )
    return res



@callback(
    Output('title_compute_proba', 'children'),
    Output('layout_proba', 'children'),
    Input('button1', 'n_clicks'),
    prevent_initial_call=True
)
def update_layout_proba(btn1):
    now = datetime.datetime.now()
    yn, mn, dn = now.year, now.month, now.day
    title = dbc.Row([
        html.H5(
            "Compute the probability of remaining out of trend",
            style={'textAlign': 'center', 'color': '#6D071A'}
        )
    ])
    div = dbc.Card(dbc.CardBody([
        dbc.Row([
            html.P('Choose a date at which computing the probability'),
            dbc.Col([
                dcc.Input(
                    id='choose_date',
                    type='datetime-local',
                    step=2,
                    min=datetime.datetime(yn, mn, dn)
                ),
            ], width=6),
            dbc.Col([
                html.Button('Submit', id='submit_date')
            ], width=2)
        ], justify='center')
    ]), style={'height': '7rem'})
    return title, div


@callback(
    Output('card_proba', 'children'),
    State('input_link', 'value'),
    State('choose_date', 'value'),
    Input('submit_date', 'n_clicks'),
    prevent_initial_call=True
)
def get_proba(link, date, btn2):
    p = survival_probability(
        link, 
        date=date,
        video_cat_enc=VIDEO_CAT_ENCODER
    )
    div = dbc.Card(dbc.CardBody([
        dbc.Row([
            html.P('Probability of not becoming a trending video at choosen date'),
            dbc.Col([
                html.H6('Probability = ', style={'color': '#6D071A', 'textAlign': 'right'})
            ], width=5),
            dbc.Col([
                html.H6(p)
            ], width=6)
        ])
    ]), style={'height': '7rem'})
    return div

@callback(
    Output('title_plot_proba', 'children'),
    Output('layout_plot', 'children'),
    Input('button1', 'n_clicks'),
    prevent_initial_call=True
)
def update_layout_plot(btn1):
    title = dbc.Row([
        html.H5(
            "Plot Survival Graph",
            style={'textAlign': 'center', 'color': '#6D071A'}
        )
    ])
    now = datetime.datetime.now()
    yn, mn, dn = now.year, now.month, now.day
    div = dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([dbc.Row([
                dbc.Col([
                    html.P('Choose a starting date'),
                    dcc.Input(
                        id='choose_start_date',
                        type='datetime-local',
                        step=2,
                        min=datetime.datetime(yn, mn, dn)
                )
                ], width=4),
                dbc.Col([
                    html.P('Choose a span of days to plot'),
                    dcc.Slider(
                        5, 50, 5, value=10, id='choose_range_days'
                    )
                ], width=8)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.Button('Update Graph', id='submit_params')
            ], width=2)
        ], justify='center')]))
        ])
    ])
    return title, div


@callback(
    Output('plot_proba', 'children'),
    State('input_link', 'value'),
    State('choose_start_date', 'value'),
    State('choose_range_days', 'value'),
    Input('submit_params', 'n_clicks'),
    prevent_initial_call=True
)
def get_plot_proba(link, start_date, range_days, btn3):
    df = get_video_details(
        link, 
        video_cat_enc=VIDEO_CAT_ENCODER
    )
    x, y = plot_survival_probability(
        single_df=df,
        start_date=start_date,
        duration_days=range_days,
        video_link=link,
        video_cat_enc=VIDEO_CAT_ENCODER
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x, y=y, line_shape='hv')
    )
    fig.update_layout(
        template='plotly_white',
        title='Survival Plot',
        xaxis_title='Epoch of 12 hours',
        yaxis_title='Probability')
    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    )
