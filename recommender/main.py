from collections import Counter

import numpy as np
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from db.models import session, Course
from settings import STOP_WORDS_COUNT
from utils.threadering import threaded

generate_vectors_lock = False


def generate_vectors():
    global generate_vectors_lock

    to_delete_courses = []

    if not generate_vectors_lock:
        generate_vectors_lock = True

        print("Start generating vectors")
        courses = session.query(Course).all()
        print("Old len of courses was {}".format(len(courses)))

        blacklist = open('blacklist.txt').read().split()

        for course in courses:
            text_displayed = course.text + course.title

            for black_item in blacklist:
                if black_item in text_displayed:
                    to_delete_courses.append(course)

        courses = list(filter(lambda x: x not in to_delete_courses, courses))
        print("New len of courses is {}".format(len(courses)))

        text = [course.text if course.text is not None else "" for course in courses]
        stop_words = [i[0] for i in Counter(" ".join(text).split(" ")).most_common(STOP_WORDS_COUNT)]
        vectorizer = TfidfVectorizer(stop_words=stop_words)
        vectorizer_answer = vectorizer.fit_transform(text).toarray()

        for course, vector in tqdm(zip(courses, vectorizer_answer), desc="Update course information"):
            course.vector = vector

        session.commit()
        generate_vectors_lock = False

        return to_delete_courses


def update_similars(specific_id=None, to_delete_courses=None):
    print(specific_id, type(specific_id))

    if specific_id:
        to_update = session.query(Course).filter(Course.specific_id == specific_id).all()
    else:
        to_update = session.query(Course).filter(Course.type.in_(['event', 'special'])).all()

    to_recommend = session.query(Course).filter(~Course.type.in_(['event', 'special'])).all()

    to_update = list(filter(lambda course: course not in to_delete_courses, to_update))
    to_recommend = list(filter(lambda course: course not in to_delete_courses, to_recommend))

    for update_item in tqdm(to_update, desc="Update similar in db"):
        recommend = []
        similarity = []

        for recommend_item in to_recommend:
            similarity.append(cosine(update_item.vector, recommend_item.vector))

        for index in np.asarray(similarity).argsort()[:10]:
            recommend.append(to_recommend[index])

        update_item.similars = recommend

    session.commit()

    for item in to_delete_courses:
        session.delete(item)

    session.commit()

    print("Deleted {}".format(len(to_delete_courses)))


@threaded
def generate_vectors_wrapper(specific_id=None):
    global to_delete_courses

    to_delete_courses = generate_vectors()
    update_similars(specific_id, to_delete_courses=to_delete_courses)


if __name__ == "__main__":
    generate_vectors_wrapper()
