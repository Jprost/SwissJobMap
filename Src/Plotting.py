import plotly.graph_objects as go
import numpy as np

class MapPlot:

    def __init__(self, df_job_count, df_count_canton, scale_bubble, swiss_canton_geojson):
        self.df_job_count = df_job_count
        self.df_count_canton = df_count_canton
        self.scale_bubble = scale_bubble
        self.swiss_canton_geojson = swiss_canton_geojson

    def canton_and_bubble(self, job_function):
        """
        Creates a Chororpleth of the number of jobs (of a certain function) per
        canton and a bubble map of the mmber of job (of a certain function) per
        city.

        Inputs :
        scale_bubble = float to determine the sacle factor of the size of the
                    bubbles


        Return a tuple of go.Trace object
        """
        fig_bubble = go.Scattermapbox(lon=self.df_job_count['lon'],
                                      lat=self.df_job_count['lat'],
                                      line={'color': 'black'},
                                      customdata=self.df_job_count[['municipality', job_function]],
                                      hovertemplate='%{customdata[0]}' + '<br>%{customdata[1]} jobs',
                                      marker=dict(
                                          size=self.df_job_count[job_function] * self.scale_bubble,
                                          color='blue',
                                          sizemode='area'),
                                      visible=True,
                                      name='Cities - ' + job_function, showlegend=False)

        # Cantons plot
        fig_canton = go.Choroplethmapbox(colorscale='Reds',
                                         colorbar={'title': job_function},
                                         customdata=self.df_count_canton,
                                         geojson=self.swiss_canton_geojson,
                                         featureidkey='properties.NAME',
                                         locations=self.df_count_canton['canton'],
                                         z=self.df_count_canton[job_function],
                                         hovertemplate='%{customdata[0]}' + '<br>%{customdata[1]} jobs',
                                         visible=False, marker={'opacity': 0.5},
                                         name='Cantons - ' + job_function)

        return fig_bubble, fig_canton

    def draw_single_canton(self, canton):
        fig_canton = go.Choroplethmapbox(geojson=self.swiss_canton_geojson,
                                         featureidkey='properties.NAME',
                                         locations=self.df_count_canton['canton'][canton],
                                         visible=True, marker={'opacity': 0, 'line-with': 5})
        return fig_canton


def draw_single_canton(canton, df_count_canton, swiss_canton_geojson, swiss_canton_ordering_geojson):

    # canton_nbrs = swiss_canton_ordering_geojson[canton]
    # colors = np.array(['lightgrey'] * 51)
    # colors[canton_nbrs] = 'red'
    # fig_canton = go.Choroplethmapbox(geojson=swiss_canton_geojson,
    #                                  featureidkey='properties.NAME',
    #                                  locations=df_count_canton['canton'],
    #                                  marker_line_color=colors,
    #                                  colorscale = [[0,'rgb(255, 255, 255)'],[,'rgb(220, 20, 60)']],
    #                                  showlegend=False, showscale = False, hoverinfo='skip',
    #                                  visible=True)
    width = np.ones(26)
    width[df_count_canton[df_count_canton['canton']== canton].index] = 1
    colors = np.array(['lightgrey']*26)
    colors[df_count_canton[df_count_canton['canton']== canton].index] = 'red'
    fig_canton = go.Choroplethmapbox(geojson=swiss_canton_geojson,
                                     featureidkey='properties.NAME',
                                     locations=df_count_canton['canton'],
                                     marker_line_color=colors,
                                     marker_line_width = 1,
                                     text='location',
                                     colorscale = [[0,'rgba(0, 0, 0, 0)'],[1,'rgba(0, 0, 0, 0)']],
                                     showlegend=False, showscale = False, hoverinfo='skip',
                                     visible=True)
    return fig_canton

def canton_and_bubble(job_function, df_job_count, df_count_canton, scale_bubble, swiss_canton_geojson):
    """
    Creates a Chororpleth of the number of jobs (of a certain function) per
    canton and a bubble map of the mmber of job (of a certain function) per
    city.

    Inputs :
    scale_bubble = float to determine the sacle factor of the size of the
                bubbles


    Return a tuple of go.Trace object
    """
    fig_bubble = go.Scattermapbox(lon=df_job_count['lon'],
                                  lat=df_job_count['lat'],
                                  text=df_job_count['municipality'] + '<br>' + df_job_count[job_function].astype(str),
                                  hovertemplate='%{text} jobs<extra></extra>',
                                  marker=dict(
                                      size=df_job_count[job_function] * scale_bubble,
                                      color='rgb(20,110,220)',
                                      sizemode='area'),
                                  visible=False, name='bubble',
                                  showlegend=False)

    # Cantons plot
    fig_canton = go.Choroplethmapbox(colorscale= [[0,'rgb(255,255,255)'],[0.30,'rgb(202,28,22)'],[1,'rgb(106,15,12)']],
                                     colorbar={'x': 0, 'title': 'Number of Jobs'},
                                     geojson=swiss_canton_geojson,
                                     featureidkey='properties.NAME',
                                     locations=df_count_canton['canton'],
                                     text=df_count_canton['Name'],
                                     z=df_count_canton[job_function],
                                     hovertemplate='%{text}' + '<br>%{z} jobs<extra></extra>',
                                     visible=False, marker={'opacity': 0.75},
                                     name='Cantons - ' + job_function)

    return fig_bubble, fig_canton

