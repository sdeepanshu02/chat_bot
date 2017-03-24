from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
book_issue = Table('book_issue', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('book_id', String(length=30)),
    Column('stu_roll_no', String(length=40)),
    Column('issue_date', DateTime),
    Column('due_date', DateTime),
    Column('reminded', Boolean),
)

lib_books = Table('lib_books', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('book_id', String(length=30)),
    Column('book_name', String(length=60)),
    Column('author_name', String(length=45)),
    Column('price', Float),
    Column('no_of_copies', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['book_issue'].create()
    post_meta.tables['lib_books'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['book_issue'].drop()
    post_meta.tables['lib_books'].drop()
