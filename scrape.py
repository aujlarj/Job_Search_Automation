from bs4 import BeautifulSoup
import requests


def get_main_url():
    usa_alias = ['us', 'usa', 'america', 'united states', 'states']
    usa_domain = 'https://www.indeed.com'
    canada_domain = 'https://ca.indeed.com'
    # ------------------------ USER INPUT------------------------------------
    # search_keywords = input('Please enter search words:')
    # city = input('Please enter City:')
    # state = input('Please enter State/Province:')
    # country = input('Country (Canada or US only):')

    # while country.lower() != 'canada' and country.lower() not in usa_alias:
    #     country = input('Please enter a valid country (Canada or US only):')
    # -------------------------------------------------------------------------
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

    return website


def get_eachjob_url(site):
    source = requests.get(site).text

    soup = BeautifulSoup(source, 'lxml')

    mydivs = soup.findAll(
        "div", class_="jobsearch-SerpJobCard unifiedRow row result")

    with open("div.txt", "w") as text_file:
        for div in mydivs:
            text_file.write(str(div))
            text_file.write(
                '\n\n\n-----------------------------------------------------------\n\n\n')

    return 'checkout!'


def main():
    main_url = get_main_url()
    urls = get_eachjob_url(main_url)
    print(urls)


if __name__ == "__main__":
    main()
