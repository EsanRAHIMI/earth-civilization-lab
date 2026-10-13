import csv,hashlib,json,pathlib
root=pathlib.Path('.')
manifest=json.loads((root/'data/manifest.json').read_text())
panel=root/'data/observations.csv'
if hashlib.sha256(panel.read_bytes()).hexdigest()!=manifest['panel_sha256']:
 raise ValueError('Panel hash mismatch')
for entry in manifest['sources']:
 raw=(root/'data/raw'/(entry['indicator']+'.json')).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=entry['sha256']:
  raise ValueError('Raw hash mismatch')
rows=list(csv.DictReader(panel.open()))
if len(rows)!=manifest['rows'] or not rows: raise ValueError('Row count mismatch')
keys=[(r['iso3'],r['year'],r['indicator']) for r in rows]
if len(keys)!=len(set(keys)): raise ValueError('Duplicate observations')
coverage={r['indicator'] for r in rows}
if len(coverage)!=4: raise ValueError('Incomplete indicator coverage')
(root/'reports').mkdir(exist_ok=True)
(root/'reports/quality.json').write_text(json.dumps({'status':'passed','rows':len(rows),'countries':len({r['iso3'] for r in rows}),'indicators':sorted(coverage),'scientific_ready':False},indent=2))
print('QUALITY VALIDATION PASSED',len(rows))
