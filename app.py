from dash import Dash, dcc, html, Input, Output
import json
import logging
import pandas as pd
import plotly.express as px
import re
import webbrowser

logging.getLogger('werkzeug').setLevel(logging.ERROR)

number_matcher = re.compile(r"([0-9]+\.?|[0-9]*\.[0-9]+)")

app = Dash(__name__)
with open("config.json") as fp:
    config = json.load(fp)

regions: list[str] = config["regions"]

with open(config["map_path"]) as fp:
    geojson = json.load(fp)

table_body = html.Tbody(id="table-body")
table_body.children = []

inputs_for_callback = []
for r in regions:
    dcc_input = dcc.Input("50")
    displayed_r = ""
    for c in r:
        if c.isupper() and displayed_r != "":
            displayed_r += " "
        displayed_r += c

    table_body.children.append(html.Tr([
        html.Th(displayed_r, scope="row"),
        html.Td(dcc_input),
    ]))
    inputs_for_callback.append(Input(dcc_input, "value"))

app.layout = html.Div([
    html.Header([
        html.H1("NTT Visualization")
    ]),
    html.Main([
        dcc.Graph(id="graph"),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Daerah", scope="col"),
                    html.Th("Nilai", scope="col"),
                ])
            ]),
            table_body
        ]),
        html.Div([
            html.Label("Minimum", htmlFor="minimum"),
            dcc.Input(id="minimum", value="", style={
                "margin-left": "8px"
            }),
            html.Br(),
            html.Label("Maximum", htmlFor="maximum"),
            dcc.Input(id="maximum", value="", style={
                "margin-left": "8px"
            })
        ])
    ], style={
        "display": "flex",
        "flex-direction": "row",
        "justify-content": "space-between",
        "padding": "8px"
    }),
])

@app.callback([
    Output("graph", "figure")
], [
    *inputs_for_callback,
    Input("minimum", "value"),
    Input("maximum", "value"),
])
def update_graph(*inputs):
    values = [to_number_or_none(v) for v in inputs[:-2]]
    min_value = to_number_or_none(inputs[-2])
    max_value = to_number_or_none(inputs[-1])

    if min_value is None or max_value is None:
        non_null_values = [v for v in values if v is not None]
        if len(non_null_values) > 0:
            if min_value is None:
                min_value = min(non_null_values)

            if max_value is None:
                max_value = min(non_null_values)
        else:
            if min_value is None:
                if max_value is None:
                    min_value = 0.0
                    max_value = 0.0
                else:
                    min_value = max_value
            elif max_value is None:
                max_value = min_value

    df = pd.DataFrame({
        "Daerah": regions,
        "Nilai": values
    })

    fig = px.choropleth(
        df, geojson=geojson, color="Nilai",
        locations="Daerah", featureidkey=config["name_attribute"],
        color_continuous_scale="RdYlGn",
        range_color=[min_value, max_value]
    )

    fig.update_geos(fitbounds="geojson", visible=False, showframe=True)
    fig.update_layout(autosize=False)

    return (fig,)

def to_number_or_none(v: str):
    # We use Indonesian locale
    v = v.strip()
    v = v.replace(".", "")
    v = v.replace(",", ".")

    match_obj = number_matcher.search(v)
    if match_obj is None:
        return None
    
    v = match_obj.group(0)

    try:
        new_v = float(v.strip())
    except ValueError:
        new_v = None

    return new_v

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8050/", new=0, autoraise=True)
    app.run(debug=False)
