"""
Module used for obtaining data about books including: title, author, cover, number of pages,
publication date and house, ISBN 10 and 13, edition language, book format, description and genres.

The data is acquired from 'Best Books Ever' list from www.goodreads.com
"""

import re
from datetime import datetime

import grequests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, SoupStrainer

import properties

BASE_URL = 'https://www.goodreads.com'
LIST_BASE_URL = 'https://www.goodreads.com/list/show/1.Best_Books_Ever?page='
NUMBER_OF_PAGES = properties.determine_number_of_pages()
LIST_OF_DICT_KEYS = ['title', 'author', 'pages', 'publish_date', 'published_by', 'edition_language', 'book_format',
                     'ISBN10', 'ISBN13', 'description', 'genres', 'cover_url']


def scrap_book_data():
    """
    Function used for scraping data for each book on each page of the list.
    The data for every book is yielded as a dictionary in the form of:
    {
     'title': 'The Hunger Games',
     'author': 'Suzanne Collins',
     'pages': 374,
     'publish_date': '2008-09-14',
     'published_by': 'Scholastic Press',
     'edition_language': 'English',
     'book_format': 'Hardcover',
     'ISBN10': '0439023483'
     'ISBN13': '9780439023481'
     'description': '...',
     'genres': ['Young Adult', 'Fiction', 'Science Fiction', 'Dystopia']
     'cover_url': 'https://d.gr-assets.com/books/1447303603l/2767052.jpg',
    }
    """
    page_responses = generate_responses(LIST_BASE_URL + str(x + 1) for x in range(NUMBER_OF_PAGES))
    for list_page_response in page_responses:
        page_soup = BeautifulSoup(list_page_response.text, 'lxml', parse_only=SoupStrainer(class_='bookTitle'))
        responses = generate_responses(BASE_URL + tag['href'] for tag in page_soup.find_all('a'))
        for book_response in responses:
            yield save_book_data_for_url(book_response)


def generate_responses(url_generator):
    """
    Function used for asynchronous generation of responses with random user agent from url generator.

    :return: generator of responses
    """
    ua = UserAgent()
    requests_generator = (grequests.get(url, headers={'User-Agent': ua.random}) for url in url_generator)
    return grequests.imap(requests_generator, size=5)


def save_book_data_for_url(response):
    """
    Function that saves book data from given response to a dictionary and returns it.
    """
    book_data = {key: None for key in LIST_OF_DICT_KEYS}
    book_soup = BeautifulSoup(response.text, 'lxml')

    book_data['title'] = next(book_soup.find(id='bookTitle').stripped_strings)

    author_tag = book_soup.find('span', itemprop='name')
    if author_tag:
        book_data['author'] = author_tag.string

    cover_tag = book_soup.find(id='coverImage')
    if cover_tag:
        book_data['cover_url'] = cover_tag['src']

    pages_tag = book_soup.find(itemprop='numberOfPages')
    if pages_tag:
        book_data['pages'] = int(pages_tag.string.split()[0])

    isbn13_tag = book_soup.find(itemprop='isbn')

    if isbn13_tag and isbn13_tag.string.isdigit():
        book_data['ISBN13'] = isbn13_tag.string
        book_data['ISBN10'] = calculate_isbn10(isbn13_tag.string)

    language_tag = book_soup.find('div', itemprop='inLanguage')
    if language_tag:
        book_data['edition_language'] = language_tag.string

    book_format_tag = book_soup.find(itemprop='bookFormatType')
    if book_format_tag:
        book_data['book_format'] = book_format_tag.string

    genre_tags = book_soup.find_all(class_='actionLinkLite bookPageGenreLink')
    if genre_tags:
        book_data['genres'] = []
        for tag in genre_tags:
            if tag.string not in book_data['genres']:
                book_data['genres'].append(tag.string)

    description_tag = book_soup.find(id='description')
    if description_tag:
        book_data['description'] = clear_string(description_tag.find_all('span')[-1].get_text())

    scrap_publish_info(book_soup, book_data)

    return book_data


def calculate_isbn10(isbn_13):
    """
    Function used for calculating ISBN-10 from ISBN-13.

    ISBN-13 is sliced to get 9 digits common for both isbns. Every digit is then multiplied
    by its respective index (1-9) from left to right and summed up. The check digit (i.e. last digit)
    equals the remainder from modulo 11 of this sum (exception: if the remainder == 10 the check digit is X).

    :return: isbn_10
    """
    digit_list = isbn_13[3:-1]
    multiplied_sum = 0
    for index, digit in enumerate(digit_list, start=1):
        multiplied_sum += index * int(digit)

    check_digit = multiplied_sum % 11

    if check_digit == 10:
        isbn_10 = isbn_13[3:-1] + 'X'
    else:
        isbn_10 = isbn_13[3:-1] + str(check_digit)

    return isbn_10


def scrap_publish_info(soup, book_dictionary):
    """
    Function that acquires publish information (date and publisher) from given book soup
    and writes it to the given dictionary.

    NOTE: the code was extracted to the separate function due to its extensive volume
    """
    publish_info_tag = soup.find('div', class_='row')

    if publish_info_tag:
        publish_info = ' '.join(next(publish_info_tag.find_next_sibling().strings).split())
        publisher_match = re.search('by (.+$)', publish_info)

        date_regex_list = ['(\w+) (\d{1,2})\w{2} (\d{4})', '(?<=Published )([a-zA-Z]+) (\d{4})',
                           '(?<=Published )(\d{4})']

        for regexp in date_regex_list:
            date_match = re.search(regexp, publish_info)
            if date_match:
                format_and_save_publish_info(date_match, publisher_match, book_dictionary)
                break


def format_and_save_publish_info(date_match, publisher_match, book_dictionary):
    """
    Function that formats date and publisher strings and saves it to the given dictionary.

    :param date_match: regex match for date
    :param publisher_match: regex match for publisher
    :param book_dictionary: the book dictionary to save publish info to
    """
    date_match = date_match.groups()

    if len(date_match) == 3:
        book_dictionary['publish_date'] = datetime.strptime(''.join(date_match), '%B%d%Y').date().isoformat()
    elif len(date_match) == 2:
        date = datetime.strptime(''.join(date_match), '%B%Y').date()
        book_dictionary['publish_date'] = '-'.join([str(date.year), str(date.month).zfill(2)])
    elif len(date_match) == 1:
        book_dictionary['publish_date'] = date_match[0]

    if publisher_match:
        book_dictionary['published_by'] = publisher_match.group(1)


def clear_string(string_to_clear):
    """
    Function used for refactoring given string. It removes unicode non-breaking spaces and makes sure proper spacing is
    maintained throughout the text.

    :return: cleared string
    """
    string_to_clear = re.sub(u'\xa0+', r' ', string_to_clear)
    string_to_clear = re.sub(r'\.(?! |\.|\n|\r|$)', r'. ', string_to_clear)
    return string_to_clear


if __name__ == '__main__':
    scrap_book_data()
