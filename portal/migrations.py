"""Additive versioned migration. Personal databases are backed up before schema edits."""
import json,sqlite3
from portal import db

def upgrade():
    if db.get_meta('studio_schema')==1:return
    with db.connect() as c:
        if c.execute('SELECT count(*) FROM opportunities').fetchone()[0] and not str(db.DB_PATH).startswith('/tmp/'):
            dest=db.DB_PATH.parent/'backups'/('before-studio-schema-'+db.now().replace(':','').replace('+','_')+'.sqlite3');dest.parent.mkdir(exist_ok=True)
            backup=sqlite3.connect(dest)
            try:c.backup(backup)
            finally:backup.close()
            dest.chmod(0o600)
        c.executescript('''
        CREATE TABLE IF NOT EXISTS uploads(id TEXT PRIMARY KEY,kind TEXT NOT NULL,name TEXT NOT NULL,hash TEXT NOT NULL,metadata TEXT NOT NULL,created TEXT NOT NULL,UNIQUE(kind,hash));
        CREATE TABLE IF NOT EXISTS profile_versions(id INTEGER PRIMARY KEY,profile TEXT NOT NULL,changes TEXT NOT NULL,upload_id TEXT,created TEXT NOT NULL,undone INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS studio_projects(id TEXT PRIMARY KEY,data TEXT NOT NULL,created TEXT NOT NULL,updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS studio_documents(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES studio_projects(id) ON DELETE CASCADE,kind TEXT NOT NULL,source TEXT NOT NULL,metadata TEXT NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kind TEXT NOT NULL,data TEXT NOT NULL,status TEXT NOT NULL,created TEXT NOT NULL,started TEXT,finished TEXT,result TEXT NOT NULL DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS notification_events(id TEXT PRIMARY KEY,opportunity_id TEXT NOT NULL,fingerprint TEXT NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,next_due TEXT,provider_id TEXT,created TEXT NOT NULL,sent TEXT,error TEXT,UNIQUE(opportunity_id,fingerprint));
        CREATE TABLE IF NOT EXISTS model_usage(id TEXT PRIMARY KEY,month TEXT NOT NULL,model TEXT NOT NULL,reserved REAL NOT NULL,actual REAL,status TEXT NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS generation_cache(hash TEXT PRIMARY KEY,output TEXT NOT NULL,model TEXT NOT NULL,prompt_version TEXT NOT NULL,created TEXT NOT NULL);
        ''')
    db.set_meta('studio_schema',1)
