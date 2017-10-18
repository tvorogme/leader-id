from time import sleep

from parsers.coursera import update_all as coursera_update_all
from parsers.events import update_all as events_update_all
from parsers.specials import update_all as specials_update_all
from parsers.stepic import update_all as stepic_update_all
from recommender.main import generate_vectors_wrapper
from utils.threadering import threaded


def update_all():
    coursera_update_all()
    events_update_all()
    stepic_update_all()
    specials_update_all()


@threaded
def update_all_wapper():
    while True:
        sleep(24 * 60 * 60)
        update_all()
        generate_vectors_wrapper()
