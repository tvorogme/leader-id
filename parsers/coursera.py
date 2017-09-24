import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from db.models import Course
from db.utils import save_courses, get_all_specific_ids
from settings import DEBUG
from utils.parser import mozilla_headers
from utils.text import clear_text

already_in_db_ids = get_all_specific_ids('coursera')


def download_pack(start):
    url = 'https://www.coursera.org/courses?_facet_changed_=true&primaryLanguages=ru&start=%s' % start
    html = requests.get(url, headers=mozilla_headers).text
    root = BeautifulSoup(html, "html.parser")
    items = root.findAll('div', {'class': 'rc-SearchResults'})[0]
    return [x['href'] for x in items.findAll('a')]


def download_coursera_links() -> list:
    all_links = []
    old_len = len(already_in_db_ids) if len(already_in_db_ids) != 0 else -1
    pbar = tqdm(desc="Download links of coursera courses")

    while old_len != len(all_links):
        old_len = len(all_links)
        all_links += download_pack(len(all_links))
        pbar.update(1)

    return all_links


def parse_coursera_link(link):
    try:
        url = 'https://www.coursera.org%s' % link

        html = requests.get(url, headers=mozilla_headers)
        root = BeautifulSoup(html.content.decode(), "html.parser")

        title = root.findAll('h1', {'class': 'title'})
        image = root.findAll('meta', {'property': 'og:image'})[0]['content']

        if len(title) == 0:
            title = root.findAll('h2')[0]
        else:
            title = title[0]

        descriptions = root.findAll('p', {'class': 'course-description'})

        if len(descriptions) == 0:
            descriptions = root.findAll('div', {'class': 'description'})
        courses = root.findAll('div', {'class': 'course-cont'})

        if len(courses) == 0:
            courses = root.findAll('div', {'class': 'module-desc'})

        return Course(**{'title': title.text,
                         'text': clear_text(" ".join(
                             [description.text + course.text for description, course in zip(descriptions, courses)])),
                         'url': url,
                         'is_active': True,
                         'type': 'coursera',
                         'specific_id': link,
                         'image_link': image})
    except IndexError:
        pass


def update_all():
    links = download_coursera_links()
    courses = list(map(parse_coursera_link, tqdm(links, desc="Parse coursera links into courses")))
    courses = list(filter(lambda x: x, courses))
    saved = save_courses(courses)
    print("Saved %s coursera courses" % saved)

if __name__ == "__main__":
    update_all()