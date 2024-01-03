from dash import Dash, html, dcc, callback, State, Input, Output
import dash

dash.register_page(__name__, name='Hugging Face Authentication')

layout = html.Div([
    html.H3('Authentication'),
    html.P('Before accessing the Stable Diffusion page, you have to enter your access token to Hugging Face.'),
    dcc.Input(id='input-token', type='text', placeholder='Please enter your Hugging Face token'),
    html.Button('Submit', id='submit-token'),
    html.Div(id='token-status'),
    html.A("Generate a token", href="https://huggingface.co/settings/tokens", target="_blank")
])

# Adding a dcc.Store to hold the token submission state
layout = html.Div([
    layout,  # your existing layout
    dcc.Store(id='token-submitted', data=False)
])

# Modify add_auth_callbacks function
def add_auth_callbacks(app):
    @app.callback(
        [Output('token-status', 'children'),
         Output('token-submitted', 'data')],
        Input('submit-token', 'n_clicks'),
        State('input-token', 'value'),
        prevent_initial_call=True
    )
    def update_token_status(n_clicks, token):
        if n_clicks and token:
            app.server.config['HUGGINGFACE_TOKEN'] = token
            return 'Token submitted successfully!', True
        return '', False