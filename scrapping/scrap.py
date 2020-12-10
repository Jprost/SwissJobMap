import logging.config
import yaml
import pandas as pd
from scrapper import Scrapper
from data_formatting import get_job_functions, canton_cleaning, split_data_frame
"""
Get the publicly available data from LinkedIn and formats it in a DataFrame fro the interactive web app. 

The whole program process is written int eh scrapper_process.log log file.
"""
with open('logging_config.yml', 'r') as config:
    logging.config.dictConfig(yaml.safe_load(config))

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    linkedin_link = 'https://www.linkedin.com/jobs/search/?location=Switzerland&sortBy=DD'
    scrapping = Scrapper(access_link=linkedin_link)
    job_pages = scrapping()

    df_raw = pd.DataFrame(job_pages)
    df_raw.dropna(how='all', inplace=True)
    df_raw = get_job_functions(df_raw)
    df_raw = canton_cleaning(df_raw, '../Data/')
    df_jobs, df_content = split_data_frame(df_raw)

