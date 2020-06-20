import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
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
    usa_domain = 'https://www.indeed.com'
    canada_domain = 'https://ca.indeed.com'

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
        website = canada_domain + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state + '&radius=100'
    else:
        website = usa_domain + '/jobs?q=' + \
            search_keywords + '&l=' + city + '%2C+' + state + '&radius=100'

    print(website)

    return website


def get_job_summary(job_site):
    next_url_counter = 0
    jobscard_jks = []
    url_flag = True

    df = pd.DataFrame(columns=["Primary_Key", "Location",
                               "Company", "Salary", "Ratings", "Remote_work", "Date_posted"])

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)

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

            if jobcard_jk not in jobscard_jks:

                jobscard_jks.append(jobcard_jk)

                jobcard_html = BeautifulSoup(jobcard.get_attribute(
                    'innerHTML'), 'html.parser')

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

                df = df.append({"Primary_Key": jobcard_jk, 'Location': location, "Company": company, "Salary": salary,
                                "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                                }, ignore_index=True)

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

        df = df.append({"Primary_Key": url_jk, 'Title': title,
                        "Full_Description": description}, ignore_index=True)

    return df


def merge_dataframes(df1, df2, file_names):
    df1_columns = list(df1.columns.values)
    df2_columns = list(df2.columns.values)
    common_columns = list(set(df1_columns) & set(df2_columns))
    Key = common_columns[0]

    df3 = df1.merge(df2, how='inner', on=Key)
    df3 = df3[['Primary_Key', 'Title', 'Company',
               'Location', 'Salary', 'Ratings', 'Remote_work', 'Date_posted', 'Full_Description']]

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


def main():
    job_summary_df = pd.DataFrame(columns=["Primary_Key", "Location", 'Country',
                                           "Company", "Salary", "Ratings", "Remote_work", "Date_posted"])
    summary_to_csv = pd.DataFrame(columns=["Primary_Key", "Location",
                                           "Company", "Salary", "Ratings", "Remote_work", "Date_posted"])
    job_description_df = pd.DataFrame(columns=["Primary_Key", "Title",
                                               "Full_Description"])
    description_to_csv = pd.DataFrame(columns=["Primary_Key", "Title",
                                               "Full_Description"])
    usa_domain = 'https://www.indeed.com'
    canada_domain = 'https://ca.indeed.com'
    base_url = 'https://www.indeed.com/viewjob?jk='
    job_title = 'Data Scientist'
    firstpage_urls = []
    jobcard_jks = []
    next_url_counter = 0
    first_row = True
    file_name = str(date.today()) + '.csv'

    # canadian_list = [('Fernie', 'BC'), ('Banff', 'AB')]
    # american_list = [('Sidney', 'MT'), ('Marfa', 'TX')]

    canadian_list = [('Toronto', 'Ontario'), ('Montreal', 'Quebec'), ('Vancouver', 'British Columbia'),
                     ('Calgary', 'Alberta'), ('Edmonton', 'Alberta'), ('Ottawa',
                                                                       'Ontario'), ('Quebec City', 'Quebec')]

    american_list = [('New York City', 'NY'), ('Los Angeles', 'CA'), ('Portland', 'OR'),
                     ('Austin', 'TX'), ('Washington', 'DC'), ('San Francisco', 'CA'), ('Seattle', 'WA')]

    for item in canadian_list:
        website = canada_domain + '/jobs?q=' + \
            job_title + '&l=' + item[0] + \
            '%2C+' + item[1] + '&sort=date'
        firstpage_urls.append(website)

    for item in american_list:
        website = usa_domain + '/jobs?q=' + \
            job_title + '&l=' + item[0] + \
            '%2C+' + item[1] + '&sort=date'
        firstpage_urls.append(website)

    pprint(firstpage_urls)

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)

    driver.implicitly_wait(30)

    for url in firstpage_urls:
        _flag = True
        next_url_counter = 0
        while(_flag):
            new_site = url + '&start=' + str(next_url_counter)
            print(new_site)

            driver.get(new_site)
            # can not have space in by_class_name. Must be one word
            jobcards = driver.find_elements_by_class_name(
                'jobsearch-SerpJobCard')

            job_check = 0
            driver.implicitly_wait(5)
            for jobcard in jobcards:
                summary_to_csv = summary_to_csv.head(0)
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

                    if canada_domain in new_site:
                        country = 'Canada'
                    else:
                        country = 'USA'

                    job_summary_df = job_summary_df.append({"Primary_Key": jobcard_jk, 'Location': location, 'Country': country, "Company": company, "Salary": salary,
                                                            "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                                                            }, ignore_index=True)

                    summary_to_csv = summary_to_csv.append({"Primary_Key": jobcard_jk, 'Location': location, "Company": company, "Salary": salary,
                                                            "Ratings": rating, "Remote_work": remote_work, "Date_posted": date_posted
                                                            }, ignore_index=True)

                    if first_row:
                        summary_to_csv.to_csv('summary-'+file_name, mode='a',
                                              index=False)
                        first_row = False
                    else:
                        summary_to_csv.to_csv('summary-'+file_name, mode='a',
                                              header=False, index=False)

                    job_check += 1
                    print("Got these many results:", job_summary_df.shape)

            # Exit if no new jobs found
            if job_check == 0:
                _flag = False

            next_url_counter += 10

    first_row = True
    driver.close()

    for jk in jobcard_jks:
        description_to_csv = description_to_csv.head(0)
        full_link = base_url + jk
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

        job_description_df = job_description_df.append({"Primary_Key": jk, 'Title': title,
                                                        "Full_Description": description}, ignore_index=True)

        description_to_csv = description_to_csv.append({"Primary_Key": jk, 'Title': title,
                                                        "Full_Description": description}, ignore_index=True)

        if first_row:
            description_to_csv.to_csv('description-'+file_name, mode='a',
                                      index=False)
            first_row = False
        else:
            description_to_csv.to_csv('description-'+file_name, mode='a',
                                      header=False, index=False)

    df1_columns = list(job_summary_df.columns.values)
    df2_columns = list(job_description_df.columns.values)
    common_columns = list(set(df1_columns) & set(df2_columns))
    Key = common_columns[0]

    df3 = job_summary_df.merge(job_description_df, how='inner', on=Key)
    df3 = df3[['Primary_Key', 'Title', 'Company',
               'Location', 'Country', 'Salary', 'Ratings', 'Remote_work', 'Date_posted', 'Full_Description']]

    df3.to_csv(file_name, mode='a', index=False, encoding='utf_8')

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
