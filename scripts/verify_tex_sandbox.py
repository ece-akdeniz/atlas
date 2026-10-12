"""Real compilation boundary checks using disposable synthetic canaries."""
import tempfile
from pathlib import Path
from portal.compilation import compile_source
with tempfile.TemporaryDirectory(prefix='atlas-boundaries-') as temp:
 root=Path(temp);canary=root/'private-canary.txt';canary.write_text('UNIQUE_PRIVATE_CANARY')
 good=r'\documentclass{article}\begin{document}Sandbox test\end{document}'
 assert compile_source(good,None,root/'good')['pages']==1
 try:compile_source(good.replace('Sandbox test',r'\input{'+str(canary)+'}'),None,root/'read')
 except RuntimeError:pass
 else:raise AssertionError('Absolute private file access must fail')
 attack=r'\immediate\write18{touch '+str(root/'shell-escaped')+'}'+good
 compile_source(attack,None,root/'shell')
 assert not (root/'shell-escaped').exists()
 print('PASS: normal compilation, private-file denial, TeX shell-execution denial')
