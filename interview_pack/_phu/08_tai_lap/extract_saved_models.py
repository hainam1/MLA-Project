"""Development-only saved-model arithmetic. Never fits; never reads Test/text."""
import csv, hashlib, json, pathlib, sys
import joblib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACK = pathlib.Path(__file__).resolve().parents[1]
IDS = ['0514D25768A0', '684166ED2438']
EXPECTED = {
 'random_forest_vocabulary': '899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be',
 'random_forest_grammar': 'bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91',
 'ridge_vocabulary': '14591a1822ffa4fc7c9006a5abd270928401721739bea3f9fe5a76852780ef64',
 'ridge_grammar': '812885caab21dac6508835c83dc91de75b23d622577ba15a8e37e207e59b085f'}
schema = json.loads((ROOT/'outputs/phase6/feature_schema.json').read_text())
with (ROOT/'reports/week9/t3_eligible_development.csv').open(encoding='utf-8-sig',newline='') as f:
 rows = {r['essay_id']: r for r in csv.DictReader(f) if r['essay_id'] in IDS}
assert set(rows)==set(IDS)
assert all(r['source_partition']=='official_train' for r in rows.values())
X = np.array([[float(rows[i][s]) for s in schema] for i in IDS])
out = {'scope': 'Frozen Phase 6 predictions, NOT held-out GroupKFold predictions; 684166ED2438 is original model_train and is in-sample here.', 'models': {}, 'rows': {i:{} for i in IDS}}
for name, expected in EXPECTED.items():
 p=ROOT/'outputs/phase6'/f'{name}.joblib'
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 assert digest==expected, name
 m=joblib.load(p); pred=m.predict(X); xt=m[:-1].transform(X)
 out['models'][name]={'sha256':digest,'source':str(p.relative_to(ROOT)).replace('\\','/')}
 for j,i in enumerate(IDS):
  d={'prediction':float(pred[j]), 'source':out['models'][name]['source'], 'sha256':digest}
  if name.startswith('ridge'):
   model=m.named_steps['model']; terms=model.coef_*xt[j]
   d.update(intercept=float(model.intercept_), reconstructed=float(model.intercept_+terms.sum()), terms=[{'feature':s,'standardized_value':float(v),'coefficient':float(c),'product':float(t)} for s,v,c,t in zip(schema,xt[j],model.coef_,terms)])
  else:
   vals=[float(t.predict(xt[j:j+1])[0]) for t in m.named_steps['model'].estimators_]
   assert len(vals)==300
   d.update(tree_predictions=vals, reconstructed=float(np.mean(vals)), population_std=float(np.std(vals)))
  assert abs(d['reconstructed']-d['prediction'])<1e-11
  out['rows'][i][name]=d
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
(PACK/'02_mau_truy_vet').mkdir(exist_ok=True)
(PACK/'02_mau_truy_vet/saved_model_arithmetic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: four model hashes; development only; two rows; Ridge sums and 300-tree means verified; no fit.')
