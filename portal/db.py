import os, sqlite3, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get('PORTAL_DB', str(ROOT / 'data/portal.sqlite3')))
def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
class Connection(sqlite3.Connection):
    def __exit__(self,*args):
        try: return super().__exit__(*args)
        finally: self.close()

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=30, factory=Connection)
    os.chmod(DB_PATH,0o600)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS opportunities(id TEXT PRIMARY KEY, canonical TEXT UNIQUE NOT NULL, data TEXT NOT NULL, discovered TEXT NOT NULL, verified TEXT, changed TEXT, hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE, source_id TEXT NOT NULL, url TEXT NOT NULL, verified TEXT NOT NULL, PRIMARY KEY(opportunity_id,source_id));
        CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, data TEXT NOT NULL, last_attempt TEXT, last_success TEXT, error TEXT, failures INTEGER NOT NULL DEFAULT 0, next_due TEXT);
        CREATE TABLE IF NOT EXISTS workflow(opportunity_id TEXT PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE, stage TEXT, notes TEXT NOT NULL DEFAULT '', dismissed INTEGER NOT NULL DEFAULT 0, updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS changes(id INTEGER PRIMARY KEY, opportunity_id TEXT REFERENCES opportunities(id) ON DELETE CASCADE, at TEXT NOT NULL, fields TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, started TEXT NOT NULL, finished TEXT, status TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS cache(url TEXT PRIMARY KEY, hash TEXT NOT NULL, etag TEXT, modified TEXT, version TEXT NOT NULL, data TEXT NOT NULL, checked TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, created TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS login_attempts(ip TEXT NOT NULL, at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS locks(name TEXT PRIMARY KEY, until INTEGER NOT NULL);
        ''')
        columns={r['name'] for r in c.execute('PRAGMA table_info(workflow)')}
        if 'bookmarked' not in columns:
            c.execute('ALTER TABLE workflow ADD COLUMN bookmarked INTEGER NOT NULL DEFAULT 0')
            c.execute('UPDATE workflow SET bookmarked=1 WHERE stage IS NOT NULL')
        c.execute("INSERT INTO meta VALUES('schema_version','2') ON CONFLICT(key) DO UPDATE SET value='2'")

    migrate_taxonomy()

def migrate_taxonomy():
    # Representation-only migration: preserve discovery, verification and workflow.
    from portal.taxonomy import normalize, VERSION
    with connect() as c:
        for row in c.execute('SELECT id,data FROM opportunities').fetchall():
            old=json.loads(row['data']); current=normalize(old)
            if old==current: continue
            body=json.dumps(current,sort_keys=True,ensure_ascii=False)
            c.execute('UPDATE opportunities SET data=?,hash=? WHERE id=?',(body,hashlib.sha256(body.encode()).hexdigest(),row['id']))
        searches=c.execute("SELECT value FROM meta WHERE key='saved_searches'").fetchone()
        if searches:
            items=json.loads(searches[0]);changed=False
            for item in items:
                filters=item.get('filters',{});value=filters.get('type','')
                if value.lower() in ['full-time','full-time role','part-time','part-time role']:
                    filters['workload']='Part-time' if value.lower().startswith('part') else 'Full-time';filters.pop('type');changed=True
                elif value:
                    labels=normalize({'type':value})['types']
                    if len(labels)==1 and labels[0]!='Unspecified' and value!=labels[0]:filters['type']=labels[0];changed=True
            if changed:c.execute("UPDATE meta SET value=? WHERE key='saved_searches'",(json.dumps(items,ensure_ascii=False),))
        c.execute("INSERT INTO meta VALUES('taxonomy_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(json.dumps(VERSION),))

def get_meta(key, default=None):
    with connect() as c: row=c.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
    return json.loads(row['value']) if row else default

def set_meta(key,value):
    with connect() as c: c.execute('INSERT INTO meta VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value,ensure_ascii=False)))

def rows():
    from portal.taxonomy import normalize
    with connect() as c:
        values=c.execute('SELECT o.*,w.stage,w.notes,w.dismissed,w.bookmarked FROM opportunities o LEFT JOIN workflow w ON o.id=w.opportunity_id').fetchall()
        evidence=c.execute('SELECT * FROM evidence').fetchall()
    return [{**normalize(json.loads(r['data'])),'id':r['id'],'discovered':r['discovered'],'verified':r['verified'],'changed':r['changed'],'stage':r['stage'],'notes':r['notes'] or '', 'bookmarked':bool(r['bookmarked']), 'dismissed':bool(r['dismissed']), 'sources':[dict(e) for e in evidence if e['opportunity_id']==r['id']]} for r in values]

def sources():
    with connect() as c: values=c.execute('SELECT * FROM sources ORDER BY id').fetchall()
    return [{**json.loads(r['data']),**{k:r[k] for k in r.keys() if k!='data'}} for r in values]

def upsert(record, source_id, verified=None):
    from portal.model import validate, canonical_url
    validate(record)
    from portal.taxonomy import normalize
    record=normalize(record)
    record.setdefault('field_evidence',{k:{'url':record['url'],'method':record.get('evidence_method','Source extraction'),'version':record.get('extraction_version','unknown')} for k,v in record.items() if v is not None and k not in ['field_evidence','questions','extraction_scope']})
    verified=verified or now()
    changed_at=now()
    key=canonical_url(record.get('identity_url') or record['url'])
    # Explicit publisher IDs avoid fuzzy merges across distinct research projects.
    if record.get('publisher_id'): key=record['organization'].lower()+'|'+record['publisher_id']
    identity=hashlib.sha256(key.encode()).hexdigest()[:24]
    body=json.dumps(record,sort_keys=True,ensure_ascii=False)
    digest=hashlib.sha256(body.encode()).hexdigest()
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        previous=c.execute('SELECT * FROM opportunities WHERE canonical=?',(key,)).fetchone()
        # Publisher-issued cross-platform identity, never fuzzy title similarity.
        if not previous and record.get('publisher_identifiers'):
            identifiers=record['publisher_identifiers']
            for candidate in c.execute('SELECT * FROM opportunities').fetchall():
                known=json.loads(candidate['data']).get('publisher_identifiers',{})
                if any(value and known.get(kind)==value for kind,value in identifiers.items() if kind in ['sirop','breezy']):
                    previous=candidate;break
        if previous:
            old_record=json.loads(previous['data'])
            for field in ['required','deadline','hours']:
                # Different publishers disagree: retain both versions as explicit evidence.
                if old_record.get('publisher') and record.get('publisher')!=old_record.get('publisher') and old_record.get(field) and record.get(field) and old_record[field]!=record[field]:
                    record.setdefault('field_states',{})[field]={'state':'conflict','values':[old_record[field],record[field]]}
            body=json.dumps(record,sort_keys=True,ensure_ascii=False);digest=hashlib.sha256(body.encode()).hexdigest()
        if previous:
            identity=previous['id']
            if previous['hash']!=digest:
                old=json.loads(previous['data']); changes={k:{'before':old.get(k),'after':record.get(k)} for k in set(old)|set(record) if old.get(k)!=record.get(k)}
                c.execute('INSERT INTO changes(opportunity_id,at,fields) VALUES(?,?,?)',(identity,changed_at,json.dumps(changes)))
                c.execute('UPDATE opportunities SET data=?,hash=?,verified=?,changed=? WHERE id=?',(body,digest,verified,changed_at,identity))
            else: c.execute('UPDATE opportunities SET verified=? WHERE id=?',(verified,identity))
        else: c.execute('INSERT INTO opportunities VALUES(?,?,?,?,?,?,?)',(identity,key,body,now(),verified,None,digest))
        c.execute('INSERT INTO evidence VALUES(?,?,?,?) ON CONFLICT(opportunity_id,source_id) DO UPDATE SET url=excluded.url,verified=excluded.verified',(identity,source_id,record['url'],verified))
    return identity
