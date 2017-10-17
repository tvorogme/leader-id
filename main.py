from db.models import create_tables

if __name__ == "__main__":
    # # Init database
    create_tables()

    from api.main import run_api

    run_api()

    from parsers.all import update_all_wapper, update_all

    # Update
    update_all()

    from recommender.main import generate_vectors, update_similars

    # Generate vectors
    generate_vectors()
    update_similars()

    # Generate thread with dataset update
    update_all_wapper()

    from db.utils import print_status

    print_status()
