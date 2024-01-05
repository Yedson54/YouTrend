import base64
import requests
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, ALL
from PIL import Image
import io
import json
import os

dash.register_page(__name__, name='Stable Diffusion Model')

center_style = {'textAlign': 'center', 'color': '#6D071A'}
button_style = {'display': 'block'}
thumbnail_style = {'max-width': '100px', 'height': 'auto', 'margin': '10px'}
hidden_style = {'display': 'none'}
fixed_right_bottom_style = {
    'position': 'fixed',
    'right': '10px',
    'bottom': '10px'}

layout1 = html.Div([
    html.H3('Authentication', style=center_style),
    html.P(
        'Before accessing the Stable Diffusion page, you have to enter ' +
        'your access token to Hugging Face.'),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input-token',
                type='text',
                placeholder='Please enter your Hugging Face token',
                style={'width': '100%'}),
        ], width=7),
        dbc.Col([
            html.Button('Submit', id='submit-token')
        ], width=1),
    ], justify='center'),
    dbc.Row([
        dbc.Col([
            html.A(
                "Generate a token",
                href="https://huggingface.co/settings/tokens",
                target="_blank",
                style={'textAlign': 'center'})
        ], width=2)
    ], justify='center')
])


layout2 = html.Div([
    html.H3('Custom Thumbnail Generator', style=center_style),
    html.P(
        'Enter a prompt to generate your video thumbnail. ' +
        'You can regenerate or download different images according ' +
        'to your needs and choose the one that suits you best. ' +
        'For example, you can try the following prompt: ' +
        '"Cartoon of a cheerful man happy to eat a Mexican taco"',
        style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input-prompt',
                type='text',
                placeholder='Enter a prompt',
                style={'width': '100%', 'margin': '10px'})
        ], width=9)
    ], justify='center'),
    html.Div([
        html.Button('Generate Image', id='submit-button', n_clicks=0),
        html.A(
            "Download Image",
            id='download-link',
            download="",
            href="",
            target="_blank",
            className='download-link', style={
                'color': 'blue',
                'marginLeft': '10px'})
    ], style=center_style),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div(id='image-container', style=center_style)),
    html.Div(id='previous-images', style=center_style),
    dcc.Store(id='store-previous-images', data=[])
])

layout = html.Div([
    html.Br(),
    dcc.Store(id='token-submitted', data=False),
    dcc.Store(id='token-value', data=None),
    html.Div(id='layout1'),
    html.Div(id='layout2')
])


@callback(
    Output('token-submitted', 'data'),
    Output('token-value', 'data'),
    Input('submit-token', 'n_clicks'),
    State('input-token', 'value'),
    prevent_initial_call=True
)
def update_token_status_and_value(button, token):
    if token is not None:
        return True, token
    return False, None


@callback(
    Output('layout1', 'children'),
    Output('layout2', 'children'),
    Input('token-submitted', 'data')
)
def update_layout(token_submitted):
    if not token_submitted:
        return layout1, None
    else:
        return None, layout2


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode()


def query_and_save_image(prompt, img_count, token):
    API_URL = "".join([
        "https://api-inference.huggingface.co",
        "/models/stabilityai/stable-diffusion-2-1"])
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        max_size = (450, 450)
        image.thumbnail(max_size, Image.ANTIALIAS)
        filename = f"assets/image_{img_count}.png"
        image.save(filename)
        return filename
    else:
        return None


# updating the image
@callback(
    Output('image-container', 'children'),
    Output('submit-button', 'children'),
    Output('download-link', 'href'),
    Output('download-link', 'style'),
    Output('previous-images', 'children'),
    Output('store-previous-images', 'data'),
    Input('submit-button', 'n_clicks'),
    Input({'type': 'thumbnail', 'index': ALL}, 'n_clicks'),
    State('input-prompt', 'value'),
    State('store-previous-images', 'data'),
    State('token-value', 'data')
)
def update_image(
        submit_n_clicks, thumbnail_n_clicks, prompt, stored_images, token):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]['prop_id']
    button_text = "Generate Image"

    if 'submit-button' in trigger_id:
        button_text = "Re-generate Image"
        image_path = query_and_save_image(
            prompt,
            len(stored_images) + 1,
            token)
        if image_path:
            encoded_image = encode_image(image_path)
            stored_images.append(encoded_image)
            dir_path = "assets"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            download_link = f'/{dir_path}/image_{len(stored_images)}.png'
            new_previous_images = create_thumbnails(stored_images)
            return (
                create_image(encoded_image),
                button_text, download_link,
                button_style,
                new_previous_images,
                stored_images)
        else:
            return (
                html.Div("Failed to generate image."),
                button_text,
                "",
                hidden_style,
                dash.no_update, stored_images)

    elif 'thumbnail' in trigger_id:
        img_index = json.loads(trigger_id.split('.')[0])['index'] - 1
        selected_image_data = stored_images[img_index]
        download_link = f'/assets/image_{img_index + 1}.png'
        return (
            create_image(selected_image_data),
            button_text, download_link,
            button_style,
            dash.no_update,
            stored_images)

    return dash.no_update


def create_image(encoded_image):
    return html.Img(
        src=f'data:image/png;base64,{encoded_image}',
        style={'max-width': '100%', 'height': 'auto'})


def create_thumbnails(stored_images):
    return [
        html.Button(
            html.Img(
                src=f'data:image/png;base64,{img_data}',
                style=thumbnail_style),
            id={'type': 'thumbnail', 'index': i+1},
            style={'border': 'none', 'padding': 0}
        ) for i, img_data in enumerate(stored_images)]