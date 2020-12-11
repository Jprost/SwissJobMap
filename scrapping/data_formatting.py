import pickle
import json
import pandas as pd
import numpy as np

"""
 Cleaning/Formatting functions for job dataframe
"""


def get_job_functions(df: pd.DataFrame) -> pd.DataFrame:
    """
    From the list of job functions contained in the `job function` columns,
    creates dummy variables and returns them added to the dataframe
    """
    df = df.join(pd.get_dummies(df.Industries.apply(pd.Series).stack()). \
                 sum(level=0)).drop(columns=['Industries'])
    df.drop(columns=['Job function'], inplace=True)
    return df


def get_canton_from_city(DATA_DIR: str) -> dict:
    """
    Creates a dict with city as key and canton as value from the official
    geojson
    """
    JSON_PATH = DATA_DIR + 'SwissMunicipalities.geojson'
    with open(JSON_PATH, 'r') as j:
        geojson_municipality = json.loads(j.read())

    nb_municipalicites = len(geojson_municipality["features"])

    city_canton_hash = {}
    for muni in range(nb_municipalicites):
        name = geojson_municipality["features"][muni]['properties']['NAME']
        canton = geojson_municipality["features"][muni]['properties']['CantonCODE']
        city_canton_hash[name] = canton

    city_canton_hash['unknown'] = 'unknown'
    return city_canton_hash


def canton_cleaning(df: pd.DataFrame, DATA_DIR: str) ->pd.DataFrame:
    """
    Translate the canton into the two letter abbrevation form to get rid of
    language issues/translations. Treats NaN as well
    """
    canton_code = {'Zurich': 'ZH',
                   'Bern': 'BE',
                   'Berne': 'BE',
                   'Luzern': 'LU',
                   'Lucerne': 'LU',
                   'Uri': 'UR',
                   'Schwyz': 'SZ',
                   'Obwalden': 'OW',
                   'Nidwalden': 'NW',
                   'Glarus': 'GL',
                   'Zug': 'ZG',
                   'Fribourg': 'FR',
                   'Freiburg': 'FR',
                   'Solothurn': 'SO',
                   'Basel': 'BS',
                   'Basel-Stadt': 'BS',
                   'Basel-Landschaft': 'BL',
                   'Basel-Country': 'BL',
                   'Schaffhausen': 'SH',
                   'Appenzell Ausserrhoden': 'AR',
                   'Appenzell Innerrhoden': 'AI',
                   'Appenzell Outer-Rhoden': 'AR',
                   'Appenzell Inner-Rhoden': 'AI',
                   'St. Gallen': 'SG',
                   'St Gallen': 'SG',
                   'Graubunden': 'GR',
                   'Grigioni': 'GR',
                   'Grischun': 'GR',
                   'Aargau': 'AG',
                   'Thurgau': 'TG',
                   'Ticino': 'TI',
                   'Vaud': 'VD',
                   'Valais': 'VS',
                   'Wallis': 'VS',
                   'Neuchatel': 'NE',
                   'Geneve': 'GE',
                   'Geneva': 'GE',
                   'Jura': 'JU'}
    for job in df.index:
        try:
            df.loc[job, 'canton'] = canton_code[df.loc[job, 'canton']]
        except KeyError:
            df.loc[job, 'canton'] = 'unknown'
    df.loc[df.city == 'Zurich', 'canton'] = 'ZH'
    df.loc[df.city == 'Geneve', 'canton'] = 'GE'
    df.loc[df.city == 'Bern', 'canton'] = 'BE'
    df.loc[df.city == 'Basel', 'canton'] = 'BS'

    city_canton_hash = get_canton_from_city(DATA_DIR)
    df.loc[df.canton == 'unknown', 'canton'] = \
        df.loc[df.canton == 'unknown', 'city']. \
            apply(lambda x: city_canton_hash[x] if x in city_canton_hash.keys() \
            else 'unknown')
    return df


def split_data_frame(df: pd.DataFrame) -> [pd.DataFrame, pd.DataFrame]:
    """
    Splits the overall dataframe into two smaller version each having its
    use. They would be able to be merged through their `title`, `compagny`
    `date` attributes present in both dataframes
    - df_jobs =  contains the job functions
    - df_job_content = contains the html page (str) and other info
    """
    df_job_content = df[['title', 'company', 'date',
                         'city', 'canton', 'Seniority level',
                         'Employment type', 'content']]
    # drop empty content
    df_job_content = df_job_content[df_job_content['content'].notna()]

    df_jobs = df.drop(columns=['Seniority level',
                               'Employment type',
                               'content']).drop_duplicates()
    # treats NaN
    df_jobs['city'] = df_jobs['city'].fillna(value='unknown')
    df_jobs['canton'] = df_jobs['canton'].fillna(value='unknown')
    df_jobs.fillna(value=0, inplace=True)
    # convert from float to int16
    df_jobs = df_jobs.astype(np.int16, errors='ignore')
    # datetime.date
    df_jobs['date'] = pd.to_datetime(df_jobs['date'], dayfirst=True). \
        apply(lambda x: x.date())
    return df_jobs, df_job_content


def save_df_jobs(new_df: pd.DataFrame) -> None:
    """
    Loads the df_jobs and gather to the previouly scrapped
    """
    try:
        job_df_old = pickle.load(open('../Data/df_jobs.p', 'rb'))
        # append the old list, most recent on top
        job_df_augmented = job_df_old.append(new_df).drop_duplicates()
        # if absent job functions are added --> NaN becomes 0
        job_df_augmented.fillna(value=0, inplace=True)
        job_df_augmented = job_df_augmented.astype(np.int16, errors='ignore')
        job_df_augmented.reset_index(drop=True, inplace=True)
        pickle.dump(job_df_augmented, open('../Data/df_jobs.p', 'wb'))
    except FileNotFoundError:
        pickle.dump(new_df, open('../Data/df_jobs.p', 'wb'))


def save_df_jobs_content(new_df: pd.DataFrame) -> None:
    """
    Loads the df_jobs_content and gather to the previouly scrapped
    """
    try:
        job_df_old = pickle.load(open('../Data/df_jobs_content.p', 'rb'))
        # append the old list, most recent on top
        job_df_augmented = job_df_old.append(new_df).drop_duplicates()
        pickle.dump(job_df_augmented, open('./Data/df_jobs_content.p', 'wb'))
    except FileNotFoundError:
        pickle.dump(new_df, open('../Data/df_jobs_content.p', 'wb'))


def save_dataframes(df_jobs: pd.DataFrame, df_jobs_content: pd.DataFrame) -> None:
    """
    Save the dataframes
    """
    save_df_jobs(df_jobs)
    save_df_jobs_content(df_jobs_content)
