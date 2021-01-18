import pickle
import pandas as pd
from source.charts_manager import ChartsManager, city_canton_jobs
from source.plotting import draw_canton_and_bubble_chart, draw_pie_chart, draw_bar_charts

# Loads dataframes
DATA_DIR = './Data/'
df_city_coordinates = pd.read_csv(DATA_DIR + 'df_city_coordinates.csv')
df_canton_naming = pd.read_csv(DATA_DIR +'canton_naming.csv', index_col='Idx')
df_jobs = pickle.load(open(DATA_DIR +'/df_jobs.p', 'rb'))
df_count_city, df_count_canton = city_canton_jobs(df_jobs=df_jobs, city_coordinates=df_city_coordinates,
                                                 job_function=False, canton_naming=df_canton_naming)

bar_plot_height = 150
scale_bubble = 1 #800 / df_count_city['All Jobs'].max()
job_function = 'All Jobs'
fig_map = draw_canton_and_bubble_chart(job_function, df_count_city, df_count_canton, scale_bubble, DATA_DIR, bar_plot_height)

# Pie chart
fig_pie = draw_pie_chart(df_jobs, bar_plot_height)

# Bar charts
fig_Canton_bar, fig_city_bar = draw_bar_charts(df_count_city, df_count_canton, job_function, bar_plot_height)

selected_button_style = {'border-color': '#e14c4e', 'background-color': '#dc1e14', 'color': '#FFFFFF', 'border-width': '2px'}
unselected_button_style = {}

job_map_app = ChartsManager(df_jobs, df_city_coordinates, df_canton_naming,
                fig_map, fig_pie, fig_Canton_bar, fig_city_bar,
                selected_button_style, unselected_button_style)

del df_count_city, df_count_canton, df_jobs

server = job_map_app.app.server

if __name__ == '__main__':
    job_map_app.app.run_server(debug=False)