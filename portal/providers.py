"""Private provider settings, never included in API state or exported profile data."""
import json, os, stat, math
from pathlib import Path
ALLOWED={'OPENAI_API_KEY','STUDIO_MODEL','STUDIO_MONTHLY_BUDGET_USD','RESEND_API_KEY','ATLAS_EMAIL_FROM'}
def config_path():
    return Path(os.environ.get('ATLAS_PROVIDER_CONFIG', Path(__file__).resolve().parent.parent/'private'/'providers.json'))
def settings():
    path=config_path()
    if not path.exists():return {}
    if not path.is_file() or path.is_symlink() or stat.S_IMODE(path.stat().st_mode)&0o077:
        raise ValueError('Provider configuration must be a private regular file (chmod 600)')
    data=json.loads(path.read_text())
    if not isinstance(data,dict):raise ValueError('Invalid provider configuration')
    return {k:str(v) for k,v in data.items() if k in ALLOWED}
def get(key,default=None):
    if os.environ.get('ATLAS_ZERO_COST')=='1' and key in {'OPENAI_API_KEY','RESEND_API_KEY'}:return None
    return os.environ.get(key) or settings().get(key,default)
def budget():
    value=float(get('STUDIO_MONTHLY_BUDGET_USD','2'))
    if not math.isfinite(value) or value<=0:raise ValueError('Writing budget must be a positive finite amount')
    return min(value,50)
def preflight():
    if os.environ.get('ATLAS_ZERO_COST')=='1':raise ValueError('Writing provider calls are disabled in zero-cost mode')
    import requests
    from portal.writing import RATES
    model=get('STUDIO_MODEL','gpt-6-luna');key=get('OPENAI_API_KEY')
    if model not in RATES:raise ValueError('Model has no verified price entry')
    if not key:raise ValueError('Writing key is not configured. Run python -m scripts.configure_providers writing in your own terminal.')
    r=requests.get('https://api.openai.com/v1/models/'+model,headers={'Authorization':'Bearer '+key},timeout=20)
    if r.status_code!=200:raise ValueError('Account model check failed: HTTP '+str(r.status_code))
    if r.json().get('id')!=model:raise ValueError('Provider returned a different model identifier')
    return {'model':model,'available':True,'input_usd_per_million':RATES[model][0],'output_usd_per_million':RATES[model][1], 'monthly_budget_usd':budget()}
