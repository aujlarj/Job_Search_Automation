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
        df = pd.read_excel('./List_of_cites/Canada.xlsx', sheetname=0)
        mylist = df['column name'].tolist()
    print(mylist)


def main():
    get_cities('canada')


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total time: %s minutes" % ((time.time() - start_time)/60))
