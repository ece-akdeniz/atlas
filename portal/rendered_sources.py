"""Bounded public-page rendering for two explicitly registered JavaScript sources.
No login, cookies from user browsers, CAPTCHA solving, stealth flags or private APIs.
"""
import os,sys,re
from urllib.parse import urlsplit
from pathlib import Path
from bs4 import BeautifulSoup
PAGES={'aionic-rendered':('https://aioniclabs.notion.site/team-careers',r'Open roles in Zurich'), 'robotum-rendered':('https://www.robotum.info/events',r'Upcoming & Past Events')}
def render(adapter,url):
    from portal.collector import robots,safe_url,SourceError,AGENT
    if adapter not in PAGES or url!=PAGES[adapter][0]:raise SourceError('Rendered source is not explicitly registered')
    robots(url)
    try:from playwright.sync_api import sync_playwright
    except ImportError:raise SourceError('Public renderer missing: install requirements-rendering.lock and Chromium')
    origin=urlsplit(url).hostname
    allowed={origin,'www.notion.so','www.notion.com','notion.so','notion.com'} if adapter=='aionic-rendered' else {origin}
    suffixes=('.notion-static.com','.notion.site','.notion.com','.notion.so') if adapter=='aionic-rendered' else ('.supabase.co',)
    with sync_playwright() as p:
        options={'headless':True,'chromium_sandbox':True}
        if sys.platform=='darwin' and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():options['channel']='chrome'
        browser=p.chromium.launch(**options)
        try:
            context=browser.new_context(accept_downloads=False,service_workers='block')
            page=context.new_page();requests=0;blocked=set();validated=set();errors=[]
            def route(req):
                nonlocal requests
                requests+=1;request=req.request;host=urlsplit(request.url).hostname or ''
                if request.resource_type in ['image','media','font']:return req.abort()
                if requests>220 or not (host in allowed or any(host.endswith(s) for s in suffixes)):
                    blocked.add(host);return req.abort()
                try:
                    if host not in validated:safe_url(request.url);validated.add(host)
                except Exception:
                    errors.append(host);return req.abort()
                return req.continue_()
            page.route('**/*',route)
            response=page.goto(url,wait_until='domcontentloaded',timeout=45000)
            if not response or response.status>=400:raise SourceError('Rendered source returned HTTP '+str(response.status if response else 'unknown'))
            try:page.get_by_text(re.compile(PAGES[adapter][1],re.I)).first.wait_for(timeout=30000)
            except Exception:
                raise SourceError('Rendered content unavailable. Title: '+page.title()[:80]+'; blocked asset hosts: '+', '.join(sorted(blocked))+'; validation failures: '+', '.join(sorted(set(errors)))+'; page: '+page.locator('body').inner_text()[:350])
            # Wait for the page's own public event request; a shell with zero counters is not a complete feed.
            if adapter=='robotum-rendered':
                page.wait_for_load_state('networkidle',timeout=25000)
            # Read only the rendered public document; scripts/tokens are never cached.
            text=page.locator('body').inner_text()
            if re.search(r'verify you are human|checking your browser|captcha|sign in to continue',text,re.I):raise SourceError('Source requires access verification; renderer stopped')
            raw=page.content()
            soup=BeautifulSoup(raw,'html.parser')
            for x in soup.select('script,style,link,meta,noscript'):x.decompose()
            raw=str(soup)
            if len(raw.encode())>2_000_000:raise SourceError('Rendered content exceeds 2 MB limit')
            return raw
        finally:browser.close()


def robotum_records(raw,url):
    """Public rendered index. Fail closed on a shell, malformed dates or truncation."""
    from datetime import datetime,date
    from urllib.parse import urljoin
    from portal.adapters import base,evidence
    from portal.model import tags,validate
    soup=BeautifulSoup(raw,'html.parser');cards=soup.select('article');seen=set();records=[]
    if not cards:raise ValueError('Event cards not loaded; cannot confirm an empty event feed')
    if re.search(r'load more|next page',soup.get_text(' ',strip=True),re.I):raise ValueError('Event pagination requires review; previous records retained')
    for card in cards:
        a=card.select_one('a[href^="/events/"]');h=card.find('h3');ps=card.find_all('p')
        if not a or not h or len(ps)<3:raise ValueError('Event card incomplete; previous records retained')
        target=urljoin(url,a['href'])
        if target in seen:continue
        seen.add(target)
        if len(seen)>100:raise ValueError('Event index exceeds 100 unique events; coverage incomplete')
        text=card.get_text(' ',strip=True);title=h.get_text(' ',strip=True);description=ps[-1].get_text(' ',strip=True)
        badge=card.select_one('div.absolute.left-3')
        if not badge or badge.get_text(' ',strip=True) not in ['Tech & Robotics','Hackathon','Workshop']:continue
        if not re.search(r'robot|hackathon|embodied|autonom|\bAI\b',title+' '+description,re.I):continue
        dates=ps[0].get_text(' ',strip=True)
        m=re.fullmatch(r'(\d{1,2})[–-](\d{1,2}) ([A-Za-z]+), (20\d{2})',dates)
        try:
            if m:
                month=datetime.strptime(m[3],'%b').month;start=date(int(m[4]),month,int(m[1]));end=date(int(m[4]),month,int(m[2]))
            else:start=end=datetime.strptime(dates,'%b %d, %Y').date()
        except ValueError:raise ValueError('Unrecognized event dates: '+dates)
        past=bool(re.search(r'\bPast\b',text))
        if not past and not re.search(r'\bUpcoming\b',text):raise ValueError('Event edition status not recognized')
        r=base(title,target,'roboTUM',None,'events','event');r.update(organization_id='robotum',publisher_id=a['href'].split('/')[-1],publisher='roboTUM',type='Hackathon' if 'hackathon' in text.lower() else 'Workshop' if 'Workshop' in text else 'Conference',summary=description,tags=tags(title+' '+description),event_start=start.isoformat(),event_end=end.isoformat(),status='closed' if past or end<date.today() else 'unverified',extraction_complete=False,venue=ps[1].get_text(' ',strip=True))
        place=r['venue']+' '+title
        r['city']='Garching' if re.search(r'Garching',place,re.I) else 'Munich' if re.search(r'Munich|München|Olympiapark|LabCampus|Donnersbergerbrücke|Walter-Gropius',place,re.I) else None
        if r['city']:r['metro']='Munich';r['country']='Germany'
        evidence(r,'event_start',r['event_start'],dates,'Published event card',url=url)
        evidence(r,'event_end',r['event_end'],dates,'Published event card',url=url)
        evidence(r,'summary',description,description,'Published event card',url=url)
        r['field_states']={**r.get('field_states',{}),'application_method':{'state':'incomplete'},'fees':{'state':'incomplete'}}
        r['questions']=['Historical edition; registration is closed.'] if past else ['Organizer index only: confirm current registration, eligibility, fees and full instructions on the event page.']
        r['evidence_method']='Official rendered organizer event cards; edition dates retained; deeper instructions not extracted.'
        validate(r);records.append(r)
    return records,f'{len(seen)} unique published events checked; {len(records)} technically relevant editions stored. Historical editions excluded from upcoming results. Event-detail extraction remains incomplete.'
