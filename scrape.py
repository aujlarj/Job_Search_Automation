from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
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
    search_keywords = 'Data Science'
    city = 'san francisco'
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


def get_eachjob_url(job_site, num_jobs):
    job_counter = 0
    next_url_counter = 0
    jobs_urls_ids = []
    url_flag = True

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=CHROME_PATH)

    while(job_counter < num_jobs and url_flag):
        new_site = job_site + '&start=' + str(next_url_counter)
        print(new_site)

        driver.get(new_site)
        driver.implicitly_wait(5)
        divs = driver.find_elements_by_class_name('result')

        job_check = 0
        for div in divs:
            job_id = div.get_attribute('data-jk')
            if job_id not in jobs_urls_ids:
                jobs_urls_ids.append(job_id)
                job_counter += 1
                job_check += 1
                print('Job_counter:', job_counter)

        if job_check == 0:
            url_flag = False

        next_url_counter += 10

    driver.close()

    return jobs_urls_ids


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
    number_of_jobs = get_total_num_jobs(main_url)
    print('Number of Jobs:', number_of_jobs)
    # open_browser(main_url)  # for testing
    job_urls = get_eachjob_url(main_url, number_of_jobs)
    write_to_new_file('url.txt', job_urls)
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

#     count_div = firstpage.find(id='searchCountPages')
#     unpack_div_string = count_div.contents[0]
#     unpack_div_string = unpack_div_string.strip()
#     unpack_div_list = unpack_div_string.split(" ")

#     if int(unpack_div_list[3]):
#         num_jobs = int(unpack_div_list[3])
#     else:
#         print('ERROR! Unpacking Div for Number of jobs not working')
#     # print(num_jobs)

#     jobsite_divs = firstpage.findAll(
#         "div", class_="jobsearch-SerpJobCard unifiedRow row result")

#     for div in jobsite_divs:
#         # can also use div.get(attribute_name)
#         all_urls.append(base_url+div[attribute_name])
#         job_counter += 1

#     while(job_counter <= num_jobs):
#         new_site = job_site + '&start=' + str(next_url_counter)
#         print(new_site)
#         new_source = requests.get(new_site).text
#         next_page = BeautifulSoup(new_source, 'html.parser')

#         jobsite_divs = next_page.findAll(
#             "div", class_="jobsearch-SerpJobCard unifiedRow row result")

#         for div in jobsite_divs:
#             # can also use div.get(attribute_name)
#             all_urls.append(base_url+div[attribute_name])
#             job_counter += 1

#         next_url_counter += 10
