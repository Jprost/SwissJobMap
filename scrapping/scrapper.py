import logging
import requests
import unidecode
from tqdm import tqdm
import io
from multiprocessing import cpu_count, Pool
import pickle
from bs4 import BeautifulSoup
from datetime import timedelta, date
from time import sleep
from selenium import webdriver

DATA_DIR = './Data/'


class TqdmToLogger(io.StringIO):
    """
    Output stream for TQDM which will output to logger module instead of
    the StdOut.
    """
    logger = None
    level = None
    buf = ''

    def __init__(self, logger, level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)


# --- Scrapping job page ---
def get_job_date(html_soup):
    """
    Get the posting date of the job.
    Best accuracy is at the day scale, then week, then month

    return a datetime.date type
    """
    time_raw = html_soup.find("span",
                              class_="topcard__flavor--metadata posted-time-ago__text")

    # if job is defined as `NEW`
    if not time_raw:
        time_raw = html_soup.find("span",
                                  class_="topcard__flavor--metadata posted-time-ago__text posted-time-ago__text--new")

    time_raw = time_raw.text.split()[:2]
    time_scale = time_raw[1]

    today = ['minutes', 'minute', 'hour', 'hours', 'seconds', 'Just']
    if time_scale in today:
        job_date = date.today()
    elif (time_scale == 'day') or (time_scale == 'days'):
        job_date = date.today() - timedelta(days=int(time_raw[0]))
    elif (time_scale == 'week') or (time_scale == 'weeks'):
        job_date = date.today() - timedelta(weeks=int(time_raw[0]))
    elif (time_scale == 'month') or (time_scale == 'months'):
        job_date = date.today() - timedelta(weeks=4 * int(time_raw[0]))
    else:
        raise ValueError

    return job_date


def format_city(city_str: str) -> str:
    """
    Put the city string in the appropriate format
    """
    city_str = unidecode.unidecode(city_str)

    if len(city_str.split()) == 2:
        composed_str = city_str.split()
        first_str = composed_str[0]
        sec_str = composed_str[1]

        if first_str == 'St' or first_str == 'Saint' or first_str == 'Sankt':
            return 'St. ' + sec_str
    # specific cases - frequent mistakes
    if city_str == 'Geneva':
        return 'Geneve'
    elif city_str == 'Lucerne':
        return 'Luzern'
    elif city_str == 'Biel' or city_str == 'Bienne':
        return 'Biel/Bienne'
    elif city_str == 'Berne':
        return 'Bern'
    elif city_str == 'Schlatt (Zurich)':
        return 'Zurich'
    else:
        return city_str


def get_job_characteristic(html_soup: BeautifulSoup) -> dict:
    """
    Get the HTML file and extract job information. Store it in a dict format
    to late append to a pd.DataFrame
    """
    job_charac = {}
    job_charac['title'] = html_soup.h1.text
    company_span = html_soup.find("span", class_='topcard__flavor')
    job_charac['company'] = company_span.text

    if company_span.a:  # if the company name is clickable

        location = html_soup.find_all("span", class_='topcard__flavor')[1] \
            .text.split(', ')
        if location:
            if len(location) > 2:
                job_charac['city'] = format_city(location[0])
                job_charac['canton'] = unidecode.unidecode(location[1])

            elif len(location) == 1:
                location = location.split()
                if len(location) > 1:
                    # Greater XXX Area
                    if location[0] == 'Greater':
                        job_charac['city'] = location[1]
                    else:  # XXX Metropolitan Area
                        job_charac['city'] = location[0]
                else:
                    job_charac['country'] = 'Switzerland'
            else:
                job_charac['city'] = format_city(location[0])
        else:
            job_charac['city'] = 'unknown'
    else:
        job_charac['city'] = 'unknown'

    job_charac['date'] = get_job_date(html_soup)
    job_charac['content'] = html_soup.find("div",
                                           class_="description__text description__text--rich").prettify()

    for subheader in html_soup.find_all("h3", class_='job-criteria__subheader'):
        job_charac[subheader.text] = [x.text for x in subheader.find_next_siblings("span")]

    job_charac['Seniority level'] = job_charac['Seniority level'][0]
    job_charac['Employment type'] = job_charac['Employment type'][0]

    return job_charac


def scrap_job_page(job_link: str) -> dict:
    """
    Get a web link, access the page and scrap its content
    """
    job_page_html = requests.get(job_link).text
    html_soup = BeautifulSoup(job_page_html, 'html.parser')

    try:
        scrapped = get_job_characteristic(html_soup)
    except:
        # .failed_job_links.append(job_link)
        scrapped = {}

    return scrapped


