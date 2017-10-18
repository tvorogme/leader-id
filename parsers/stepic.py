import json

import requests
from tqdm import tqdm

from db.utils import *
from utils.parser import mozilla_headers
from utils.stepik_api import get_token
from utils.text import clear_text

get_course_url = lambda x: "https://stepik.org/course/%s/" % x
already_in_db_ids = get_all_specific_ids('stepic')


def get_data(page: int) -> list:
    api_url = 'https://stepik.org/api/courses?page=%s' % page
    html = requests.get(api_url, headers={'Authorization': 'Bearer ' + get_token()}).text
    course = json.loads(html)
    return [course['courses'], course['meta']['has_next']]


def parse_new_state_for_stepic_course(_id):
    html = requests.get("https://stepik.org/api/courses/%s/" % _id, headers=mozilla_headers).text
    html = json.loads(html)
    return html['courses'][0]['is_active']


def parse_course(course: dict):
    text = course['course_format'] + " "
    text += course['description'] + " "
    text += course['certificate'] + " "
    text += course['requirements'] + " "
    text += course['summary'] + " "
    text += course['target_audience'] + " "
    text += course['title'] + " "

    text = clear_text(text)

    if course['cover']:
        image = 'https://stepik.org{}'.format(course['cover'])
    else:
        image = None

    if len(course['title']) < 3 or len(text) < 5:
        return None

    return Course(**{'text': text, 'title': course['title'], 'is_active': course['is_active'],
                     'url': get_course_url(course['id']), 'type': 'stepic', 'specific_id': course['id'],
                     'image_link': image})


def download_from_page(page_number: int):
    flag = True
    whole_data = []
    pbar = tqdm(desc="Download stepic dataset")

    while flag:
        current_data = get_data(page_number)
        data = current_data[0]
        data = list(filter(lambda x: x['id'] not in already_in_db_ids, data))
        whole_data += list(map(parse_course, data))
        pbar.update(1)
        page_number += 1
        flag = current_data[1]

    whole_data = list(filter(lambda x: x, whole_data))
    added_courses = save_courses(whole_data)
    print("Saved %s stepic courses" % added_courses)


def update_courses_states():
    open_courses = get_open_stepic_courses()
    new_states = list(map(parse_new_state_for_stepic_course, tqdm(open_courses, desc="Update stepic states")))
    update_stepic_states({x: y for x, y in zip(open_courses, new_states)})


def update_all():
    page_number = get_last_stepic_page()
    download_from_page(page_number)


if __name__ == "__main__":
    download_from_page(1)
