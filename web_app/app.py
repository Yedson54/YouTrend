import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP])

from pages.auth import add_auth_callbacks
import pages.pg3 as pg3
add_auth_callbacks(app)
pg3.add_model_callbacks(app)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(page["name"], href=page["path"])
            ) for page in dash.page_registry.values()],
    brand="Youtube Trends",
    brand_href="/",
    color="#6D071A",
    dark=True
)

app.layout = dbc.Container([
    navbar,
    dash.page_container
], fluid=True)

if __name__ == "__main__":
    app.run_server(port=4050)
    