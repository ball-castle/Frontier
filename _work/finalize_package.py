from pathlib import Path
import zipfile,json,hashlib
base=Path(r'C:\Users\CAI BIN\Desktop\1')
folder=base/'美赛建模面试备考包_20261105'
target=base/'美赛建模面试备考包_20261105.zip'
assert folder.resolve().is_relative_to(base.resolve())
files=sorted(p for p in folder.rglob('*') if p.is_file())
assert all(p.resolve().is_relative_to(folder.resolve()) for p in files)
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in files:z.write(p,str(Path(folder.name)/p.relative_to(folder)))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
report={'archive':str(target),'files':len(files),'archive_MB':round(target.stat().st_size/1048576,2),'archive_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_files_preserved':True,'visual_review':'20 authored pages inspected; changed pages re-rendered and inspected','local_links':'all checked and valid','excerpt':'27 pages text-equivalent to original final PDF'}
(base/'_work/final_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
