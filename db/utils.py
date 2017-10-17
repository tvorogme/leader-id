from db.models import session, Meta, Course
from settings import DEBUG


def save_courses(courses: list) -> int:
    to_add = len(courses)

    for course in courses:
        already_in_db = bool(len(session.query(Course).filter(Course.url == course.url).all()))
        if already_in_db:
            to_add -= 1

            if DEBUG:
                print('Course<%s> already in db, pass' % course.title)
        else:
            session.add(course)
    session.commit()
    return to_add


def update_last_parsed_stepic_page(last_page: int) -> None:
    meta = session.query(Meta).filter(Meta.id == 1).all()[0]
    meta.last_stepic_id = last_page
    session.commit()


def update_last_parsed_event_id(last_page: int) -> None:
    meta = session.query(Meta).filter(Meta.id == 1).all()[0]
    meta.last_event_id = last_page
    session.commit()


def get_open_stepic_courses() -> list:
    ids = session.query(Course.specific_id).filter(Course.type == 'stepic').filter(Course.is_active == True).all()
    return [_id[0] for _id in ids]


def get_last_stepic_page() -> int:
    return session.query(Meta).filter(Meta.id == 1).all()[0].last_stepic_id


def get_last_event_id() -> int:
    return session.query(Meta).filter(Meta.id == 1).all()[0].last_event_id


def update_stepic_states(new_states: dict):
    courses = session.query(Course).filter(Course.specific_id.in_(new_states.keys())).all()

    for course in courses:
        course.is_active = new_states[course.specific_id]

    session.commit()
    print("Update states successful")


def get_all_specific_ids(type) -> list:
    return [i[0] for i in session.query(Course.specific_id).filter(Course.type == type).all()]


def get_course(specific_id, type):
    query = session.query(Course).filter(Course.specific_id == specific_id).filter(Course.type == type).all()

    if len(query) > 0:
        return query[0]
    else:
        return None


def rollback() -> None:
    session.rollback()


def print_status() -> None:
    events = session.query(Course).filter(Course.type == 'event').count()
    specials = session.query(Course).filter(Course.type == 'special').count()
    coursera = session.query(Course).filter(Course.type == 'coursera').count()
    stepic = session.query(Course).filter(Course.type == 'stepic').count()

    status = "DB status:\n\t " \
             "Events: {}\n\t " \
             "Specials: {}\n\t " \
             "Coursera: {}\n\t " \
             "Stepic: {}".format(events,
                                 specials,
                                 coursera,
                                 stepic)

    print(status)
