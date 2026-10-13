"""One private owner; no registration or multi-tenant authorization is exposed."""
import hashlib,os,re
from portal import db

def normalize_email(value):
    email=str(value or '').strip().casefold()
    if not re.fullmatch(r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9.-]+\.[a-z]{2,63}",email):
        raise ValueError('Enter a valid owner email address')
    return email

def owner():
    saved=db.get_meta('owner_account',{})
    email=os.environ.get('PORTAL_OWNER_EMAIL') or saved.get('email')
    if not email:return None
    email=normalize_email(email)
    return {'id':hashlib.sha256(email.encode()).hexdigest(),'email':email,'name':saved.get('name','Owner')}

def set_owner(email,name):
    email=normalize_email(email)
    previous=db.get_meta('owner_account')
    if previous and previous.get('email')!=email:raise ValueError('Owner already configured; explicit account migration required')
    account={'email':email,'name':str(name),'created':(previous or {}).get('created',db.now())}
    db.set_meta('owner_account',account)
    return account
