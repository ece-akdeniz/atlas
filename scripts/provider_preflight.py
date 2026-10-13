"""Verify account model access without sending any CV or posting content."""
import os,requests
from portal.writing import RATES
model=os.getenv('STUDIO_MODEL','gpt-6-luna')
if model not in RATES:raise SystemExit('Model has no verified price entry')
key=os.getenv('OPENAI_API_KEY')
if not key:raise SystemExit('OPENAI_API_KEY is not configured')
r=requests.get('https://api.openai.com/v1/models/'+model,headers={'Authorization':'Bearer '+key},timeout=20)
if r.status_code!=200:raise SystemExit('Account model availability check failed: HTTP '+str(r.status_code))
print('Model available to this account:',r.json().get('id'))
print('No profile data sent and no generation request made. Test writing quality separately.')
