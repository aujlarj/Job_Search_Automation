from pprint import pprint
from bs4 import BeautifulSoup
import requests


def user_input():
    usa_alias = ['us', 'usa', 'america', 'united states', 'states']
    search_keywords = input('Please enter search words:')
    city = input('Please enter City:')
    state = input('Please enter State/Province:')
    country = input('Country (Canada or US only):')

    while country.lower() != 'canada' and country.lower() not in usa_alias:
        country = input('Please enter a valid country (Canada or US only):')

    return search_keywords, city, state, country


def get_main_url():
    usa_domain = 'https://www.indeed.com'
    canada_domain = 'https://ca.indeed.com'

    # search_keywords, city, state, country = user_input()

    country = 'US'
    search_keywords = 'data scientist'
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


def get_eachjob_url(site):
    source = requests.get(site).text
    soup = BeautifulSoup(source, 'html.parser')
    tag_name = 'data-jk'
    base_url = 'https://www.indeed.com/viewjob?jk='
    job_urls = []

    mydivs = soup.findAll(
        "div", class_="jobsearch-SerpJobCard unifiedRow row result")

    for div in mydivs:
        # can also use div.get(tagname)
        job_urls.append(base_url+div[tag_name])

    return job_urls


def main():
    main_url = get_main_url()
    urls = get_eachjob_url(main_url)
    pprint(urls)


if __name__ == "__main__":
    main()
