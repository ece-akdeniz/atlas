"""Scan staged blobs only; never print matching secret values."""
import re,subprocess,sys
files=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z']).decode().split('\0')
patterns={'OpenAI credential':r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}','GitHub credential':r'gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}','AWS access credential':r'AKIA[0-9A-Z]{16}','private key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','Resend credential':r're_[A-Za-z0-9]{24,}','OpenVSX credential':r'ovsx_[A-Za-z0-9_-]{15,}'}
errors=[]
for path in filter(None,files):
 if path=='.env.example' or path=='data/.gitkeep':continue
 if re.search(r'(^|/)(?:\.env(?:\.|$)|private/|uploads/|backups/|\.venv/)|\.(?:sqlite\w*|pdf|tex|zip|pem|key|p12|pfx)$',path):errors.append((path,'private/local file'));continue
 content=subprocess.check_output(['git','show',':'+path]).decode(errors='ignore')
 for label,pattern in patterns.items():
  if re.search(pattern,content):errors.append((path,label))
if errors:
 for path,label in errors:print('Blocked:',path,'—',label,'(value hidden)',file=sys.stderr)
 sys.exit(1)
print('Staged-file privacy checks passed. Provider-specific secret scanning remains necessary.')
