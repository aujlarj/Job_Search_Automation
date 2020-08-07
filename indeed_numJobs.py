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
        pprint(jobs_per_city)

    return expected_num_jobs


def get_actual_num_jobs(urls):
    jobcard_jks = []
    expected_num_jobs = []
    jobs_per_city = []

    print('get_actual_num_jobs started...')

    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--incognito")
    driver = webdriver.Chrome(
        options=options, executable_path=CHROME_PATH)

    driver.implicitly_wait(10)

    for url in urls:
        _flag = True
        num_jobs = 0
        next_url_counter = 0
        try_times = 3
        driver.implicitly_wait(10)
        while(_flag):
            new_site = url[0] + '&start=' + str(next_url_counter)
            driver.get(new_site)
            jobcards = driver.find_elements_by_class_name(
                'jobsearch-SerpJobCard')

            new_job_check = 0

            for jobcard in jobcards:
                # summary_to_csv = summary_to_csv.head(0)  # Reset
                jobcard_jk = jobcard.get_attribute('data-jk')

                if jobcard_jk not in jobcard_jks:

                    jobcard_jks.append(jobcard_jk)

                    new_job_check += 1
                    num_jobs += 1
                    # print("Got these many results:", job_summary_df.shape)

            # print('URLcounter:', next_url_counter, 'Num_jobs:', num_jobs)

            if new_job_check == 0:
                try_times -= 1
                # print(try_times)

            # Exit if no new jobs found for 3 times in a row
            if new_job_check == 0 and try_times == 0:
                try_times = 3
                _flag = False

            next_url_counter += 10

        jobs_per_city = [num_jobs, url[1], url[2]]
        expected_num_jobs.append(jobs_per_city)
        pprint(jobs_per_city)

    driver.close()
    print('get_actual_num_jobs ended...')
    return expected_num_jobs


def merge(list1, list2):
    df1 = pd.DataFrame(list1, columns=['Expected_jobs', 'City', 'State'])
    df2 = pd.DataFrame(list2, columns=['Actual_jobs', 'City', 'State'])

    Key = ['City', 'State']
    Final_columns = ['Expected_jobs', 'Actual_jobs', 'City', 'State']

    df3 = df1.merge(df2, how='inner', on=Key)
    df3 = df3[Final_columns]

    df3.to_csv('file_name.csv', index=False)


def main():
    canadian_cites = get_cities('Canada')
    # us_cities = get_cities('US')

    candian_urls = create_urls('Canada', canadian_cites)
    # us_urls = create_urls('US', us_cities)

    expected_canadian_jobs = get_expected_num_jobs(candian_urls)
    # expected_us_jobs = get_expected_num_jobs(us_urls)

    actual_canadian_jobs = get_actual_num_jobs(candian_urls)
    # actual_US_jobs = get_actual_num_jobs(us_urls)

    merge(expected_canadian_jobs, actual_canadian_jobs)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total time: %s minutes" % ((time.time() - start_time)/60))
