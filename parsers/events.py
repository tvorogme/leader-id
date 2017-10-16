import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from db.models import Course
from db.utils import get_last_event_id, update_last_parsed_event_id, save_courses, get_all_specific_ids
from utils.text import clear_text

last_id = get_last_event_id()
already_parsed_events = get_all_specific_ids('event')


def fetch_information_by_url(_id):
    url = "https://leader-id.ru/event/%s/" % _id
    request = requests.get(url)

    if request.status_code == 404:
        return None
    else:
        pass

    html = request.text
    root = BeautifulSoup(html, "html.parser")

    # Get header
    header = root.findAll('h1', {'class': 'title-lg'})

    if len(header) == 0:
        return None

    header = header[0].text

    # Get main text
    text = root.findAll('div', {'class': 'program'})

    if len(text) == 0:
        return None

    text = text[0].text

    return Course(**{'title': header,
                     'text': clear_text(" ".join([header, text])),
                     'url': url, 'is_active': True,
                     'type': 'event',
                     'specific_id': _id})


def update_all():
    all_courses = []

    if last_id == 1000:
        max_id = tqdm(range(1000, 5777))
    else:
        max_id = tqdm(range(last_id + 1, last_id + 101))

    for i in max_id:
        if i not in already_parsed_events:
            info = fetch_information_by_url(i)

            if info is not None:
                all_courses.append(info)

            max_id.set_description('Have been parsed %s leaderid events' % len(all_courses))
    if len(all_courses) > 0:
        update_last_parsed_event_id(max([i.specific_id for i in all_courses]))

    saved = save_courses(all_courses)
    print("Saved %s leader-id events" % saved)
