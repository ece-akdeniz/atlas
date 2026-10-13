"""Prepare private native-service settings locally; never starts or exposes a server."""
import argparse,os,re,secrets
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash

def prepare(domain,password,destination,owner_email=None):
    from portal.access import normalize_email,owner
    owner_email=normalize_email(owner_email or (owner() or {}).get("email"))
    if not isinstance(domain,str) or not re.fullmatch(r'(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',domain):
        raise ValueError('Enter a public hostname only, for example atlas.your-domain.de')
    if len(password)<12:raise ValueError('Use an Atlas password of at least 12 characters')
    folder=Path(destination)
    if folder.exists():raise ValueError('Destination already exists; existing credentials will not be overwritten')
    folder.mkdir(parents=True,mode=0o700)
    values={'PORTAL_OWNER_EMAIL':owner_email,'PORTAL_ENV':'production','PORTAL_DOMAIN':domain,'PORTAL_ORIGIN':'https://'+domain,'SECRET_KEY':secrets.token_urlsafe(48),'PORTAL_PASSWORD_HASH':generate_password_hash(password),'ATLAS_PROVIDER_CONFIG':'/var/lib/atlas/provider-settings.json','PLAYWRIGHT_BROWSERS_PATH':'/var/lib/atlas/browser-cache'}
    for filename,body in [('atlas.env',''.join(k+'='+v+'\n' for k,v in values.items())),('caddy.env','PORTAL_DOMAIN='+domain+'\n')]:
        fd=os.open(folder/filename,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:f.write(body)
    return folder

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--domain',required=True);p.add_argument('--destination',default='private/production-settings');args=p.parse_args()
    from portal.access import owner
    owner_email=(owner() or {}).get('email') or input('Owner sign-in email: ').strip()
    password=getpass('Choose Atlas sign-in password (hidden, minimum 12 characters): ')
    if password!=getpass('Repeat password (hidden): '):raise SystemExit('Passwords differ; nothing saved')
    try:folder=prepare(args.domain,password,args.destination,owner_email)
    except ValueError as e:raise SystemExit(str(e))
    print('Private configuration saved in',folder,'. Transfer over SSH following PRODUCTION-RUNBOOK.md. No server started; plaintext password not saved.')
if __name__=='__main__':main()
