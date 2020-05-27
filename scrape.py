import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver import ActionChains
# from webdriver_manager.chrome import ChromeDriverManager
import requests

# Global Variables
CHROME_PATH = './browser_dependency/chromedriver_v83.exe'


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
        print('DIFFRENT TYPE!')


def write_to_existing_file(filename, fileinfo):
    if type(fileinfo) == str:
        with open(filename, 'a') as text:
            text.write(fileinfo)
    elif type(fileinfo) == list:
        with open(filename, 'a') as text:
            for index, element in enumerate(fileinfo):
                line = str(index+1) + '. ' + element + '\n'
                text.write(line)


def create_html(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')

    write_to_new_file('Site.html', soup.prettify())


def user_input():
    country_list = ['us', 'usa', 'america',
                    'united states', 'states', 'canada']
    search_keywords = input('Please enter search words:')
    city = input('Please enter City:')
    state = input('Please enter State/Province:')
    country = input('Country (Canada or US only):')

    while country.lower() not in country_list:
        country = input('Please enter a valid country (Canada or US only):')

    return search_keywords, city, state, country


def get_main_url():
    usa_domain = 'https://www.indeed.com'
    canada_domain = 'https://ca.indeed.com'

    # search_keywords, city, state, country = user_input()

    country = 'US'
    search_keywords = 'Data Scienctist'
    city = 'San Francisco'
    state = 'CA'

    search_keywords = search_keywords.strip()
    city = city.strip()
    state = state.strip()

    search_keywords = search_keywords.replace(" ", "+")
    city = city.replace(" ", "+")
    state = state.replace(" ", "+")

    if country.lower() == 'canada':
        website = canada_domain + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state
    else:
        website = usa_domain + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state

    print(website)

    return website


def get_job_summary(job_site):
    # job_counter = 0
    # jobcard_div_ids = []
    next_url_counter = 0
    jobscard_jks = []
    url_flag = True

    df = pd.DataFrame(columns=["Primary_Key", "Location",
                               "Company", "Salary", "Ratings", "Remote_work", "Date_posted"])

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)

    # driver.delete_all_cookies()

    driver.implicitly_wait(30)

    while(url_flag):
        new_site = job_site + '&start=' + str(next_url_counter)
        print(new_site)

        driver.get(new_site)
        # can not have space in by_class_name. Must be one word
        jobcards = driver.find_elements_by_class_name('jobsearch-SerpJobCard')

        job_check = 0
        driver.implicitly_wait(5)
        for jobcard in jobcards:

            jobcard_jk = jobcard.get_attribute('data-jk')
            # jobcard_div_id = jobcard.get_attribute('id')
            # jobcard_div_ids.append(jobcard_div_id)

            if jobcard_jk not in jobscard_jks:

                jobscard_jks.append(jobcard_jk)

                jobcard_html = BeautifulSoup(jobcard.get_attribute(
                    'innerHTML'), 'html.parser')

                # print(jobcard_html.prettify())
                # try:
                #     title = jobcard_html.find("a", class_="jobtitle").text.replace(
                #         "\n", "").strip()
                # except:
                #     title = 'None'

                try:
                    location = jobcard_html.find(class_="location").get_text("|", strip=True).replace(
                        "\n", "").strip()
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

                # # Automate click on each jobcard(useful if it shows the onpage description) not consistent tho
                # element_to_click = driver.find_element_by_id(
                #     jobcard_div_id)
                # ActionChains(driver).click(element_to_click).perform()
                # job_desc = driver.find_element_by_id(
                #     'jobDescriptionText').text

                # print('Title:', title)
                # print('location:', location)
                # print('company:', company)
                # print('salary:', salary)
                # print('rating:', rating)
                # print('remote_work:', remote_work)
                # print('date_posted:', date_posted)

                df = df.append({"Primary_Key": jobcard_jk, 'Location': location, "Company": company, "Salary": salary,
                                "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                                }, ignore_index=True)

                # df = df.append({'Primary_Key': jobcard_jk, 'Title': title, 'Location': location, "Company": company,
                #                 "Salary": salary}, ignore_index=True)
                # job_counter += 1
                job_check += 1
                print("Got these many results:", df.shape)

        # Exit if no new jobs found
        if job_check == 0:
            url_flag = False

        next_url_counter += 10

    driver.close()
    return jobscard_jks, df


def get_job_description(url_jks):
    base_url = 'https://www.indeed.com/viewjob?jk='
    df = pd.DataFrame(columns=["Primary_Key", "Title",
                               "Full_Description"])

    for url_jk in url_jks:
        full_link = base_url + url_jk
        print(full_link)
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

        # print('Div type:', type(div))
        # pprint(div)

        # for i in range(0, len(div.contents)):
        #     write_to_existing_file(
        #         url_jk + '.txt', str(div.contents[i]))

        df = df.append({"Primary_Key": url_jk, 'Title': title,
                        "Full_Description": description}, ignore_index=True)

    return df


def merge_dataframes(df1, df2):
    df1_columns = list(df1.columns.values)
    df2_columns = list(df2.columns.values)
    common_columns = list(set(df1_columns) & set(df2_columns))
    Key = common_columns[0]

    df3 = df1.merge(df2, how='inner', on=Key)
    df3 = df3[['Primary_Key', 'Title', 'Company',
               'Location', 'Salary', 'Ratings', 'Remote_work', 'Date_posted', 'Full_Description']]
    df3.to_csv('file_name.csv', index=False)
    print(Key)


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


def main():
    main_url = get_main_url()

    # main_url = 'https://www.indeed.com/jobs?q=Data+Scientist+%24157%2C000&l=San+Francisco%2C+CA&radius=0'

    # number_of_jobs = get_total_num_jobs(main_url)
    # print('Number of Jobs:', number_of_jobs)
    # open_browser(main_url)  # for testing

    job_url_jks, job_summary_df = get_job_summary(main_url)
    # job_summary_df.to_csv('file_name.csv', index=False)
    job_description = get_job_description(job_url_jks)
    merge_dataframes(job_summary_df, job_description)

    # click_eachjob(main_url)

    # pprint(urls)
    # print(len(urls))


if __name__ == "__main__":
    main()

# def get_eachjob_url(job_site, all_urls):
#     source = requests.get(job_site).text
#     firstpage = BeautifulSoup(source, 'html.parser')
#     base_url = 'https://www.indeed.com/viewjob?jk='
#     attribute_name = 'data-jk'
#     job_counter = 0
#     next_url_counter = 10


# try:
#     div = job_page.find(
#         'h3', class_='jobsearch-JobInfoHeader-title').get_text("|", strip=True)
# except:
#     div = 'None'


# try:
#     div = job_page.find(
#         'div', class_='icl-Ratings-count').get_text("|", strip=True)
# except:
#     div = 'None'
