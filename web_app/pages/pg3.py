import base64
import requests
import dash
from dash import Dash, html, dcc, callback, ctx
from dash.dependencies import Input, Output, State, ALL
from PIL import Image
import io
import json

dash.register_page(__name__, name='Stable Diffusion Model')

center_style = {'textAlign': 'center'}
button_style = {'display': 'block'}
thumbnail_style = {'max-width': '100px', 'height': 'auto', 'margin': '10px'}
hidden_style = {'display': 'none'}
fixed_right_bottom_style = {'position': 'fixed', 'right': '10px', 'bottom': '10px'}

layout = html.Div([
    html.H3('Custom Thumbnail Generator', style=center_style),
    html.P('Enter a prompt to generate your video thumbnail. You can regenerate or download different images according to your needs and choose the one that suits you best.', style={'textAlign': 'center'}),
    html.P(''),
    html.P('Make sure that you have already enter your Hugging Face access token in the Authentification page', style={'textAlign': 'center'}),
    dcc.Input(id='input-prompt', type='text', placeholder='Enter a prompt', style={'width': '60%', 'margin': '10px'}),
    html.Div([
        html.Button('Generate Image', id='submit-button', n_clicks=0),
        html.A("Download Image", id='download-link', download="", href="", target="_blank",
               className='download-link', style={'color': 'blue', 'marginLeft': '10px'})
    ], style=center_style),
    dcc.Loading(id="loading-1", type="default", children=html.Div(id='image-container', style=center_style)),
    html.Div(id='previous-images', style=center_style),
    dcc.Store(id='store-previous-images', data=[])
])

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode()

def query_and_save_image(app, prompt, img_count):
    token = app.server.config.get('HUGGINGFACE_TOKEN', None)
    if not token:
        return "No authentication token provided."

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
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
def add_model_callbacks(app):
    @app.callback(
        Output('image-container', 'children'),
        Output('submit-button', 'children'),
        Output('download-link', 'href'),
        Output('download-link', 'style'),
        Output('previous-images', 'children'),
        Output('store-previous-images', 'data'),
        Input('submit-button', 'n_clicks'),
        Input({'type': 'thumbnail', 'index': ALL}, 'n_clicks'),
        State('input-prompt', 'value'),
        State('store-previous-images', 'data')
    )
    def update_image(submit_n_clicks, thumbnail_n_clicks, prompt, stored_images):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trigger_id = ctx.triggered[0]['prop_id']
        button_text = "Generate Image"

        if 'submit-button' in trigger_id:
            button_text = "Re-generate Image"
            image_path = query_and_save_image(app, prompt, len(stored_images) + 1)
            if image_path:
                encoded_image = encode_image(image_path)
                stored_images.append(encoded_image)
                download_link = f'/assets/image_{len(stored_images)}.png'
                new_previous_images = create_thumbnails(stored_images)
                return create_image(encoded_image), button_text, download_link, button_style, new_previous_images, stored_images
            else:
                return html.Div("Failed to generate image."), button_text, "", hidden_style, dash.no_update, stored_images

        elif 'thumbnail' in trigger_id:
            img_index = json.loads(trigger_id.split('.')[0])['index'] - 1
            selected_image_data = stored_images[img_index]
            download_link = f'/assets/image_{img_index + 1}.png'
            return create_image(selected_image_data), button_text, download_link, button_style, dash.no_update, stored_images

        return dash.no_update

def create_image(encoded_image):
    return html.Img(src=f'data:image/png;base64,{encoded_image}', style={'max-width': '100%', 'height': 'auto'})

def create_thumbnails(stored_images):
    return [html.Button(html.Img(src=f'data:image/png;base64,{img_data}', style=thumbnail_style), 
                        id={'type': 'thumbnail', 'index': i+1}, 
                        style={'border': 'none', 'padding': 0}) for i, img_data in enumerate(stored_images)]
