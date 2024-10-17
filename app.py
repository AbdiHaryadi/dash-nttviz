from dash import Dash, dcc, html, Input, Output
import json
import pandas as pd
import plotly.express as px
import webbrowser

app = Dash(__name__)
regions = [
    "Alor",
    "Belu",
    "Ende",
    "FloresTimur",
    "KotaKupang",
    "Kupang",
    "Lembata",
    "Manggarai",
    "ManggaraiBarat",
    "ManggaraiTimur",
    "Nagekeo",
    "Ngada",
    "RoteNdao",
    "SabuRaijua",
    "Sikka",
    "SumbaBarat",
    "SumbaBaratDaya",
    "SumbaTengah",
    "SumbaTimur",
    "TimorTengahSelatan",
    "TimorTengahUtara"
]

with open("ntt_map.json") as fp:
    geojson = json.load(fp)

table_body = html.Tbody(id="table-body")
table_body.children = []

inputs_for_callback = []
for r in regions:
    dcc_input = dcc.Input(50, type="number")
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
            dcc.Input(id="minimum", type="number", value=0, style={
                "margin-left": "8px"
            }),
            html.Br(),
            html.Label("Maximum", htmlFor="maximum"),
            dcc.Input(id="maximum", type="number", value=100, style={
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
    values = inputs[:-2]
    min_value = inputs[-2]
    max_value = inputs[-1]
    df = pd.DataFrame({
        "Daerah": regions,
        "Nilai": values
    })

    fig = px.choropleth(
        df, geojson=geojson, color="Nilai",
        locations="Daerah", featureidkey="properties.NAME_2",
        color_continuous_scale="RdYlGn",
        range_color=[min_value, max_value]
    )

    fig.update_geos(fitbounds="geojson", visible=False, showframe=True)
    fig.update_layout(autosize=False)

    return (fig,)

if __name__ == "__main__":
    app.run(debug=True)
