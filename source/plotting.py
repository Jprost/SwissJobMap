import pickle
import json
import os
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.colors import label_rgb, n_colors

"""
Functions used to plot the charts at the launching of the web app. 
Their successive modification will be done by a `update` method.
"""

# Geography - geojson handling
def load_swiss_borders_df(DATA_DIR):
    """
    Load the longitude and latitude of Swiss municipalities
    :param DATA_DIR: data folder directory
    :return: pd.DataFrame of lon and lat for each municipality
    """
    JSON_PATH = DATA_DIR + '/Switzerland.geojson'
    if 'swiss_borders.p' not in os.listdir(DATA_DIR):
        with open(JSON_PATH, 'r') as j:
            swiss_borders = json.loads(j.read())
        df_borders = pd.DataFrame(data={'lat': [np.array(feature["geometry"]["coordinates"][0])[:, 1] for feature in
                                                swiss_borders['features']][0],
                                        'lon': [np.array(feature["geometry"]["coordinates"][0])[:, 0] for feature in
                                                swiss_borders['features']][0]})
        pickle.dump(df_borders, open(DATA_DIR + '/df_swiss_borders.p', 'wb'))
        return df_borders
    else:
        return pickle.load(open(DATA_DIR + '/df_swiss_borders.p', 'rb'))


def load_swiss_canton_geojson(DATA_DIR):
    '''
    :param DATA_DIR: data folder directory
    :return: the geojson dict of the cantons' borders
    '''
    JSON_PATH = DATA_DIR + '/SwissCanton.geojson'
    with open(JSON_PATH, 'r') as j:
        swiss_canton_geojson = json.loads(j.read())
    return swiss_canton_geojson


def draw_canton_and_bubble_chart(job_function, df_count_city, df_count_canton,
                                 scale_bubble, DATA_DIR, bar_plot_height) -> go.Figure:
    """
    Creates:
     - a chororpleth of the number of jobs (of a certain function) per canton
     - a bubble map of the number of job (of a certain function) per city
     - a line following the Swiss borders

    Inputs :
     - job_function : str defining the selected job function (or 'All Jobs')
     - df_count_city : pd.DataFrame containing teh number of jobs per category per city
     - df_count_canton : pd.DataFrame containing eh number of jobs per function per canton
     - scale bubble : float defining the scaling factor of the bubbles in the bubble plot
     - DATA_DIR : data folder directory
     - bar_plot_height : int defining the height unit used for HTML rendering

    Returns a go.Figure object containing three traces
    """

    df_swiss_borders = load_swiss_borders_df(DATA_DIR)
    # Swiss border
    fig_map = go.Figure()
    fig_map.add_trace(go.Scattermapbox(name='Switzerland',
                                       lat=df_swiss_borders['lat'],
                                       lon=df_swiss_borders['lon'],
                                       mode="lines", line=dict(width=1, color="#F00"),
                                       hoverinfo='none', visible=True,
                                       showlegend=False))

    # bubble map plot - cities
    fig_bubble = go.Scattermapbox(lon=df_count_city['lon'],
                                  lat=df_count_city['lat'], mode='markers',
                                  text=df_count_city['municipality'] + '<br>' + df_count_city[job_function].astype(str),
                                  hovertemplate='%{text} jobs<extra></extra>',
                                  marker=dict(
                                      size=df_count_city[job_function] * scale_bubble,
                                      color='rgb(20,110,220)',
                                      sizemode='area'),
                                  visible=False, name='bubble',
                                  showlegend=False)

    # Cantons plot - choropleth
    swiss_canton_geojson = load_swiss_canton_geojson(DATA_DIR)
    fig_canton = go.Choroplethmapbox(
        colorscale=[[0, 'rgb(255,255,255)'], [0.30, 'rgb(202,28,22)'], [1, 'rgb(106,15,12)']],
        colorbar={'x': 0, 'title': 'Number of Jobs'},
        geojson=swiss_canton_geojson,
        featureidkey='properties.NAME',
        locations=df_count_canton['canton'],
        text=df_count_canton['Name'],
        z=df_count_canton[job_function],
        hovertemplate='%{text}' + '<br>%{z} jobs<extra></extra>',
        visible=False, marker={'opacity': 0.75},
        name='Cantons - ' + job_function)

    # gathers all three maps
    fig_map.add_traces([fig_bubble, fig_canton])

    # Access code to special map layer for plotting
    with open(DATA_DIR + '/mapbox_token.txt', 'r') as f:
        mapbox_key = f.read().strip()
    # layout set up
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          mapbox_style="light",
                          mapbox_accesstoken=mapbox_key,
                          mapbox_zoom=6.95,
                          mapbox_center={'lat': 46.8181877, 'lon': 8.2275124},
                          height=4 * bar_plot_height)
    fig_map.update_traces(visible=True, selector=dict(type="scattermapbox"))

    return fig_map


def draw_pie_chart(df_jobs, bar_plot_height) -> go.Figure:
    """
    Creates the pie chart

    Inputs:
    - df_jobs : pd.DataFrame containing the raw information about jobs web pages
    - bar_plot_height : int defining the height unit used for HTML rendering

    Returns a go.Figure
    """
    df_job_function = df_jobs[df_jobs.columns[5:]].sum()

    colors = [label_rgb(c) for c in n_colors((200, 27, 18), (113, 15, 11), df_job_function.shape[0])]
    fig_pie = go.Figure(go.Pie(labels=df_job_function.index,
                               values=df_job_function,
                               marker={'colors': colors},
                               hovertemplate='%{label}<br>%{value} jobs - %{percent}<extra></extra>',
                               showlegend=False, textposition='inside',
                               textinfo='label',
                               insidetextorientation='radial'),
                        layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0}, 'height': 3 * bar_plot_height})
    return fig_pie


def draw_bar_charts(df_count_city, df_count_canton, job_function, bar_plot_height) -> [go.Figure, go.Figure]:
    """
    Draw the two bar charts.

    Inputs:
     df_count_city: pd.DataFrame, nbr of jobs per city
     df_count_canton: pd.DataFrame, nbr of jobs per canton
     job_function: str, job function
     bar_plot_height: int, the height of the bar plots

    Returns two go.Figures
    """
    # bar chart for cantons
    # ordering job numbers in decreasing order
    df_canton = df_count_canton[['canton', 'Name', job_function]].sort_values(job_function, ascending=False)
    fig_Canton_bar = go.Figure(go.Bar(y=df_canton[job_function], x=df_canton['canton'],
                                      customdata=df_canton['Name'],
                                      marker={'color': 'rgb(220,30,20)'},
                                      hovertemplate='%{customdata} :<br> %{y} jobs<extra></extra>',
                                      showlegend=False),
                               layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0},
                                       'plot_bgcolor': 'white',
                                       'yaxis': {'gridcolor': 'rgb(250,205,214)'},
                                       'height': bar_plot_height})

    # get the top 10 most represented cities by job function
    df_top_10_city = df_count_city[['municipality', job_function]].sort_values(job_function, ascending=False)[:10]
    fig_city_bar = go.Figure(go.Bar(y=df_top_10_city[job_function], x=df_top_10_city['municipality'],
                                    marker={'color': 'rgb(220,30,20)'},
                                    hovertemplate='%{y} jobs<extra></extra>',
                                    showlegend=False),
                             layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0},
                                     'plot_bgcolor': 'white',
                                     'yaxis': {'gridcolor': 'rgb(250,205,214)'},
                                     'height': bar_plot_height})

    return fig_Canton_bar, fig_city_bar

