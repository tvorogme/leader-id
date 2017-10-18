import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from db.models import Course
from db.utils import save_courses
from utils.parser import mozilla_headers
from utils.text import text_sum


def parse_openedu(data: list):
    answer = {}
    answer['title'] = data[0]

    # Get half of url
    url = data[1]
    answer['specific_id'] = url

    # Made normal url
    url = 'https://openedu.ru%s' % url
    # Save it
    answer['url'] = url

    # Parse course by url
    html = requests.get(url, headers=mozilla_headers)

    # BS it
    root = BeautifulSoup(html.content.decode(), "html.parser")

    # Get div with text
    needed_div = root.findAll('div', {'class': 'col-sm-8 issue'})[0]

    # Append text to data
    answer['text'] = text_sum([i.text for i in needed_div.findAll('p')])

    # Find photo
    photo = root.findAll('meta', {'property': 'og:image'})

    if len(photo) > 0:
        photo = photo[0]['content']
        answer['image_link'] = photo
    else:
        answer['image_link'] = None

    answer['type'] = 'openedu'
    answer['is_active'] = True

    return Course(**answer)


def update_all():
    courses = open('data/courses.json').read()
    courses = eval(courses[:-1].replace('false', 'False').replace('true', 'True'))

    titles = []
    urls = []

    for i in courses:
        titles.append(courses[i]['title'])
        urls.append(courses[i]['url'])

    data = []

    for title, url in zip(titles, urls):
        data.append([title, url])

    data = list(map(parse_openedu, tqdm(data, desc="Openedu parse")))
    data = list(filter(lambda x: x, data))
    save_courses(data)


if __name__ == '__main__':
    update_all()
