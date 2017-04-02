from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
daily_time_table = Table('daily_time_table', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('department', String(length=5)),
    Column('year', String(length=4)),
    Column('semester', String(length=4)),
    Column('day_of_week', Integer),
    Column('subjects', String(length=100)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['daily_time_table'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['daily_time_table'].drop()
