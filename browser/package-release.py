"""Copied as browser/package-release.py in the public fork."""
from pathlib import Path
import hashlib,json,sys,zipfile,shutil
lab=Path(__file__).resolve().parent;root=lab.parent;build=lab/'build'/sys.argv[1];src=root/'KoboDeluxe-0.5.1'
assert '_oga_state' not in (build/'kobo.js').read_text()
notice=(lab/'README.md').read_text(encoding='utf-8')
for folder in [src,lab/'licenses']:
 for p in sorted(folder.rglob('*')):
  if p.is_file() and (p.name.lower().startswith(('readme','license','copying','credits')) or p.parent==lab/'licenses'):
   notice+='\n\n=== '+p.relative_to(root).as_posix()+' ===\n'+p.read_text(encoding='utf-8',errors='replace')
(build/'notices.txt').write_text(notice,encoding='utf-8');shutil.copy2(src/'COPYING',build/'COPYING.txt');shutil.copy2(lab/'README.md',build/'README.txt')
items=[p for folder in [src,lab] for p in folder.rglob('*') if p.is_file() and not any(n in p.relative_to(root).parts for n in ['.git','node_modules','build','evidence','emsdk','__pycache__']) and p.suffix not in ['.o','.a'] and p.name not in ['KoboPlayer','kobodl']]
items=sorted(set(items));sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=[{'path':p.relative_to(root).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in items]
with zipfile.ZipFile(build/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in items:z.write(p,p.relative_to(root).as_posix())
 z.writestr('SOURCE-MANIFEST.json',json.dumps(manifest,indent=2))
names=['index.html','kobo.js','kobo.wasm.bin','kobo.data.bin','bridge.js','input.js','persistence.js','COPYING.txt','README.txt','notices.txt','source.zip']
(build/'release-manifest.json').write_text(json.dumps({'source':'2edc48fc17e21af4ff20912b6205bb0025f8f909','containsTestExports':False,'files':[{'path':n,'bytes':(build/n).stat().st_size,'sha256':sha((build/n).read_bytes())} for n in names]},indent=2))
print(json.dumps({'sourceFiles':len(items),'runtimeFiles':len(names)}))
