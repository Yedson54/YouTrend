# import dash
# from dash import dcc, html, callback, ctx
# from dash.dependencies import Input, Output, State

# from 
# import dash_bootstrap_components as dbc
# # import pandas as pd
# # import plotly.express as px
# import re

# dash.register_page(__name__, name='DurMod')


# layout = html.Div([
#     html.Br(),
#     dbc.Row([
#         html.H3('Duration Model', style={'color': '#6D071A'})
#     ]),
#     html.Br(),
#     dbc.Row([
#         dcc.Input(
#             id='input_link',
#             placeholder='Enter video link...',
#             type='url',
#             style={'width': '100%'}
#         )
#     ]),
#     html.Br(),
#     dbc.Row([
#         dbc.Button('Submit', id='button1', n_clicks=0)
#     ]),
#     html.Br(),
#     dbc.Row([
#         dbc.Col([
#             html.H5('Video Id'),
#             html.H5(id='video_id')
#         ], width=3),
#         dbc.Col([
#             html.H5('Title'),
#             html.H5(id='video_title')
#         ], width=9)
#     ])
# ])


# @callback(
#     Output('video_id', 'children'),
#     Output('video_title', 'children'),
#     State('input_link', 'value'),
#     Input('button1', 'n_clicks'),
#     prevent_initial_call=True
# )
# # def check_and_find_video(link, btn1):
# #     to_match1 = "https://www.youtube.com/watch\?v="
# #     if re.search(to_match1, link) is None:
# #         return None, None
# #     else:
# #         video_id = get_video_id(link)
# #         df = get_video_details(video_id)
# #     return video_id, df.loc[0, 'Titre']
