import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


class ChartsManager:
    """
    This class manages the web app.
    An instance will recieve teh data and the plots. The HTML layout is defined at its creation.
    The instance stores the current states of each chart (map, pie and two bar charts) dropdown menus and buttons.
    When one elements is activated/clicked it modifies the aspect of others. Multiple elements combinations are
    possibles to modify the display of others.
    """
    def __init__(self, df_jobs, df_count_city, df_count_canton,
                 fig_map, fig_pie, fig_Canton_bar, fig_city_bar,
                 selected_button_style, unselected_button_style):

        self.df_count_city = df_count_city
        self.df_city_color = self.df_count_city.municipality.to_frame()
        self.df_city_color['color'] = 'rgb(20,110,220)'
        self.selected_city_color = 'rgb(255,0,0)'

        self.df_count_canton = df_count_canton
        self.df_job_function = df_jobs[df_jobs.columns[10:]].sum()

        self.job_function = 'All Jobs'
        self.scale_bubble = 800 / self.df_count_city[self.job_function].max()

        self.fig_map = fig_map
        self.fig_pie = fig_pie
        self.fig_Canton_bar = fig_Canton_bar
        self.fig_city_bar = fig_city_bar

        self.selected_button_style = selected_button_style
        self.unselected_button_style = unselected_button_style
        self.btn_canton, self.btn_both, self.btn_staff_off = {}, {}, {}
        self.btn_staff_on, self.btn_city = selected_button_style, selected_button_style

        self.staff_and_recr = True

        self.app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],)
        self.app.title = 'SwissJobMap'
        canton_dropdown_labels = df_count_canton.canton + ' - ' + df_count_canton.Name
        job_functions = df_count_city.columns[4:]

        self.app.layout = html.Div(children=[
            html.H1(children='Swiss Employment Map', style={'margin-left': 10, 'margin-bottom': 10}),
            html.Div(style={'background-color': '#dc1e14', 'height': 2, 'margin-bottom': 20}),
            html.H6(children=([html.Strong("What part of Switzerland hires the most ? Where could I expect to find companies "
                                 "specialized in biotechnology ? What kind of jobs are proposed in the canton of Bern ?"
                                 " Does Geneva offers non-profit organization jobs ?"),
                                 html.Br(),
                                "The goal of this project was to create a visual and interactive representation of the "
                                "Switzerland's dynamism at the national, cantonal and municipal scale. "
                                "Statistical descriptions of the job function enable to understand the geographic "
                                "organisation and polarisation of certain industries.",
                               html.Br(),
                               "The project in built on data scrapped from ",
                               html.A('LinkedIn', href='https://www.linkedin.com/', style={'font-style': 'italic'}),
                               " from to November 8, 2020 to "
                               "November 20, 2020."
                               ]),
                     style={'margin-left': 10, 'font-family': 'avenir'}),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3(children="Swiss Map 🇨🇭"),
                        html.Div([
                            html.Button('Cities', id='map-c', style=self.selected_button_style),
                            html.Button('Cantons', id='map-C', style=self.unselected_button_style),
                            html.Button('Both', id='map-b', style=self.unselected_button_style),
                        ]),
                        dcc.Graph(id='Swiss-Employment-Map', figure=self.fig_map)],
                        style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top',
                               'margin-left': 10, 'margin-right': 10}),

                    html.Div([
                        html.H3(children="Job Functions"),
                        dcc.Dropdown(id='function-DD',
                                     options=[
                                         {'label': jf + ' - ' + str(df_count_city[jf].sum()) + ' jobs', 'value': jf}
                                         for jf in job_functions],
                                     placeholder='Select a job function ...'),

                        html.Div([html.H6('Staffing and Recruiting', style={'display': 'inline-block',
                                                                            'margin-right': 10,
                                                                            'vertical-align': 'middle'}),
                                  html.Button('On', id='staff-on', style=self.selected_button_style),
                                  html.Button('Off', id='staff-off', style=self.unselected_button_style)],
                                 style={'display': 'inline-block', 'margin-top': 10}),

                        html.Div(children=[
                            html.H4(children='Switzerland - All Job Functions', id='dynamic-title',
                                    style={'margin-top': 30, 'margin-bottom': 30, 'text-align': 'center',
                                           'font-size': 'xx-large'}),
                            dcc.Graph(id='fun-pie', figure=self.fig_pie,
                                      clickData={'points': [{'label': 'All Jobs'}]})],
                            style={'vertical-align': 'bottom'}),

                    ], style={'display': 'inline-block', 'width': '33%', 'margin-left': 10,
                              'vertical-align': 'bottom'}),

                    html.Div([
                        html.Div([
                            html.H4(children='Cantons'),
                            dcc.Dropdown(id='Canton_DD', options=[{'label': c_lab, 'value': C} for C, c_lab in
                                                                  zip(df_count_canton.canton, canton_dropdown_labels)],
                                         placeholder='Select a canton ...'),
                            dcc.Graph(id='Canton_bar', figure=self.fig_Canton_bar),
                            html.Div('The bars represent the cantons ranked by number of jobs of a certain function '
                                     'in decreasing order.', style={'font-size': 'large', 'font-family': 'avenir'})],
                            style={'width': '65%', 'display': 'inline-block', 'margin-left': 10, 'margin-right': 10}),

                        html.Div([
                            html.H4(children='Cities'),
                            dcc.Dropdown(id='city_DD',
                                         options=[{'label': c, 'value': c} for c in df_count_city.municipality],
                                         placeholder='Select a city ...'),
                            dcc.Graph(id='city_bar', figure=self.fig_city_bar),
                            html.Div('The chart displays the ten most represented cities for a particular job'
                                     'function.', style={'font-size': 'large', 'font-family': 'avenir'})],
                            style={'display': 'inline-block', 'width': '33%', 'margin-left': 10}),
                    ]),

                    html.Footer(children=' Made by Jean-Baptiste PROST - Fall 2020 ', style={'text-align': 'right',
                                                                                             'margin-top': 20}),
                ])
            ])
        ])
        del canton_dropdown_labels, job_functions

        self.app.callback([Output('Swiss-Employment-Map', 'figure'),
                           Output('fun-pie', 'figure'),
                           Output('Canton_bar', 'figure'),
                           Output('city_bar', 'figure'),
                           Output('map-c', 'style'), Output('map-C', 'style'), Output('map-b', 'style'),
                           Output('staff-on', 'style'), Output('staff-off', 'style'),
                           Output('dynamic-title', 'children')],
                          [Input('map-c', 'n_clicks'), Input('map-C', 'n_clicks'), Input('map-b', 'n_clicks'),
                           Input('function-DD', 'value'), Input('fun-pie', 'clickData'),
                           Input('Canton_bar', 'clickData'), Input('Canton_DD', 'value'),
                           Input('city_bar', 'clickData'), Input('city_DD', 'value'),
                           Input('staff-on', 'n_clicks'), Input('staff-off', 'n_clicks'),
                           Input('Swiss-Employment-Map', 'clickData')],
                          prevent_initial_call=True)(self.update_map_job_function)

        self.app.callback(Output('function-DD', 'value'),
                          Input('fun-pie', 'clickData'),
                          prevent_initial_call=True)(self.update_job_function_dropdown_value)

        self.app.callback(Output('Canton_DD', 'value'),
                          Input('Canton_bar', 'clickData'),
                          prevent_initial_call=True)(self.update_canton_dropdown_value)

        self.app.callback(Output('city_DD', 'value'),
                          Input('city_bar', 'clickData'),
                          prevent_initial_call=True)(self.update_city_dropdown_value)

    def update_map_job_function(self, click_cities, click_cantons, click_both,
                                job_function_dd, job_function_pie,
                                Canton_bars, Canton_DD,
                                city_bars, city_DD,
                                staff_on, staff_off,
                                map_click):
        """
        Updates the scattermapbox and the choroplethmapbox
        """
        # buttons - Change map visualization

        job_function_triggered = False
        canton, city = None, None
        dynamic_title = 'Switzerland'
        ctx = dash.callback_context
        callb_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # button --> map styling
        if callb_id.startswith('m'):
            if callb_id.endswith('C'):  # cantons
                self.fig_map.update_traces(visible=True, selector=dict(type="choroplethmapbox"), overwrite=True)
                self.fig_map.update_traces(visible=False, selector=dict(type="scattermapbox"), overwrite=True)
                self.btn_canton = self.selected_button_style
                self.btn_both = self.unselected_button_style
                self.btn_city = self.unselected_button_style
            elif callb_id.endswith('c'):  # cities
                self.fig_map.update_traces(visible=False, selector=dict(type="choroplethmapbox"), overwrite=True)
                self.fig_map.update_traces(visible=True, selector=dict(type="scattermapbox"), overwrite=True)
                self.btn_city = self.selected_button_style
                self.btn_canton = self.unselected_button_style
                self.btn_both = self.unselected_button_style
            elif callb_id.endswith('b'):  # both
                self.fig_map.update_traces(visible=True, selector=dict(type="choroplethmapbox"), overwrite=True)
                self.fig_map.update_traces(visible=True, selector=dict(type="scattermapbox"), overwrite=True)
                self.btn_both = self.selected_button_style
                self.btn_canton = self.unselected_button_style
                self.btn_city = self.unselected_button_style

        # buttons for Staff and Recruiting
        elif callb_id.startswith('s'):
            if callb_id.endswith('f'):  # off
                self.staff_and_recr = False
                self.btn_staff_off = self.selected_button_style
                self.btn_staff_on = self.unselected_button_style
            else:  # on
                self.staff_and_recr = True
                self.btn_staff_on = self.selected_button_style
                self.btn_staff_off = self.unselected_button_style
            self.pie_update(canton, city)

        # Job_function
        elif callb_id.startswith('f'):
            job_function_triggered = True  # for latter plotting
            if callb_id.endswith('D'):  # dropdown menu for job functions
                self.job_function = job_function_dd
            else:  # pie chart
                self.job_function = job_function_pie['points'][0]['label']

        # Canton
        elif callb_id.startswith('C'):
            if callb_id.endswith('r'):
                canton = Canton_bars['points'][0]['label']
            elif Canton_DD is not None:  # dropdown menu
                canton = Canton_DD

            self.fig_map.update_traces(visible=True, selector=dict(type="choroplethmapbox"), overwrite=True)
            self.fig_map.update_traces(visible=False, selector=dict(type="scattermapbox"), overwrite=True)
            self.btn_canton = self.selected_button_style
            self.btn_both = self.unselected_button_style
            self.btn_city = self.unselected_button_style


        # city
        elif callb_id.startswith('c'):
            if callb_id.endswith('r'):
                city = city_bars['points'][0]['label']
            elif city_DD is not None:  # dropdown menu
                city = city_DD

            # df_city_tmp = self.df_count_city[self.df_count_city.municipality == city]
            self.df_city_color.at[self.df_city_color.municipality == city, 'color'] = 'rgb(255,0,0)'
            self.fig_map.update_traces(visible=False, selector=dict(type="choroplethmapbox"), overwrite=True)
            self.fig_map.update_traces(visible=True, selector=dict(type="scattermapbox"), overwrite=True)
            self.btn_city = self.selected_button_style
            self.btn_canton = self.unselected_button_style
            self.btn_both = self.unselected_button_style

        # click on the map
        elif callb_id.startswith('S'):
            if map_click['points'][0]['curveNumber'] == 1:  # cities
                city = map_click['points'][0]['text'].split('<', 1)[0]
            else:
                canton = map_click['points'][0]['location']

        if city is not None:  # locate the selected city with a red point/dot
            # city is too small to be seen
            if self.df_count_city.loc[self.df_count_city.municipality == city, self.job_function].values[0] < 50:
                # extract the original nbr of jobs
                nb_jobs_tmp = self.df_count_city.loc[self.df_count_city.municipality == city, self.job_function].values[
                    0]
                # set arbitrary size
                self.df_count_city.at[
                    self.df_count_city.municipality == city, self.job_function] = 50 / self.scale_bubble
                self.fig_map.update_traces(marker={'color': self.df_city_color['color'],
                                                   'size': self.df_count_city[self.job_function] * self.scale_bubble,
                                                   'sizemode': 'area'},
                                           selector={'type': 'scattermapbox'},
                                           overwrite=True)
                # re-set to  the original nbr of jobs
                self.df_count_city.at[self.df_count_city.municipality == city, self.job_function] = nb_jobs_tmp
            else:
                self.fig_map.update_traces(marker={'color': self.df_city_color['color'],
                                                   'size': self.df_count_city[self.job_function] * self.scale_bubble,
                                                   'sizemode': 'area'},
                                           selector={'type': 'scattermapbox'},
                                           overwrite=True)
            # re-set the city color to standard
            self.df_city_color.at[self.df_city_color.municipality == city, 'color'] = 'rgb(20,110,220)'
            self.pie_update(canton, city)

            dynamic_title = 'City of ' + city

        if canton is not None:  # locate the canton by drawing borders in red
            self.pie_update(canton, city)
            dynamic_title = 'Canton of ' + canton

        if job_function_triggered:  # change bar plots and maps by filtering job by function
            if self.job_function == 'All Jobs':
                dynamic_title += ' -  All Job Functions'
                self.scale_bubble = 1
            else:
                dynamic_title += ' - ' + self.job_function
                self.scale_bubble = 500 / self.df_count_city[self.job_function].max()

            self.fig_map.update_traces(marker_size=self.df_count_city[self.job_function] * self.scale_bubble,
                                       text=self.df_count_city['municipality'] + '<br>' + self.df_count_city[
                                           self.job_function].astype(str) + '<extra></extra>',
                                       selector=dict(type="scattermapbox"), overwrite=True)

            self.fig_map.update_traces(colorbar_title=self.job_function,
                                       text=self.df_count_canton['canton'],
                                       z=self.df_count_canton[self.job_function],
                                       selector=dict(type="choroplethmapbox"), overwrite=True)

            df_canton = self.df_count_canton[['canton', self.job_function]].sort_values(self.job_function,
                                                                                        ascending=False)
            df_top_10_city = self.df_count_city[['municipality', self.job_function]].sort_values(self.job_function,
                                                                                                 ascending=False)[:10]

            self.fig_Canton_bar.update_traces(y=df_canton[self.job_function], x=df_canton['canton'])
            self.fig_city_bar.update_traces(y=df_top_10_city[self.job_function], x=df_top_10_city['municipality'])
        else:
            dynamic_title += ' -  All Jobs'

        return self.fig_map, self.fig_pie, self.fig_Canton_bar, self.fig_city_bar, \
               self.btn_city, self.btn_canton, self.btn_both, self.btn_staff_on, self.btn_staff_off, \
               dynamic_title

    def pie_update(self, canton, city):
        """
        Updates the pie chart according to the city, the canton or the binary `Staffing adn Recruiting` button
        """

        if city is not None:
            if self.staff_and_recr:
                df_tmp = self.df_count_city[self.df_count_city.municipality == city]
            else:
                df_tmp = self.df_count_city.drop(columns=['Staffing and Recruiting'])
                df_tmp = df_tmp[df_tmp.municipality == city]

            df_tmp = df_tmp.drop(columns=['All Jobs', 'municipality', 'lon', 'lat', 'canton']).transpose()
            self.fig_pie.update_traces(labels=df_tmp.index,
                                       values=df_tmp.iloc[:, 0],
                                       overwrite=True)
        elif canton is not None:
            if self.staff_and_recr:
                df_tmp = self.df_count_canton[self.df_count_canton.canton == canton]
            else:
                df_tmp = self.df_count_canton.drop(columns=['Staffing and Recruiting'])
                df_tmp = df_tmp[df_tmp.canton == canton]

            df_tmp = df_tmp.drop(columns=['All Jobs', 'canton']).transpose()
            self.fig_pie.update_traces(labels=df_tmp.index,
                                       values=df_tmp.iloc[:, 0],
                                       overwrite=True)
        elif not self.staff_and_recr:
            df_tmp = self.df_job_function.drop(['Staffing and Recruiting'])
            self.fig_pie.update_traces(labels=df_tmp.index,
                                       values=df_tmp, overwrite=True)

    def update_job_function_dropdown_value(self, job_function) -> str:
        """
        Updates the value displayed/selected by the dropdown menu
        """
        return job_function['points'][0]['label']

    def update_canton_dropdown_value(self, Canton_bars) -> str:
        """
        Updates the value displayed/selected by the dropdown menu
        """
        if Canton_bars is not None:
            return Canton_bars['points'][0]['label']
        else:
            pass

    def update_city_dropdown_value(self, city_bars) -> str:
        """
        Updates the value displayed/selected by the dropdown menu
        """
        if city_bars is not None:
            return city_bars['points'][0]['label']
        else:
            pass
