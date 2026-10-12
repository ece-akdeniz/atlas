"""Import a local JSON profile into the private database; never commit that JSON."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from portal import db
from portal.seed import bootstrap
bootstrap()
p=db.get_meta('profile'); p.update(json.loads(Path(sys.argv[1]).read_text())); db.set_meta('profile',p)
print('Private profile imported. No CV sent to an external provider.')
