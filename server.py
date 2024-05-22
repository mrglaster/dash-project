import dash_draggable
import plotly
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input

dataset_url = 'https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv'

df = pd.read_csv(dataset_url)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

style_dashboard = {
    "height": '100%',
    "width": '100%',
    "display": "flex",
    "flex-direction": "column",
    "flex-grow": "0"
}

style_controls = {
    "display": "grid",
    "grid-template-columns": "auto 1fr",
    "align-items": "center",
    "gap": "1rem"
}

default_countries = ["Russia", "Germany", "France"]

measure_options = [
    {"label": "Population size", "value": "pop"},
    {"label": "Life expectancy", "value": "lifeExp"},
    {"label": "GDP per capita", "value": "gdpPercap"}
]

measure_labels = {
    "pop": "Population size",
    "lifeExp": "Life expectancy",
    "gdpPercap": "GDP per capita"
}


def build_measure_vs_year_figure(selected_countries, measure="pop"):
    filtered_df = df[df.country.isin(selected_countries)]
    fig = plotly.express.line(filtered_df, x="year", y=measure, color="country", title="Indicators by Year",
                              labels={measure: measure_labels[measure]}, template="plotly_dark")
    return fig


measure_vs_year_dashboard = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("Active Countries")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(df.country.unique(), default_countries, multi=True, id='dropdown-active-countries'),
            ], style={"width": "100%"}),
        ]),
        html.Tr([
            html.Td([
                html.Span("Measure")
            ]),
            html.Td([
                dcc.Dropdown(options=measure_options, value="pop", id='dropdown-measure', clearable=False)
            ]),
        ])
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='measure-vs-year-graph', figure=build_measure_vs_year_figure(default_countries), style=style_dashboard,
              responsive=True)
], style=style_dashboard, id="measure-vs-year-dashboard")


def build_bubble_chart_figure(x="gdpPercap", y="lifeExp", size="pop", year_from=None, year_to=None):
    filtered_df = df

    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]

    latest_data = filtered_df.sort_values(["continent", "year"], ascending=False).drop_duplicates("country")

    if size == "lifeExp":
        size = latest_data.lifeExp
        size = size / size.max()
        size = size ** 6

    fig = plotly.express.scatter(latest_data, x=x, y=y, size=size, color="continent", hover_name="country", size_max=60,
                                 hover_data=["year"],
                                 labels={x: measure_labels[x], y: measure_labels[y], size: measure_labels[size]},
                                 template="plotly_dark")
    return fig


bubble_chart_dashboard = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("X Axis")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(options=measure_options, value="gdpPercap", id='dropdown-bubble-x', clearable=False)
            ], style={"width": "100%"})
        ]),
        html.Tr([
            html.Td([
                html.Span("Y Axis")
            ]),
            html.Td([
                dcc.Dropdown(options=measure_options, value="lifeExp", id='dropdown-bubble-y', clearable=False),
            ])
        ]),
        html.Tr([
            html.Td([
                html.Span("Size")
            ]),
            html.Td([
                dcc.Dropdown(options=measure_options, value="pop", id='dropdown-bubble-size', clearable=False),
            ])
        ]),
    ], style={"margin": "0rem 1рем"}),
    dcc.Graph(id='bubble-chart', figure=build_bubble_chart_figure(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="bubble-chart-dashboard")


def build_top_population_figure(year_from=None, year_to=None):
    filtered_df = df

    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]

    latest_data = filtered_df.sort_values("year", ascending=False).drop_duplicates("country")
    top_15 = latest_data.sort_values("pop", ascending=False)[:15][::-1]

    fig = plotly.express.bar(top_15, x="pop", y="country", title="Top 15 Countries by Population", hover_data=["year"],
                             labels={"pop": measure_labels["pop"]}, template="plotly_dark")
    return fig


top_population_dashboard = html.Div([
    dcc.Graph(id='top-population', figure=build_top_population_figure(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="top-population-dashboard")


def build_population_pie_chart(year_from=None, year_to=None):
    filtered_df = df

    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]

    latest_data = filtered_df.sort_values("year", ascending=False).drop_duplicates("country")

    fig = plotly.express.pie(latest_data, values="pop", names="continent", title="Population by Continent", hole=.3,
                             labels={"pop": measure_labels["pop"]}, template="plotly_dark")
    return fig


population_pie_chart_dashboard = html.Div([
    dcc.Graph(id='population-pie-chart', figure=build_population_pie_chart(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="population-pie-chart-dashboard")

app.layout = html.Div([
    html.H1(children='Country Comparison', style={'textAlign': 'center', 'color': 'white'}),
    dash_draggable.ResponsiveGridLayout([
        measure_vs_year_dashboard, bubble_chart_dashboard,
        top_population_dashboard, population_pie_chart_dashboard
    ], clearSavedLayout=True, layouts={
        "lg": [
            {
                "i": "measure-vs-year-dashboard",
                "x": 0, "y": 0, "w": 5, "h": 15
            },
            {
                "i": "bubble-chart-dashboard",
                "x": 6, "y": 0, "w": 5, "h": 15
            },
            {
                "i": "top-population-dashboard",
                "x": 0, "y": 15, "w": 5, "h": 15
            },
            {
                "i": "population-pie-chart-dashboard",
                "x": 6, "y": 15, "w": 5, "h": 15
            }
        ]
    })
], style={'backgroundColor': '#111111'})


@callback(
    Output('measure-vs-year-graph', 'figure'),
    Input('dropdown-active-countries', 'value'),
    Input('dropdown-measure', 'value')
)
def update_measure_vs_year_dashboard(selected_countries, measure):
    return build_measure_vs_year_figure(selected_countries, measure)


def extract_year_range(range_data):
    year_from = None
    year_to = None
    if range_data:
        if 'xaxis.range[0]' in range_data:
            year_from = range_data['xaxis.range[0]']
        if 'xaxis.range[1]' in range_data:
            year_to = range_data['xaxis.range[1]']

    return year_from, year_to


@callback(
    Output('bubble-chart', 'figure'),
    Input('dropdown-bubble-x', 'value'),
    Input('dropdown-bubble-y', 'value'),
    Input('dropdown-bubble-size', 'value'),
    Input('measure-vs-year-graph', 'relayoutData'),
)
def update_bubble_chart_dashboard(x, y, size, measure_vs_year_zoom):
    return build_bubble_chart_figure(x, y, size, *extract_year_range(measure_vs_year_zoom))


@callback(
    Output('top-population', 'figure'),
    Input('measure-vs-year-graph', 'relayoutData'),
)
def update_top_population_dashboard(measure_vs_year_zoom):
    return build_top_population_figure(*extract_year_range(measure_vs_year_zoom))


@callback(
    Output('population-pie-chart', 'figure'),
    Input('measure-vs-year-graph', 'relayoutData'),
)
def update_population_pie_chart_dashboard(measure_vs_year_zoom):
    return build_population_pie_chart(*extract_year_range(measure_vs_year_zoom))


app = app.server

if __name__ == '__main__':
    app.run(debug=True)
