"""Independent background process. No browser, chat, or model required."""
import argparse, json, time, signal, sqlite3
from datetime import datetime, timezone
from portal import db
from portal.seed import bootstrap
from portal.collector import refresh

def backup():
    folder=db.DB_PATH.parent/'backups'; folder.mkdir(exist_ok=True)
    target=folder/(datetime.now(timezone.utc).strftime('%Y-%m-%d')+'.sqlite3')
    with db.connect() as src, sqlite3.connect(target) as dest: src.backup(dest)
    target.chmod(0o600)
    for old in sorted(folder.glob('*.sqlite3'))[:-7]: old.unlink()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--once',action='store_true'); p.add_argument('--backup',action='store_true'); args=p.parse_args()
    bootstrap()
    from portal.migrations import upgrade
    upgrade()
    if args.backup: backup(); return
    if args.once: print(json.dumps(refresh())); return
    running=True
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    last_backup=None
    while running:
        db.set_meta('worker_heartbeat',db.now())
        try:
            with db.connect() as c:request_ids=[r['id'] for r in c.execute("SELECT id FROM requests WHERE status='queued'")]
            results=refresh(force=bool(request_ids))
            if results: print(json.dumps({'at':db.now(),'result':results}),flush=True)
            if not isinstance(results,dict) or results.get('status')!='busy':
                with db.connect() as c:
                    for identity in request_ids:c.execute("UPDATE requests SET status='processed' WHERE id=?",(identity,))
            from portal.notifications import discover,deliver
            discover();deliver()
            day=db.now()[:10]
            if day!=last_backup:
                backup()
                from scripts.backup import backup as complete_backup
                folder=db.DB_PATH.parent/'backups';complete_backup(folder/(day+'-complete.tar.gz'))
                for old in sorted(folder.glob('*-complete.tar.gz'))[:-7]:old.unlink()
                last_backup=day
        except Exception as e: print(json.dumps({'error':str(e),'at':db.now()}),flush=True)
        for _ in range(60):
            if not running: break
            time.sleep(1)
if __name__=='__main__': main()
