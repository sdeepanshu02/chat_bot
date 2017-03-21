from migrate.versioning import api
from app import app
from app import db
import os.path

db.create_all()
SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_MIGRATE_REPO=app.config['SQLALCHEMY_MIGRATE_REPO']
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO,'data_repo')
    api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO,api.version(SQLALCHEMY_MIGRATE_REPO))
