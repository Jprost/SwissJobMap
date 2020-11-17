from FiguresClass import Figures
import plotly.graph_objects as go
import plotly
import json
import pickle

from DataFormating import *
from Plotting import canton_and_bubble, draw_single_canton

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

swiss_canton_ordering_geojson = pickle.load(open('./Data/geojson_swisscantoon_ordering.p', 'rb'))

# Loads dataframes
df_count_city = pickle.load(open('./Data/df_city_count.p', 'rb')).sort_values('municipality')
df_count_canton = pickle.load(open('./Data/df_canton_count.p', 'rb'))
df_jobs = pickle.load(open('./Data/df.p', 'rb'))

# --- Plotting
bar_plot_height = 175

# Swiss border
fig_map = go.Figure()
fig_map.add_trace(go.Scattermapbox(name='Switzerland',
                                   lat=df_borders['lat'],
                                   lon=df_borders['lon'],
                                   mode="lines", line=dict(width=1, color="#F00"),
                                   hoverinfo='none', visible=True,
                                   showlegend=False))

scale_bubble = 1 #800 / df_count_city['All Jobs'].max()
job_function = 'All Jobs'
fig_bubble, fig_canton = canton_and_bubble(job_function, df_count_city, df_count_canton, scale_bubble, swiss_canton)
fig_map.add_traces((fig_bubble, fig_canton))
# fig_map.update_layout()

fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox_style="light",
                      mapbox_accesstoken=mapbox_key,
                      mapbox_zoom=6.95,
                      mapbox_center={'lat': 46.8181877, 'lon': 8.2275124},
                      height=4 * bar_plot_height)
fig_map.update_traces(visible=True, selector=dict(type="scattermapbox"))


# Pie chart
df_job_function = df_jobs[df_jobs.columns[10:]].sum()

color_min = (200,27,18)
color_max = (113,15, 11)
kolors = [plotly.colors.label_rgb(c) for c in plotly.colors.n_colors(color_min, color_max, len(df_jobs.columns[10:]))]
fig_pie = go.Figure(go.Pie(labels=df_job_function.index,
                           values=df_job_function,
                           marker={'colors': kolors},
                           hovertemplate='%{label}<br>%{value} jobs - %{percent}<extra></extra>',
                           showlegend=False, textposition='inside',
                           textinfo='label',
                           insidetextorientation='radial'),
                           layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0}, 'height': 3*bar_plot_height})

# Bar charts
job_function = 'All Jobs'
df_canton = df_count_canton[['canton','Name',  job_function]].sort_values(job_function, ascending=False)
color_bar = 'rgb(220,30,20)'
fig_Canton_bar = go.Figure(go.Bar(y=df_canton[job_function], x=df_canton['canton'],
                                  customdata=df_canton['Name'],
                                  marker={'color': color_bar},
                                  hovertemplate='%{customdata} :<br> %{y} jobs<extra></extra>',
                                  showlegend=False),
                           layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0},
                                   'plot_bgcolor': 'white',
                                   'yaxis':{'gridcolor': 'rgb(250,205,214)'},
                                   'height': bar_plot_height})

df_top_10_city = df_count_city[['municipality', job_function]].sort_values(job_function, ascending=False)[:10]
fig_city_bar = go.Figure(go.Bar(y=df_top_10_city[job_function], x=df_top_10_city['municipality'],
                                marker={'color': color_bar},
                                hovertemplate='%{y} jobs<extra></extra>',
                                showlegend=False),
                         layout={'margin': {"r": 0, "t": 0, "l": 0, "b": 0},
                                 'plot_bgcolor': 'white',
                                 'yaxis':{'gridcolor': 'rgb(250,205,214)'},
                                 'height': bar_plot_height})

selected_button_style = {'border-color': '#e14c4e', 'background-color': '#dc1e14', 'color': '#FFFFFF', 'border-width': '2px'}
unselected_button_style = {}#{'border-color': '#e14c4e', 'background-color': '#FFFFFF', 'color': '#e14c4e', 'border-width': '2px'}
#'border-width': '1px'
job_map_app = Figures(df_jobs, df_count_city, df_count_canton,
                 fig_map, fig_pie, fig_Canton_bar, fig_city_bar,
                 selected_button_style, unselected_button_style)

server = job_map_app.app

if __name__ == '__main__':
    job_map_app.app.run_server(debug=True)