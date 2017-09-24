from functools import partial

import sqlalchemy
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import String, Integer, Boolean, PickleType, Text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

Column = partial(Column, nullable=False)
db_url = 'postgresql+psycopg2://postgres@localhost:5432/leaderid'
engine = None


def get_connector():
    global engine
    engine = sqlalchemy.create_engine(db_url, client_encoding='utf8', server_side_cursors=True)
    return engine.engine.connect()


con = get_connector()

session_factory = sessionmaker(bind=con)
Session = scoped_session(session_factory)
session = Session()

Base = declarative_base(bind=con)

similar = Table(
    'friendships', Base.metadata,
    Column('friend_a_id', Integer, ForeignKey('course.id'),
           primary_key=True),
    Column('friend_b_id', Integer, ForeignKey('course.id'),
           primary_key=True)
)


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    title = Column(String)
    image_link = Column(String, nullable=True)
    is_active = Column(Boolean)
    url = Column(String, unique=True)
    type = Column(String)
    specific_id = Column(String, nullable=True)
    vector = Column(PickleType, nullable=True)

    # this relationship is used for persistence
    similars = relationship("Course", secondary=similar,
                            primaryjoin=id == similar.c.friend_a_id,
                            secondaryjoin=id == similar.c.friend_b_id,
                            )


class Meta(Base):
    __tablename__ = 'parsers_meta'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_stepic_id = Column(Integer)
    last_event_id = Column(Integer)


def create_tables():
    for item in [Course, Meta, similar]:
        try:
            if item != similar:
                getattr(item, "__table__").create(engine)

                if item == Meta:
                    con.execute(Meta.__table__.insert(), {'last_stepic_id': 1, 'last_event_id': 1000})
            else:
                similar.create()

        except ProgrammingError:
            if item != similar:
                print("\n %s table already exist" % item.__tablename__)
            else:
                print('similar table already exist')


if __name__ == "__main__":
    create_tables()
