from flask import Flask, request, jsonify

from db.models import Course
from db.utils import save_courses, get_course
from recommender.main import generate_vectors_wrapper
from settings import DEBUG, PORT, HOST

app = Flask(__name__)


def get_url(type: str, specific_id: str) -> str:
    if type == 'special':
        return "https://leader-id.ru/specials/{}/".format(specific_id)
    elif type == 'event':
        return "https://leader-id.ru/event/{}/".format(specific_id)


def check_and_parse(json) -> dict:
    for field in ['title', 'type', 'specific_id', 'text']:
        if field not in json:
            return {"error": {"code": 1, "field": field, "message": "Specify %s field" % field}}

    title = json['title']
    specific_id = json['specific_id']
    text = json['text']

    for name, var in zip(['title', 'specific_id', 'text'], [title, specific_id, text]):
        if not isinstance(var, str):
            return {"error": {"code": 2, "field": name, "message": "%s id is not string" % name}}
    type = json['type']
    if type not in ['event', 'special']:
        return {"error": {"code": 2, "field": "type", "message": "Type is not event or special"}}

    return {'title': title, 'text': text, 'url': get_url(type, specific_id), 'is_active': True, 'type': type,
            'specific_id': specific_id}


@app.route('/api/add/', methods=['POST'])
def add_course():
    answer = check_and_parse(request.json)

    if 'error' in answer:
        return jsonify(answer)

    save_courses([Course(**answer)])

    generate_vectors_wrapper(answer['specific_id'])

    return jsonify({"response": 1})


@app.route('/api/recommendations/', methods=['POST'])
def get_recommendation():
    json = request.json

    for field in ['specific_id', 'type']:
        if field not in json:
            return {"error": {"code": 1, "field": field, "message": "Specify %s field" % field}}

    course = get_course(json['specific_id'], json['type'])

    if not course:
        return jsonify({"error": {"code": 3, "message": "No courses with such type and specific id"}})

    answer = {'items': []}
    for i in course.similars:
        tmp = {'title': i.title, 'url': i.url, 'type': i.type}

        if i.image_link:
            tmp['image'] = i.image_link

        answer['items'].append(tmp)

    return jsonify(answer)


def run_api():
    app.run(debug=DEBUG, port=PORT, host=HOST)
