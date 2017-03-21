
from app import db
from migrate.versioning import api
from app import app
import imp

SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_MIGRATE_REPO=app.config['SQLALCHEMY_MIGRATE_REPO']
v=api.db_version(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
migration=SQLALCHEMY_MIGRATE_REPO+('/versions/%03d_migration.py'%(v+1))
tmp=imp.new_module('old_module')
old_module=api.create_model(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
exec(old_module,tmp.__dict__)
script=api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO,tmp.meta,db.metadata)
open(migration,"wt").write(script)
api.upgrade(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
print('Migration script saved as '+migration)
print('Version: '+str(api.db_version(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)))
