import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import requests

# Global Variables
CHROME_PATH = './browser_dependency/chromedriver_v83.exe'
SUMMARY_COLUMNS = ["Primary_Key", "Location", 'Country',
                   "Company", "Salary", "Ratings", "Remote_work", "Date_posted"]
DESCRIPTION_COLUMNS = ["Primary_Key", "Title", "Full_Description"]
ALL_COLUMNS = ['Primary_Key', 'Title', 'Company',
               'Location', 'Country', 'Salary', 'Ratings', 'Remote_work', 'Date_posted', 'Full_Description']
KEY = 'Primary_Key'
USA_DOMAIN = 'https://www.indeed.com'
CANADA_DOMAIN = 'https://ca.indeed.com'
BASE_JOB_URL = 'https://www.indeed.com/viewjob?jk='
# CANADIAN_LIST = [('Fernie', 'BC'), ('Banff', 'AB')]
# AMERICAN_LIST = [('Sidney', 'MT'), ('Marfa', 'TX')]
CANADIAN_LIST = [('Toronto', 'Ontario'), ('Montreal', 'Quebec'), ('Vancouver', 'British Columbia'),
                 ('Calgary', 'Alberta'), ('Edmonton', 'Alberta'), ('Ottawa',
                                                                   'Ontario'), ('Quebec City', 'Quebec')]
AMERICAN_LIST = [('New York City', 'NY'), ('Los Angeles', 'CA'), ('Portland', 'OR'),
                 ('Austin', 'TX'), ('Washington', 'DC'), ('San Francisco', 'CA'), ('Seattle', 'WA')]
FILE_NAME_END = str(date.today()) + '.csv'
JOB_TITLE = 'Data Scientist'
FILE_NAME = JOB_TITLE + '-' + FILE_NAME_END


def write_to_new_file(filename, fileinfo):
    if type(fileinfo) == str:
        with open(filename, 'w') as text:
            text.write(fileinfo)
    elif type(fileinfo) == list:
        with open(filename, 'w') as text:
            for index, element in enumerate(fileinfo):
                line = str(index+1) + '. ' + element + '\n'
                text.write(line)
    else:
        print('ERROR: DIFFRENT TYPE!')


def write_to_existing_file(filename, fileinfo):
    if type(fileinfo) == str:
        with open(filename, 'a') as text:
            text.write(fileinfo)
    elif type(fileinfo) == list:
        with open(filename, 'a') as text:
            for index, element in enumerate(fileinfo):
                line = str(index+1) + '. ' + element + '\n'
                text.write(line)
    else:
        print('ERROR: DIFFRENT TYPE!')


