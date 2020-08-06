import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import time
import requests

# Global Variables
CHROME_PATH = './browser_dependency/chromedriver_v83.exe'
USA_DOMAIN = 'https://www.indeed.com'
CANADA_DOMAIN = 'https://ca.indeed.com'


def get_cities(country):
    if country.lower() == 'canada':
        df = pd.read_excel('./List_of_cites/Canada.xlsx')
    elif country.lower() == "us":
        df = pd.read_excel('./List_of_cites/UnitedStates.xlsx')
    else:
        print('ERROR! Country can be Canada or US only')
        return 0

    tuples = [tuple(x) for x in df.values]

    return tuples


def create_urls(country, city_list):
    url = []
    urls_with_city_state = []

    if country.lower() == 'canada':
        domain = CANADA_DOMAIN
    elif country.lower() == "us":
        domain = USA_DOMAIN
    else:
        print('ERROR! Country can be Canada or US only')
        return 0

    for location in city_list:
        website = domain + '/jobs?q=&l=' + location[0] + '%2C+' + location[1]
        urls_with_city_state = [website, location[0], location[1]]
        # print(urls_with_city_state)
        url.append(urls_with_city_state)

    return url


def get_expected_num_jobs(job_sites):
    expected_num_jobs = []
    jobs_per_city = []

    for job_site in job_sites:
        source = requests.get(job_site[0]).text
        page = BeautifulSoup(source, 'html.parser')

        count_div = page.find(id='searchCountPages')

        if count_div is not None:
            unpack_div_string = count_div.contents[0]
            unpack_div_string = unpack_div_string.strip()
            unpack_div_list = unpack_div_string.split(" ")

            if ',' in unpack_div_list[3]:
                numbers = unpack_div_list[3].split(",")
                number = ''.join(numbers)
                num_jobs = int(number)
            elif int(unpack_div_list[3]):
                num_jobs = int(unpack_div_list[3])
        else:
            num_jobs = 0

        jobs_per_city = [num_jobs, job_site[1], job_site[2]]
        expected_num_jobs.append(jobs_per_city)
        pprint(job_site)

    return expected_num_jobs


def temp(job_sites):
    for job_site in job_sites:
        print(job_site[0])


def main():
    canadian_cites = get_cities('Canada')
    # us_cities = get_cities('US')

    candian_url = create_urls('Canada', canadian_cites)
    # us_urls = create_urls('US', us_cities)

    canadian_jobs = get_expected_num_jobs(candian_url)
    # temp(candian_url)

    pprint(canadian_jobs)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total time: %s minutes" % ((time.time() - start_time)/60))
