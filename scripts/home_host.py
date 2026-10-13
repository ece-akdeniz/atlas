"""Prepare or run a private, zero-subscription Atlas home host; never opens a port publicly."""
import argparse, json, os, plistlib, stat, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'private/home-host/settings.json'
ROLES={'web':['-m','gunicorn','--bind','127.0.0.1:18765','--workers','2','--threads','2','--timeout','60','portal.app:app'],
       'collector':['-m','portal.worker'],'documents':['-m','portal.jobs']}

def prepare(hostname, password, email, destination=CONFIG):
    import tempfile
    from scripts.configure_production import prepare as production
    if not hostname.endswith('.ts.net'):raise ValueError('Use the exact Tailscale machine hostname ending in .ts.net')
    destination=Path(destination)
    if destination.exists():raise ValueError('Home settings already exist; refusing to replace credentials')
    with tempfile.TemporaryDirectory() as tmp:
        folder=production(hostname,password,Path(tmp)/'settings',email)
        values=dict(line.split('=',1) for line in (folder/'atlas.env').read_text().splitlines())
    values.update(PORTAL_DB=str(ROOT/'data/portal.sqlite3'),ATLAS_ZERO_COST='1',
                  ATLAS_PROVIDER_CONFIG=str(ROOT/'private/providers.json'))
    values.pop('PLAYWRIGHT_BROWSERS_PATH',None)
    destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(values,f)
    return destination

def environment(config=CONFIG):
    config=Path(config)
    if config.is_symlink() or stat.S_IMODE(config.stat().st_mode)&0o077:raise ValueError('Home settings must be a private regular file (chmod 600)')
    values=json.loads(config.read_text())
    if values.get('PORTAL_ENV')!='production' or values.get('ATLAS_ZERO_COST')!='1':raise ValueError('Home hosting requires production authentication and zero-cost mode')
    return {**os.environ,**values,'PYTHONUNBUFFERED':'1','PYTHONDONTWRITEBYTECODE':'1',
            'PATH':str(ROOT/'.venv/bin')+':/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin'}

def write_agents(destination, config=CONFIG):
    environment(config) # validate first; secrets never appear in plist
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True,mode=0o700)
    logs=ROOT/'private/home-host/logs';logs.mkdir(parents=True,exist_ok=True,mode=0o700)
    for role in ROLES:
        target=destination/f'local.atlas.{role}.plist'
        if target.exists():raise ValueError('Launch agent already exists: '+str(target))
    for role in ROLES:
        body={'Label':f'local.atlas.{role}','ProgramArguments':[str(ROOT/'.venv/bin/python'),'-m','scripts.home_host','run',role,'--config',str(Path(config).resolve())],
              'WorkingDirectory':str(ROOT),'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':10,'Umask':63,
              'StandardOutPath':str(logs/(role+'.log')),'StandardErrorPath':str(logs/(role+'.error.log'))}
        target=destination/f'local.atlas.{role}.plist';target.write_bytes(plistlib.dumps(body));target.chmod(0o600)
    return destination

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    setup=sub.add_parser('configure');setup.add_argument('--hostname',required=True)
    run=sub.add_parser('run');run.add_argument('role',choices=ROLES);run.add_argument('--config',default=str(CONFIG))
    agents=sub.add_parser('agents');agents.add_argument('--destination',default=str(ROOT/'private/home-host/agents'))
    a=p.parse_args()
    if a.action=='configure':
        from getpass import getpass
        from portal.access import owner
        email=(owner() or {}).get('email') or input('Owner email: ').strip()
        password=getpass('Choose Atlas password (hidden, 12+ characters): ')
        if password!=getpass('Repeat password: '):raise ValueError('Passwords differ')
        print('Saved private settings:',prepare(a.hostname,password,email))
    elif a.action=='agents':print('Generated launch agents (not installed):',write_agents(a.destination))
    else:
        env=environment(a.config);os.chdir(ROOT);os.umask(0o077)
        os.execve(sys.executable,[sys.executable,*ROLES[a.role]],env)
if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError) as error:raise SystemExit(str(error))
