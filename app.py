# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# import plotly.express as px
# import pandas as pd
import json
import pickle

from DataFormating import *
from Plotting import canton_and_bubble

# -* Loads geojsons
JSON_PATH = './Data/SwissMunicipalities.geojson'
with open(JSON_PATH, 'r') as j:
    municipality_cadastre = json.loads(j.read())

JSON_PATH = './Data/Switzerland.geojson'
with open(JSON_PATH, 'r') as j:
    switzerland = json.loads(j.read())

df_borders = pd.DataFrame(data={'lat': [np.array(feature["geometry"]["coordinates"][0])[:, 1] for feature in
                                        switzerland['features']][0],
                                'lon': [np.array(feature["geometry"]["coordinates"][0])[:, 0] for feature in
                                        switzerland['features']][0]})
JSON_PATH = './Data/SwissCanton.geojson'
with open(JSON_PATH, 'r') as j:
    swiss_canton = json.loads(j.read())

# Access code to special map layer for plotting
with open('./Data/mapbox_token.txt', 'r') as f:
    mapbox_key = f.read().strip()

# Loads dataframes
df_bubble = pickle.load(open('./Data/df_city_count.p', 'rb'))
df_count_canton = pickle.load(open('./Data/df_canton_count.p', 'rb'))
df_jobs = pickle.load(open('./Data/df.p', 'rb'))

# --- Plotting
bar_plot_height = 225

# Swiss border
fig = make_subplots(rows=4, cols=3, specs=[
    [{'type': 'mapbox', "rowspan": 4, 'colspan': 2}, None, {'type': 'domain', "rowspan": 2}],
    [None, None, None], [None, None, {'rowspan': 1}], [None, None, {'rowspan': 1}]],
                    horizontal_spacing=0.05, vertical_spacing=0.05,
                    subplot_titles=('','Job Functions', "Top ten canton", "Ton ten cities"))
fig_map = go.Figure()
fig_map.add_trace(go.Scattermapbox(name='Switzerland',
                               lat=df_borders['lat'],
                               lon=df_borders['lon'],
                               mode="lines", line=dict(width=1, color="#F00"),
                               hoverinfo='none', visible=True,
                               showlegend=False))

scale_bubble = 800 / df_bubble['All Jobs'].max()
job_function = 'All Jobs'
fig_bubble, fig_canton = canton_and_bubble(job_function, df_bubble, df_count_canton, scale_bubble, swiss_canton)
fig_map.add_traces((fig_bubble, fig_canton))

fig_map.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0},
                  mapbox_style="light",
                  mapbox_accesstoken=mapbox_key,
                  mapbox_zoom=6.75,
                  mapbox_center={'lat': 46.8181877, 'lon': 8.2275124},
                  height= 4*bar_plot_height)

updatemenus = list([dict(type='buttons', active=0, y=1.05, x=0.11,
                         buttons=list(
                             [dict(label='Cities',
                                   method='update',
                                   args=[{'visible': [True, True, False]}]),
                              dict(label='Cantons',
                                   method='update',
                                   args=[{'visible': [True, False, True]}]),
                              dict(label='Both',
                                   method='update',
                                   args=[{'visible': [True, True, True]}])]
                         ),
                         direction='right')])

fig_map.update_layout(updatemenus=updatemenus)

# Pie chart
df_job_function = df_jobs[df_jobs.columns[10:]].sum()
df_job_function = df_job_function.drop('Staffing and Recruiting')
df_job_function = df_job_function[df_job_function / df_job_function.sum() >= 0.01]

fig_pie = go.Figure(go.Pie(labels=df_job_function.index,
                     values=df_job_function,
                     hovertemplate='%{label}<br>%{value} jobs - %{percent}<extra></extra>',
                     showlegend=False, textposition='inside'),
                    layout={'margin':{"r": 0, "t": 0, "l": 0, "b": 0}, 'height': 2*bar_plot_height})

# Bar charts
job_function = 'All Jobs'
df_top_10_canton = df_count_canton[['canton', job_function]].sort_values(job_function, ascending=False)[:10]

fig_bar_canton = go.Figure(go.Bar(y=df_top_10_canton[job_function], x=df_top_10_canton['canton'],
                     hovertemplate='%{y} jobs<extra></extra>',
                     showlegend=False), layout={'margin':{"r": 0, "t": 0, "l": 0, "b": 0}, 'height': bar_plot_height})
df_top_10_city = df_bubble[['municipality', job_function]].sort_values(job_function, ascending=False)[:10]
fig_bar_city = go.Figure(go.Bar(y=df_top_10_city[job_function], x=df_top_10_city['municipality'],
                     hovertemplate='%{y} jobs<extra></extra>',
                     showlegend=False), layout={'margin':{"r": 0, "t": 0, "l": 0, "b": 0}, 'height': bar_plot_height})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
job_functions = df_bubble.columns[4:]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div(children=[
    html.H1(children='Swiss Employment Map'),
    html.Div(children=' Hello world '),

    html.Div([
        dcc.Graph(id='Swiss-Employment-Map',
                  figure=fig_map),
        html.Label(["Job Function",
                dcc.Dropdown(id='DD-job_function',
                             options=[{'label': jf + ' - ' + str(df_bubble[jf].sum()) + ' jobs'
                                          , 'value': jf} for jf in job_functions],
                             value='All Jobs')])
        ], style={'width': '65%', 'display': 'inline-block', 'padding': '0 0 0 0 '}),
        html.Div([
            dcc.Graph(id='pie', figure=fig_pie),
            dcc.Graph(id='bar_canton', figure=fig_bar_canton),
            dcc.Graph(id='bar_city', figure=fig_bar_city),
        ], style={'display': 'inline-block', 'width': '33%'}),
    html.Div(children=' Made by Jean-Baptiste PROST - Fall 2020 ')
])


@app.callback(Output('Swiss-Employment-Map', 'figure'),
              [Input('DD-job_function', 'value')])
def update_canton_and_bubble(job_function):
    """
    Updates the scattermapbox and the choroplethmapbox
    """
    scale_bubble = 500 / df_bubble[job_function].max()
    fig_map.update_traces(marker_size=df_bubble[job_function] * scale_bubble,
                      text=df_bubble['municipality'] + '<br>' + df_bubble[job_function].astype(str) + '<extra></extra>',
                      selector=dict(type="scattermapbox"), overwrite=True)

    fig_map.update_traces(colorbar_title=job_function,
                      text=df_count_canton['canton'],
                      z=df_count_canton[job_function],
                      selector=dict(type="choroplethmapbox"), overwrite=True)

    return fig_map


if __name__ == '__main__':
    app.run_server(debug=True)
