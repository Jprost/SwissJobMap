import os
import pickle
import json
import unidecode
import numpy as np
import pandas as pd


### Geography - geojson handeling
def get_municipalities(geojson_municipality):
    nb_municipalicites = len(geojson_municipality["features"])

    df = pd.DataFrame()
    for muni in range(nb_municipalicites):
        name = geojson_municipality["features"][muni]['properties']['NAME']
        canton = geojson_municipality["features"][muni]['properties']['CantonCODE']
        coor = np.array(geojson_municipality["features"][muni]['geometry']['coordinates'][0][0])[:, :2].mean(axis=0)
        df.loc[muni, 'municipality'] = unidecode.unidecode(name)
        df.loc[muni, 'canton'] = canton
        df.loc[muni, 'lat'] = coor[1]
        df.loc[muni, 'lon'] = coor[0]

    return df

def get_canton_from_city(geojson_municipality):
    """
    Creates a dict with city as key and canton as value from the official
    geojson
    """
    nb_municipalicites = len(geojson_municipality["features"])

    city_canton_hash = {}
    for muni in range(nb_municipalicites):
        name = geojson_municipality["features"][muni]['properties']['NAME']
        canton = geojson_municipality["features"][muni]['properties']['CantonCODE']
        city_canton_hash[name] = canton

    city_canton_hash['unknown'] = 'unknown'
    return city_canton_hash

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

def clean_df_jobs(df_jobs):
    """
    Applies the last formating and corrections to the dataframe
    """
    df_jobs.loc[df_jobs.city == 'Zurich', 'canton'] = 'ZH'
    df_jobs.loc[df_jobs.city == 'Geneve', 'canton'] = 'GE'
    df_jobs.loc[df_jobs.city == 'Bern', 'canton'] = 'BE'
    df_jobs.loc[df_jobs.city == 'Basel', 'canton'] = 'BS'
    df_jobs.loc[df_jobs.city.isna(), 'city'] = 'unknown'

    city_canton_hash = get_canton_from_city(municipality_cadastre)
    df_jobs.loc[df_jobs.canton == 'unknown', 'canton'] = \
        df_jobs.loc[df_jobs.canton == 'unknown', 'city']. \
            apply(lambda x: city_canton_hash[x] if x in city_canton_hash.keys() \
            else 'unknown')

    df_jobs.loc[(df_jobs.country.isna()), 'country'] = 'Switzerland'
    df_jobs = df_jobs[df_jobs.country == 'Switzerland']
    return df_jobs
