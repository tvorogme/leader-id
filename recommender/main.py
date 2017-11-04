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
    if not generate_vectors_lock:
        generate_vectors_lock = True

        print("Start generating vectors")
        courses = session.query(Course).all()

        text = [course.text if course.text is not None else "" for course in courses] + open(
            'stopwords.txt').read().split()
        stop_words = [i[0] for i in Counter(" ".join(text).split(" ")).most_common(STOP_WORDS_COUNT)]
        vectorizer = TfidfVectorizer(stop_words=stop_words)
        vectorizer_answer = vectorizer.fit_transform(text).toarray()

        for course, vector in tqdm(zip(courses, vectorizer_answer), desc="Update course information"):
            course.vector = vector

        session.commit()

        generate_vectors_lock = False


def update_similars(specific_id=None):
    print(specific_id, type(specific_id))

    if specific_id:
        to_update = session.query(Course).filter(Course.specific_id == specific_id).all()
    else:
        to_update = session.query(Course).filter(Course.type.in_(['event', 'special'])).all()

    to_recommend = session.query(Course).filter(~Course.type.in_(['event', 'special'])).all()

    for update_item in tqdm(to_update, desc="Update similar in db"):
        recommend = []
        similarity = []

        for recommend_item in to_recommend:
            similarity.append(cosine(update_item.vector, recommend_item.vector))

        for index in np.asarray(similarity).argsort()[:10]:
            recommend.append(to_recommend[index])

        update_item.similars = recommend

    session.commit()


@threaded
def generate_vectors_wrapper(specific_id=None):
    generate_vectors()
    update_similars(specific_id)


if __name__ == "__main__":
    generate_vectors_wrapper()
