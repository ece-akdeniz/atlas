"""Consistent SQLite snapshot plus private application assets; no secrets in Git."""
import argparse,sqlite3,tarfile,tempfile,os
from pathlib import Path
from portal import db

def backup(destination):
 destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='atlas-backup-') as tmp:
  snapshot=Path(tmp)/'portal.sqlite3'
  with db.connect() as source:
   target=sqlite3.connect(snapshot)
   try:source.backup(target)
   finally:target.close()
  with tarfile.open(destination,'w:gz') as archive:
   archive.add(snapshot,arcname='portal.sqlite3')
   private=db.DB_PATH.parent/'private'
   if private.exists():archive.add(private,arcname='private')
 destination.chmod(0o600);return destination

def restore(archive,destination):
 destination=Path(destination)
 if destination.exists() and any(destination.iterdir()):raise ValueError('Restore destination must be empty; stop services and use a fresh directory')
 destination.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive,'r:gz') as source:
  members=source.getmembers()
  if any(m.issym() or m.islnk() or m.name.startswith('/') or '..' in Path(m.name).parts for m in members):raise ValueError('Unsafe backup path')
  source.extractall(destination,filter='data')
 c=sqlite3.connect(destination/'portal.sqlite3')
 try:
  if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Restored database integrity check failed')
 finally:c.close()
 for path in destination.rglob('*'):path.chmod(0o700 if path.is_dir() else 0o600)
 return destination
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','restore']);p.add_argument('path');p.add_argument('--destination');a=p.parse_args()
 if a.action=='restore':
  if not a.destination:p.error('--destination is required for restore')
  print(restore(a.path,a.destination))
 else:print(backup(a.path))
