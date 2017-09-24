import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from db.models import Course
from db.utils import save_courses, get_all_specific_ids
from utils.parser import mozilla_headers
from utils.text import clear_text

already_in_db_ids = get_all_specific_ids('coursera')


def get_urls_and_headers_from_page(_id):
    html = requests.get('https://leader-id.ru/specials/?special_models_Special_page=%s' % _id, headers=mozilla_headers)
    root = BeautifulSoup(html.content.decode(), "html.parser")
    elements = root.findAll('div', {'class': 'events-item'})

    urls = []
    headers = []

    for element in elements:
        el = element.findAll('a')[1]

        if el['href'] not in already_in_db_ids:
            urls.append(el['href'])
            headers.append(el.text)

    return urls, headers


def downlaod_all_urls_and_headers():
    urls = set()
    headers = set()
    old_len = -1
    page_num = 1
    pbar = tqdm(desc='Download headers and urls from leader-id specials')

    while old_len != len(urls):
        old_len = len(urls)

        el = get_urls_and_headers_from_page(page_num)
        for a, b in zip(el[0], el[1]):
            urls.add(a)
            headers.add(b)

        pbar.update(1)
        page_num += 1

    return list(urls), list(headers)


def get_text_from_url(url):
    html = requests.get(url, headers=mozilla_headers)
    root = BeautifulSoup(html.content.decode(), "html.parser")

    if html.status_code == 200:
        answer = root.findAll('div', {'class': 'b-search'})

        if len(answer) > 0:
            return answer[0].text
        else:
            return ""
    else:
        return ""


def update_all():
    specific_ids, titles = downlaod_all_urls_and_headers()
    urls = list(map(lambda x: "https://leader-id.ru%s" % x, specific_ids))
    texts = list(map(get_text_from_url, urls))
    courses = []

    for specific_id, title, url, text in zip(specific_ids, titles, urls, texts):
        courses.append(
            Course(**{'title': title, 'text': clear_text(text), 'url': url, 'is_active': True, 'type': 'special',
                      'specific_id': specific_id}))

    saved = save_courses(courses)
    print("Saved %s specials from leader-id" % saved)
