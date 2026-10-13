"""Run in your own terminal: python -m scripts.configure_providers writing|email.
Keys are read without echo and saved outside Git. No profile is sent by preflight.
"""
import argparse,json,os,tempfile
from getpass import getpass
from portal import providers

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('provider',choices=['writing','email']);args=parser.parse_args()
    data=providers.settings()
    if args.provider=='writing':
        print('OpenAI writing only. Default: gpt-6-luna, $2/month Atlas limit. Generation still requires Studio consent.')
        key=getpass('OpenAI project API key (hidden): ').strip()
        if not key or any(c.isspace() for c in key):raise SystemExit('Invalid key; nothing saved.')
        data.update(OPENAI_API_KEY=key,STUDIO_MODEL='gpt-6-luna',STUDIO_MONTHLY_BUDGET_USD='2')
    else:
        key=getpass('Resend API key (hidden): ').strip()
        sender=input('Verified sender address (for example Atlas <alerts@your-domain>): ').strip()
        if not key or '@' not in sender or '\n' in sender:raise SystemExit('Invalid settings; nothing saved.')
        data.update(RESEND_API_KEY=key,ATLAS_EMAIL_FROM=sender)
    path=providers.config_path();path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.provider-')
    try:
        with os.fdopen(fd,'w') as f:json.dump(data,f);f.write('\n')
        os.chmod(tmp,0o600);os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print('Private settings saved. Existing drafts, profile and templates are unchanged.')
    if args.provider=='writing':
        try:
            result=providers.preflight();print('Account model check passed:',result['model'])
            print('No CV content sent. No generation charge. Reload Studio to activate its existing consent flow.')
        except Exception as e:raise SystemExit('Settings saved, preflight unsuccessful: '+type(e).__name__+'. Run python -m scripts.provider_preflight for a safe status report.')
    else:print('Email credentials saved. Verify sender DNS and HTTPS origin before sending a test.')
if __name__=='__main__':main()
