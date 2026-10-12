"""Interactive production setup. Password is hidden; only its salted hash is saved."""
from pathlib import Path
from getpass import getpass
import secrets, os, re
from werkzeug.security import generate_password_hash
path=Path(__file__).resolve().parent.parent/'.env'
if path.exists(): raise SystemExit('.env already exists; edit deliberately rather than overwriting secrets.')
domain=input('Domain (for example atlas.example.com): ').strip().lower()
if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?',domain) or '.' not in domain: raise SystemExit('Invalid domain')
pw=getpass('New portal password (at least 16 characters): ')
if len(pw)<16: raise SystemExit('Use at least 16 characters.')
if pw!=getpass('Confirm password: '): raise SystemExit('Passwords do not match.')
contents=f"PORTAL_DOMAIN={domain}\nPORTAL_ORIGIN=https://{domain}\nSECRET_KEY={secrets.token_hex(32)}\nPORTAL_PASSWORD_HASH='{generate_password_hash(pw)}'\n"
fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:f.write(contents)
print('Private .env created. Keep an encrypted backup; do not commit it.')
