"""Retrieve independent-source climate evidence; no invented harmonization.
GCP fossil CO2 is NOT total GHG CO2e. Retain original bytes and audit headers.
"""
import argparse,csv,datetime,hashlib,json,pathlib,urllib.request,io
SOURCES={
 'gcp_fossil_co2_per_capita_2025':'https://zenodo.org/records/17417124/files/GCB2025v15_percapita_flat.csv?download=1',
 'gcp_fossil_co2_national_2025':'https://zenodo.org/records/17417124/files/GCB2025v15_MtCO2_flat.csv?download=1',
}
def fetch(root,downloader=None):
 root=pathlib.Path(root);folder=root/'data'/'independent_raw';folder.mkdir(parents=True,exist_ok=True)
 if downloader is None:
  def downloader(url):
   req=urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0 scientific research'})
   with urllib.request.urlopen(req,timeout=90) as r:return r.read()
 results=[]
 for name,url in SOURCES.items():
  try:
   body=downloader(url)
   if len(body)<500:raise ValueError('unexpectedly short independent data')
   decoded=body.decode('utf-8-sig')
   reader=csv.DictReader(io.StringIO(decoded))
   if not reader.fieldnames:raise ValueError('missing headers')
   rows=sum(1 for row in reader)
   if rows<100:raise ValueError('insufficient rows')
   path=folder/(name+'.csv');path.write_bytes(body)
   results.append({'name':name,'status':'downloaded','source_url':url,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'rows':rows,'headers':reader.fieldnames,'units':'source_native_unharmonized','independent_source':'Global Carbon Project'})
  except Exception as e:
   results.append({'name':name,'status':'download_failed','source_url':url,'error':str(e)})
 report={'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':results,'source_harmonization_completed':False,'independent_model_validation_completed':False,'critical_unit_warning':'GCP fossil CO2 and World Bank total GHG CO2e are different targets; direct numerical comparison prohibited.'}
 dest=root/'reports';dest.mkdir(exist_ok=True)
 (dest/'independent_source_evidence.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
 if any(x['status']!='downloaded' for x in results):raise RuntimeError('Independent-source download incomplete; validation cannot pass')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');fetch(p.parse_args().root)
