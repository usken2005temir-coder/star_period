import importlib.util,tempfile,zipfile,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('tool',Path(__file__).resolve().parents[1]/'MainC.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);current=root/'run_20261127T120000_000000Z';current.mkdir()
 for name in ('run.json','RESULT.html'):(current/name).write_text('{}')
 old=root/'run_20200101T000000_000000Z';old.mkdir();(old/'run.json').write_text('{}');(old/'START_RESULT.md').write_text('old')
 search=root/'search_20200101T000000_000001Z';search.mkdir();(search/'range_advice.json').write_text('{}');(search/'RANGE_ADVICE.html').write_text('old')
 unknown=root/'my_data';unknown.mkdir();(unknown/'keep.csv').write_text('data')
 unfinished=root/'run_20200101T000000_000002Z';unfinished.mkdir();(unfinished/'used_data.csv').write_text('data')
 newer=root/'run_20990101T000000_000000Z';newer.mkdir();(newer/'run.json').write_text('{}');(newer/'START_RESULT.md').write_text('newer')
 protected=root/'run_20200101T000000_000003Z';protected.mkdir();(protected/'run.json').write_text('{}');(protected/'START_RESULT.md').write_text('input');(protected/'data.csv').write_text('data')
 try:m._prune_previous_results(current)
 except ValueError:pass
 else:raise AssertionError('Incomplete result permitted deletion')
 assert old.exists() and search.exists()
 with zipfile.ZipFile(current/'SAVE_RESULTS.zip','w') as z:z.writestr(current.name+'/run.json','{}')
 report=m._prune_previous_results(current,[protected/'data.csv'])
 assert not old.exists() and not search.exists()
 assert all(p.exists() for p in (current,unknown,unfinished,newer,protected))
 assert len(report['removed'])==2
print('PASS: incomplete runs preserve history; verified success deletes only older recognized outputs; inputs, newer and unknown folders retained.')
