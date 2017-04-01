from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
reminders = Table('reminders', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('senderID', String(length=50)),
    Column('reminder_text', String(length=100)),
    Column('reminder_time', String(length=50)),
    Column('reminded', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['reminders'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['reminders'].drop()