# --- Scrapper class ---
class Scrapper:
    """
    The class connect to LinkedIn and interacts with the page by scrolling
    and clicking on buttons thanks to a driver `bot`.
    The task is decomposed into two steps :
    _ Get all the links toward individual job add <=> scroll the job results
    page
    _ Access each individual job page and scrapp the relevant information

    The processing is split into two parts to enable multiprocessing time
    optimisation. The list of links retrieved from the first step is ditributed
    to each core.

    Once the parsing and information scrapping is done. As the class wraps up
    the pipline, the class is made callable.The class can return a list of dict
    containing orgnaised information.

    Input:
    _ access_link : str, link to connect to LinkeIn

    __call__ returns:
    _ list of dict about ad information
    """

    def __init__(self, access_link: str):

        # Access link and connect
        self.access_link = access_link
        # scrapping stopper
        self.stop_scrapping = False

        self.job_links = []  # list of links of individual html job ad

        # list of extracted html content
        self.job_pages = []  # type: list

        # logger
        logger = logging.getLogger()
        # progressbar written in logger
        self.tqdm_out = TqdmToLogger(logger, level=logging.INFO)

    # --- Search and scrapp ---
    def __call__(self) -> list:
        self.search_links()
        self.scrap_all_list()
        return self.get_job_pages()

    # --- Scrapping job ad links ---
    def connect(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")  # not displayed
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.access_link)
        sleep(2)  # loading buffer

    def scroll_job_results(self) -> None:
        """
        Scrolls the side bar containing the job results and wait for loading
        """
        # Scroll down to load all jobs
        job_results_side_bar = self.driver.find_element_by_class_name('jobs-search__results-list')
        # Find button to load more jobs
        next_job_button = self.driver.find_element_by_xpath('//*[@id="main-content"]/div/section/button')

        page_height_init = 0
        page_height_updated = 1
        # while the page keeps getting longer ...
        while page_height_init != page_height_updated:
            page_height_init = page_height_updated
            # if the `next job` button is not displayed, scroll down
            while not next_job_button.is_displayed():
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(2)
            # Once the button is reached, click on it
            next_job_button.click()
            sleep(2)  # loading buffer
            # get the new page height <=> outer while loop increment
            page_height_updated = self.driver.execute_script("return document.documentElement.scrollHeight")

    def get_job_links(self) -> list:
        """
        Get the htlm content of the page and scrap the link toward job pages.
        """
        # get the html content
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # get the job page links
        job_raw_links = soup.find_all("a", class_="result-card__full-card-link")
        # Get teh english version and not the german one
        return [l.attrs["href"].replace('/ch.', '/www.') for l in job_raw_links]

    def save_job_links(self, job_links) -> None:
        """
        Loads the list of job links previouly scrapped
        """
        try:
            job_list_old = pickle.load(open('./Data/job_links.p', 'rb'))
            # appd the old list, most recent on top
            job_list_augmented = list(set(self.job_links + job_list_old))
            pickle.dump(job_list_augmented, open('./Data/job_links.p', 'wb'))

        except FileNotFoundError:
            pickle.dump(self.job_links, open('./Data/job_links.p', 'wb'))

    def search_links(self) -> None:
        """
        Exectue the searching of new job ad links and gathers them.
        """
        # connect to LinkedIn
        self.connect()
        logging.info('Inspect job search results')
        # Scroll down the `infinit` page
        self.scroll_job_results()
        # Collects all the links toward job ad pages
        self.job_links = self.get_job_links()

        logging.info('All available jobs ads collected.')
        # teminates the bot
        self.driver.close()
        # self.save_job_links(self.job_links)  # save the links

    # --- Scrapping job page ---
    def scrap_all_list(self) -> None:

        if cpu_count() > 1:
            logging.info('Multiprocessing available - {} CPUs'.format(cpu_count()))
            with Pool(cpu_count()) as p:
                self.job_pages = list(tqdm(p.imap(scrap_job_page, self.job_links),
                                           total=len(self.job_links),
                                           file=self.tqdm_out,
                                           miniters=15))
        else:
            for job in tqdm(self.job_links, file=self.tqdm_out, miniters=15):
                self.job_pages.append(scrap_job_page(job))

        # empty dict <=> False, sum of False --> sum of failed scrapping
        failed_job_links = sum(not dict_ for dict_ in self.job_pages)
        logging.info('{} Jobs failed to be parsed'.format(failed_job_links))

    def get_job_pages(self) -> list:
        """
        Access job pages
        """
        return self.job_pages
