import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__, name='Statistics')

base = pd.read_csv('pages/data/french_youtube_10_12_23.csv')
base['nbview'] = base['exactViewNumber'].str.extract(
    '([\d|,]+)').replace('\D+', '', regex=True).astype('int')
base['nblikes'] = base['numberLikes'].replace(
    '\D+', '000', regex=True).astype('int')

creator_count = base.groupby(by='videoCreatorName', as_index=False).size()
creator_count.columns = ['videoCreatorName', 'Count']
creator_mean = base.groupby(
    by='videoCreatorName',
    as_index=False).mean(numeric_only=True)[
        ['videoCreatorName', 'nbview', 'nblikes']]
creator_mean.columns = ['videoCreatorName', 'Views', 'Likes']

creator = pd.merge(
    left=creator_mean,
    right=creator_count,
    on='videoCreatorName'
)
creator = creator.sort_values('Views', ascending=False)

category = base.groupby(
    by='videoCategory',
    as_index=False).mean(numeric_only=True)[
        ['videoCategory', 'nbview', 'nblikes']]
category.columns = ['videoCategory', 'Views', 'Likes']

category_count = base.groupby(by='videoCategory', as_index=False).size()
category_count.columns = ['videoCategory', 'Count']

layout = html.Div([
    html.Br(),
    dbc.Row([
        html.H3('Statstics per Creator', style={'color': '#6D071A'})
    ]),
    html.Br(),
    dbc.Row([
        dcc.Dropdown(
            id='choice_creator',
            options=creator['videoCreatorName'],
            value=list(creator['videoCreatorName'])[:5],
            multi=True
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='creator_views')
                ])
            )
        ], width=6),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='creator_likes')
                ])
            )
        ], width=6)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='ratio_likes_views')
            ])
        )
    ]),
    html.Br(),
    dbc.Row([
        html.H3('Statistics per Category', style={'color': '#6D071A'})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='choice_categ',
                options=category['videoCategory'],
                value=category['videoCategory'],
                multi=True
            )
        ], width=9),
        dbc.Col([
            dcc.RadioItems(
                id='choice_view_like',
                options=['Views', 'Likes'],
                value='Views'
            )
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='graph_categ')
            ])
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='pie_categ')
            ])
        )
    ])
])


@callback(
    Output('creator_views', 'figure'),
    Output('creator_likes', 'figure'),
    Output('ratio_likes_views', 'figure'),
    Input('choice_creator', 'value')
)
def creator_views(creators):
    df1 = creator.set_index('videoCreatorName')
    df1 = df1.loc[creators, :].reset_index()
    df1 = df1.sort_values('Views', ascending=False)
    fig1 = px.bar(
        df1,
        x='videoCreatorName', y='Views',
        color_discrete_sequence=['#6D071A'],
        template='plotly_white',
        title='Average number of Views per Creator'
    )
    df2 = df1.sort_values('Likes', ascending=False)
    fig2 = px.bar(
        df2,
        x='videoCreatorName', y='Likes',
        color_discrete_sequence=['#6D071A'],
        template='plotly_white',
        title='Average number of Likes per Creator'
    )
    df3 = df1.copy()
    df3['Ratio Likes/Views'] = df3['Likes']/df3['Views']
    df3 = df3.sort_values('Ratio Likes/Views', ascending=False)
    fig3 = px.bar(
        df3,
        x='videoCreatorName', y='Ratio Likes/Views',
        color_discrete_sequence=['#6D071A'],
        template='plotly_white',
        title='Ratio Likes / Views per Creator'
    )

    return fig1, fig2, fig3


@callback(
    Output('graph_categ', 'figure'),
    Input('choice_categ', 'value'),
    Input('choice_view_like', 'value')
)
def bar_categ(categories, axis_y):
    df = category.set_index('videoCategory')
    df = df.loc[categories, :].reset_index()
    df = df.sort_values(axis_y, ascending=False)
    fig = px.bar(
        df,
        x='videoCategory', y=axis_y,
        color_discrete_sequence=['#6D071A'],
        template='plotly_white',
        title='Average number of ' + axis_y + ' per Category'
    )
    return fig


@callback(
    Output('pie_categ', 'figure'),
    Input('choice_categ', 'value')
)
def pie_categ(categories):
    df = category_count.set_index('videoCategory')
    df = df.loc[categories, :].reset_index()
    df = df.sort_values('Count', ascending=False)
    tot = df['Count'].sum()
    df['prc'] = df['Count']/tot*100
    fig = px.pie(
        df,
        values='prc',
        names='videoCategory',
        labels={'label': "Category", "value": "Percentage of trending videos"},
        hole=0.3,
        title="Number of trending videos per Category"
    )
    # fig.update_layout(legend=dict(orientation="h"))
    return fig