def create_html(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')

    write_to_new_file('Site.html', soup.prettify())


def user_input():
    list_ = []
    country_list = ['us', 'usa', 'america',
                    'united states', 'states', 'canada']
    search_keywords = input('Please enter search words:')
    city = input('Please enter City:')
    state = input('Please enter State/Province:')
    country = input('Country (Canada or US only):')

    while country.lower() not in country_list:
        country = input('Please enter a valid country (Canada or US only):')

    list_ = [search_keywords, city, state, country]

    return list_


def get_main_url(url_list):
    search_keywords = url_list[0]
    city = url_list[1]
    state = url_list[2]
    country = url_list[3]

    # search_keywords = 'Data Scienctist'
    # city = 'San Francisco'
    # state = 'CA'
    # country = 'US'

    search_keywords = search_keywords.strip()
    city = city.strip()
    state = state.strip()

    search_keywords = search_keywords.replace(" ", "+")
    city = city.replace(" ", "+")
    state = state.replace(" ", "+")

    if country.lower() == 'canada':
        website = CANADA_DOMAIN + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state + '&radius=100'
    else:
        website = USA_DOMAIN + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state + '&radius=100'

    print(website)

    return website


def get_job_summary(urls):
    job_summary_df = pd.DataFrame(columns=SUMMARY_COLUMNS)
    # summary_to_csv = pd.DataFrame(columns=SUMMARY_COLUMNS)
    # first_row = True
    jobcard_jks = []

    print('get_job_summary started...')

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)

    driver.implicitly_wait(2)

    for url in urls:
        _flag = True
        next_url_counter = 0
        while(_flag):
            new_site = url + '&start=' + str(next_url_counter)
            # print(new_site)

            driver.get(new_site)
            # can not have space in by_class_name. Must be one word
            jobcards = driver.find_elements_by_class_name(
                'jobsearch-SerpJobCard')

            job_check = 0

            for jobcard in jobcards:
                # summary_to_csv = summary_to_csv.head(0)  # Reset
                jobcard_jk = jobcard.get_attribute('data-jk')

                if jobcard_jk not in jobcard_jks:

                    jobcard_jks.append(jobcard_jk)

                    jobcard_html = BeautifulSoup(jobcard.get_attribute(
                        'innerHTML'), 'html.parser')

                    try:
                        location = jobcard_html.find(
                            class_="location").get_text()
                    except:
                        location = 'None'

                    try:
                        company = jobcard_html.find(class_="company").text.replace(
                            "\n", "").strip()
                    except:
                        company = 'None'

                    try:
                        salary = jobcard_html.find(class_="salary").text.replace(
                            "\n", "").strip()
                    except:
                        salary = 'None'

                    try:
                        rating = jobcard_html.find(class_="ratingsContent").text.replace(
                            "\n", "").strip()
                    except:
                        rating = 'None'

                    try:
                        remote_work = jobcard_html.find(class_="remote").text.replace(
                            "\n", "").strip()
                    except:
                        remote_work = 'None'

                    try:
                        date_posted = jobcard_html.find(class_="date").text.replace(
                            "\n", "").strip()
                    except:
                        date_posted = 'None'

                    if CANADA_DOMAIN in new_site:
                        country = 'Canada'
                    elif USA_DOMAIN in new_site:
                        country = 'USA'
                    else:
                        country = 'None'

                    job_summary_df = job_summary_df.append({"Primary_Key": jobcard_jk, 'Location': location, 'Country': country, "Company": company, "Salary": salary,
                                                            "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                                                            }, ignore_index=True)

                    # summary_to_csv = summary_to_csv.append({"Primary_Key": jobcard_jk, 'Location': location, 'Country': country, "Company": company, "Salary": salary,
                    #                                         "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                    #                                         }, ignore_index=True)

                    # if first_row:
                    #     summary_to_csv.to_csv('summary-'+FILE_NAME_END, mode='a',
                    #                           index=False)
                    #     first_row = False
                    # else:
                    #     summary_to_csv.to_csv('summary-'+FILE_NAME_END, mode='a',
                    #                           header=False, index=False)

                    job_check += 1
                    # print("Got these many results:", job_summary_df.shape)

            # Exit if no new jobs found
            if job_check == 0:
                _flag = False

            next_url_counter += 10

    driver.close()
    print('get_job_summary ended...')
    return jobcard_jks, job_summary_df


def get_job_description(url_jks):
    job_description_df = pd.DataFrame(columns=DESCRIPTION_COLUMNS)
    # description_to_csv = pd.DataFrame(columns=DESCRIPTION_COLUMNS)
    # first_row = True
    print('get_job_description started...')

    for jk in url_jks:
        # description_to_csv = description_to_csv.head(0) # Reset
        full_link = BASE_JOB_URL + jk
        # print(full_link)
        source = requests.get(full_link).text
        job_page = BeautifulSoup(source, 'html.parser')

        # print(job_page.prettify())

        try:
            description = job_page.find(
                'div', id='jobDescriptionText').get_text("|", strip=True)
        except:
            description = 'None'

        try:
            title = job_page.find(
                'h3', class_='jobsearch-JobInfoHeader-title').get_text("|", strip=True)
            pass
        except:
            title = 'None'

        job_description_df = job_description_df.append({"Primary_Key": jk, 'Title': title,
                                                        "Full_Description": description}, ignore_index=True)

        # description_to_csv = description_to_csv.append({"Primary_Key": jk, 'Title': title,
        #                                                 "Full_Description": description}, ignore_index=True)

        # if first_row:
        #     description_to_csv.to_csv('description-'+FILE_NAME_END, mode='a',
        #                               index=False)
        #     first_row = False
        # else:
        #     description_to_csv.to_csv('description-'+FILE_NAME_END, mode='a',
        #                               header=False, index=False)

    print('get_job_description ended...')
    return job_description_df


def merge_dataframes(df1, df2, file_names):
    df1_columns = list(df1.columns.values)
    df2_columns = list(df2.columns.values)
    common_columns = list(set(df1_columns) & set(df2_columns))
    Key = common_columns[0]

    df3 = df1.merge(df2, how='inner', on=Key)
    df3 = df3[ALL_COLUMNS]

    file_name = file_names[0] + ' ' + file_names[1] + \
        ' ' + file_names[2] + ' ' + file_names[3] + '.csv'

    df3.to_csv(file_name, index=False)
    print('End!')


def get_total_num_jobs(job_site):
    source = requests.get(job_site).text
    page = BeautifulSoup(source, 'html.parser')

    count_div = page.find(id='searchCountPages')
    unpack_div_string = count_div.contents[0]
    unpack_div_string = unpack_div_string.strip()
    unpack_div_list = unpack_div_string.split(" ")

    if ',' in unpack_div_list[3]:
        numbers = unpack_div_list[3].split(",")
        number = ''.join(numbers)
        num_jobs = int(number)
    elif int(unpack_div_list[3]):
        num_jobs = int(unpack_div_list[3])

    return num_jobs


def open_browser(url):
    # Check chrome version: top right corner(3dots)-> help -> about chrome

    # keep the broswer open
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)
    driver.get(url)


def create_urls():
    urls = []
    # location[0] = City
    # location[1] = State/Province
    for location in CANADIAN_LIST:
        website = CANADA_DOMAIN + '/jobs?q=' + \
            JOB_TITLE + '&l=' + location[0] + \
            '%2C+' + location[1] + '&sort=date'
        urls.append(website)

    for location in AMERICAN_LIST:
        website = USA_DOMAIN + '/jobs?q=' + \
            JOB_TITLE + '&l=' + location[0] + \
            '%2C+' + location[1] + '&sort=date'
        urls.append(website)

    return urls


def main():
    firstpage_urls = create_urls()
    pprint(firstpage_urls)

    jobcard_jks, job_summary_df = get_job_summary(firstpage_urls)
    job_description_df = get_job_description(jobcard_jks)

    df3 = job_summary_df.merge(job_description_df, how='inner', on=KEY)
    df3 = df3[ALL_COLUMNS]

    df3.to_csv(FILE_NAME, mode='a', index=False, encoding='utf_8')

    print('End!')
    # for testing
    # number_of_jobs = get_total_num_jobs(main_url)
    # print('Number of Jobs:', number_of_jobs)
    # open_browser(main_url)

    # job_url_jks, job_summary_df = get_job_summary(main_url)
    # job_description_df = get_job_description(job_url_jks)
    # merge_dataframes(job_summary_df, job_description_df, user_input_list)


if __name__ == "__main__":
    main()
