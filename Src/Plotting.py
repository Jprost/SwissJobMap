import plotly.graph_objects as go


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
                                  line={'color': 'black'},
                                  text=df_job_count['municipality'] + '<br>' + df_job_count[job_function].astype(str),
                                  hovertemplate='%{text} jobs<extra></extra>',
                                  marker=dict(
                                      size=df_job_count[job_function] * scale_bubble,
                                      color='blue',
                                      sizemode='area'),
                                  visible=True,
                                  showlegend=False)

    # Cantons plot
    fig_canton = go.Choroplethmapbox(colorscale='Reds',
                                     colorbar={'title': job_function},
                                     geojson=swiss_canton_geojson,
                                     featureidkey='properties.NAME',
                                     locations=df_count_canton['canton'],
                                     text=df_count_canton['canton'],
                                     z=df_count_canton[job_function],
                                     hovertemplate='%{text}' + '<br>%{z} jobs<extra></extra>',
                                     visible=False, marker={'opacity': 0.5},
                                     name='Cantons - ' + job_function)

    return fig_bubble, fig_canton