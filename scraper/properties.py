"""
Module used for determinig the number of pages in the 'Best Books Ever' list from www.goodreads.com
"""

import requests

from bs4 import BeautifulSoup, SoupStrainer

LIST_BASE_URL = 'https://www.goodreads.com/list/show/1.Best_Books_Ever?page='


def determine_number_of_pages():
    r = requests.get(LIST_BASE_URL + '1')
    soup = BeautifulSoup(r.text, 'lxml', parse_only=SoupStrainer(class_='pagination'))
    return int(soup.find_all('a')[-2].string)
