"""Fail-closed TeX compilation: isolated filesystem, no network or TeX shell escape."""
import os,re,sys,json,resource,subprocess,shutil,tempfile
from pathlib import Path
from pypdf import PdfReader
from portal import uploads

def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(25,25));resource.setrlimit(resource.RLIMIT_FSIZE,(32_000_000,32_000_000));resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
    if sys.platform!='darwin':resource.setrlimit(resource.RLIMIT_AS,(1_000_000_000,1_000_000_000))

def sandbox_command(executable,args,folder,read_resources=()):
    executable=str(Path(executable).resolve());folder=str(Path(folder).resolve())
    if sys.platform=='darwin' and Path('/usr/bin/sandbox-exec').exists():
        # No general home-directory, database or network access. Executable resources only.
        allow=['/usr/local/texlive','/Library/TeX','/System/Library','/usr/lib','/usr/share','/private/etc/fonts','/Library/Fonts',str((uploads.root().parent/'texmf').resolve()),folder,*map(str,read_resources)]
        quote=lambda x:'"'+x.replace('\\','\\\\').replace('"','\\"')+'"'
        policy='(version 1)(deny default)(allow process-fork)(allow sysctl-read)(allow mach-lookup)(allow file-read-metadata)(allow process-exec (literal '+quote(executable)+'))'
        policy+='(allow file-read* '+''.join('(subpath '+quote(x)+')' for x in allow)+'(literal "/") (literal "/dev/null") (literal "/dev/urandom") (literal "/dev/random"))'
        policy+='(allow file-write* (subpath '+quote(folder)+') (literal "/dev/null"))'
        return ['/usr/bin/sandbox-exec','-p',policy,executable,*args]
    bwrap=shutil.which('bwrap')
    if not bwrap:raise RuntimeError('Isolated compiler unavailable: install Bubblewrap on Linux or use the macOS sandbox. Unsandboxed compilation is disabled.')
    cmd=[bwrap,'--die-with-parent','--unshare-all','--new-session','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--proc','/proc','--dev','/dev','--tmpfs','/tmp']
    for path in ['/lib64','/etc/texmf','/var/lib/texmf','/etc/fonts','/var/cache/fontconfig']:
        if Path(path).exists():cmd+=['--ro-bind',path,path]
    return cmd+['--bind',folder,folder,'--chdir',folder,executable,*args]

def compile_source(source,template_id,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);output.chmod(0o700)
    if len(source)>250000:raise ValueError('LaTeX source limit is 250 KB')
    with tempfile.TemporaryDirectory(prefix='atlas-tex-') as temp:
        folder=Path(temp).resolve();main='main.tex'
        if template_id:
            item=uploads.get(template_id);shutil.copytree(uploads.root()/template_id,folder,dirs_exist_ok=True);main=item['metadata']['main']
        path=folder/main;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(source);work=path.parent
        # Reserved filename keeps user-controlled names out of engine option parsing.
        (work/'atlas-document.tex').write_text(source)
        engine='xelatex' if re.search(r'\\usepackage(?:\[[^]]*\])?\{fontspec\}',source) else 'pdflatex'
        exe=shutil.which(engine) or str(Path('/Library/TeX/texbin')/engine)
        if not Path(exe).exists():raise RuntimeError('TeX engine '+engine+' is not installed')
        env={'PATH':str(Path(exe).parent)+':/usr/bin:/bin','HOME':str(folder),'TMPDIR':str(folder),'TEXMFHOME':str((uploads.root().parent/'texmf').resolve()),'TEXMFVAR':str(folder/'texmf-var'),'TEXMFCONFIG':str(folder/'texmf-config'),'openin_any':'p','openout_any':'p','shell_escape':'f','SOURCE_DATE_EPOCH':'0','TZ':'UTC','LANG':'en_US.UTF-8'}
        args=['-fmt='+engine,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-jobname=atlas-document']
        if engine=='xelatex':args+=['-no-pdf']
        logs=[]
        for _ in range(2):
            run=subprocess.run(sandbox_command(exe,args+['atlas-document.tex'],folder),cwd=work,env=env,capture_output=True,timeout=35,preexec_fn=limits)
            logs.append(run.stdout.decode(errors='replace')+run.stderr.decode(errors='replace'))
            if run.returncode:raise RuntimeError(('\n'.join(logs) or 'Isolated compiler exited with code '+str(run.returncode))[-10000:])
        if engine=='xelatex':
            converter=str(Path(exe).parent/'xdvipdfmx')
            run=subprocess.run(sandbox_command(converter,['-o','atlas-document.pdf','atlas-document.xdv'],folder),cwd=work,env=env,capture_output=True,timeout=25,preexec_fn=limits)
            logs.append(run.stderr.decode(errors='replace'))
            if run.returncode:raise RuntimeError(logs[-1][-5000:])
        pdf=work/'atlas-document.pdf'
        if not pdf.exists():raise RuntimeError('Compiler did not produce a PDF')
        reader=PdfReader(pdf);warnings=[];log='\n'.join(logs)
        if re.search(r'Overfull \\[hv]box',log):warnings.append('Overfull text detected; inspect the PDF layout')
        if re.search(r'undefined references|undefined citations|Missing character',log,re.I):warnings.append('Unresolved reference or missing character')
        placeholders=re.findall(r'\[\[(?:[^\]]+)\]\]|\{\{[^}]+\}\}|TODO|PLACEHOLDER',source)
        if placeholders:warnings.append('Unresolved placeholders: '+', '.join(sorted(set(placeholders)))[:400])
        if len(reader.pages)>2:warnings.append('More than two pages; review the requested length')
        if not any(p.extract_text() for p in reader.pages):warnings.append('PDF has no extractable text')
        shutil.copyfile(pdf,output/'document.pdf');(output/'document.pdf').chmod(0o600)
        (output/'compile.log').write_text(log);(output/'compile.log').chmod(0o600)
        previews=render_pages(pdf,folder,output,env)
        return {'previews':previews,'status':'compiled','engine':engine,'pages':len(reader.pages),'warnings':warnings,'ready':False,'requires_visual_review':True,'compiled_at':__import__('portal.db',fromlist=['now']).now()}

def render_pages(pdf,folder,output,env):
    renderer=shutil.which('pdftoppm')
    resources=[]
    if sys.platform=='darwin':
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm'
        if bundled.exists():
            renderer=str(bundled);resources=[bundled.parent.parent];env={**env,'DYLD_FALLBACK_LIBRARY_PATH':str(bundled.parent.parent/'lib')}
    if not renderer:return 0
    try:
        result=subprocess.run(sandbox_command(renderer,['-png','-r','100','-f','1','-l','10',str(pdf),str(folder/'preview')],folder,resources),env=env,cwd=folder,capture_output=True,timeout=30,preexec_fn=limits)
        if result.returncode:return 0
        images=sorted(folder.glob('preview-*.png'))
        for i,image in enumerate(images,1):
            target=output/f'page-{i}.png';shutil.copyfile(image,target);target.chmod(0o600)
        return len(images)
    except (OSError,subprocess.SubprocessError):return 0
