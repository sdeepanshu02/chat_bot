from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
prev_papers = Table('prev_papers', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('dept_name', String(length=100)),
    Column('year', String(length=5)),
    Column('semester', String(length=2)),
    Column('subject', String(length=40)),
    Column('exam_type', String(length=20)),
    Column('url', String(length=100)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['prev_papers'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['prev_papers'].drop()
