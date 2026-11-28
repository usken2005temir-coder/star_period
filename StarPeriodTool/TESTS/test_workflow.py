import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np,pandas as pd
spec=importlib.util.spec_from_file_location('tool',Path(__file__).resolve().parents[1]/'MainC.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m._activate_modules()
import analyze as a
from discovery import scout
from advanced import refine
class UpgradeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  rng=np.random.default_rng(16);self.t=np.sort(rng.uniform(0,12,160));self.y=np.sin(2*np.pi*self.t/.7)+rng.normal(0,.03,len(self.t));self.p=self.root/'star.csv'
  pd.DataFrame({'time':self.t,'flux':self.y,'error':.03}).to_csv(self.p,index=False)
  self.argv=['--input',str(self.p),'--min-period','.5','--max-period','1','--output-dir',str(self.root/'out'),'--wwz-centers','6']
  self.args=a.parser().parse_args(self.argv)
 def test_windows_grid_no_gap_or_coarsening(self):
  self.args.search_windows='[[1.05,1.15],[1.4,1.5]]';f=a.frequency_grid(self.t,self.args)
  self.assertEqual(len(a.grid_segments(f)),2);self.assertFalse(np.any((f>1.15)&(f<1.4)))
  self.assertTrue(a.grid_edge(f,1.4));self.assertIsNone(a.grid_bounds(f,1.3))
  self.args.max_grid_size=2
  with self.assertRaisesRegex(ValueError,'silently'):a.frequency_grid(self.t,self.args)
 def test_window_gap_peak_endpoints(self):
  f=np.r_[np.linspace(1,1.2,20),np.linspace(2,2.2,20)];score=np.zeros(40);score[19]=.7;score[20]=.8
  peaks=a.peak_indices(score,f,10,count=2);self.assertEqual(set(peaks),{19,20})
 def test_refinement_stays_inside_window(self):
  f=np.r_[np.linspace(1.3,1.35,40),np.linspace(1.42,1.44,40)]
  result=refine(self.t,self.y,None,[1.43],f,1)
  self.assertTrue(1.42<=result['frequencies'][0]<=1.44)
  with self.assertRaisesRegex(ValueError,'outside'):refine(self.t,self.y,None,[1.4],f,1)
 def test_scout_recovers_and_includes_companions(self):
  r=scout(self.t,self.y,np.full(len(self.t),.03),.2,3,top_count=3)
  self.assertTrue(any(abs(c['period_days']/.7-1)<.005 for c in r['candidates']))
  for f in (1/.7,2/.7,.5/.7):self.assertTrue(any(lo<=f<=hi for lo,hi in r['frequency_windows']))
 def test_scout_rejects_over_budget(self):
  with self.assertRaisesRegex(ValueError,'not silently'):scout(self.t,self.y,None,.001,3,max_points=100)
 def test_units(self):
  self.assertAlmostEqual(89*m._period_factor('minutes'),89/1440)
  with self.assertRaises(ValueError):m._period_factor('years')
 def test_mc_off_switch(self):
  with patch.object(m,'_ask',return_value='n'):flags=m.choose_monte_carlo(self.argv)
  self.assertIn('--no-recommend',flags);self.assertEqual(flags[flags.index('--bootstrap')+1],'0')
 def test_mc_on_switch(self):
  with patch.object(m,'_ask',side_effect=['y','10']):flags=m.choose_monte_carlo(self.argv)
  self.assertEqual(flags[flags.index('--bootstrap')+1],'10')
 def test_mc_unknown_errors_explicit_choice(self):
  pd.DataFrame({'time':self.t,'flux':self.y}).to_csv(self.p,index=False)
  with patch.object(m,'_ask',side_effect=['y','n']):flags=m.choose_monte_carlo(self.argv)
  self.assertEqual(flags[flags.index('--bootstrap')+1],'0')
  with patch.object(m,'_ask',side_effect=['y','y','3']):flags=m.choose_monte_carlo(self.argv)
  self.assertIn('--noise-estimate',flags)
 def test_known_period_wizard(self):
  argv=['--input',str(self.p),'--output-dir',str(self.root),'--basic']
  with patch.object(m,'_ask',side_effect=['','2','minutes','89','2']),patch('webbrowser.open'):
   flags=m.choose_period_range(argv)
  self.assertAlmostEqual(float(flags[flags.index('--min-period')+1]),89/1440*.98)
  self.assertEqual(flags[flags.index('--search-origin')+1],'known')
 def test_clipped_mc_all_methods_and_reports(self):
  df=pd.read_csv(self.p);df.loc[55,'flux']+=7;df.to_csv(self.p,index=False)
  out=m.run_combined(self.argv+['--basic','--bootstrap','3'])
  info=json.loads((out/'preprocessing.json').read_text());self.assertGreater(info['flagged'],0)
  self.assertEqual(info['flagged']+info['retained'],info['valid_before'])
  self.assertEqual(len(pd.read_csv(out/'perturbation_periods.csv')),12)
  for method in a.METHODS:
   for suffix in ('_periodogram.png','_monte_carlo.png'):self.assertTrue((out/(method+suffix)).exists())
  self.assertTrue((out/'FINAL_PERIODS.csv').exists());self.assertTrue((out/'RESULT.html').exists())
 def test_discovery_conditional_no_forced_winner(self):
  from recommendation import recommend
  self.args.methods=['ls'];self.args.search_windows='[[1.35,1.5],[1.8,1.9]]';self.args.search_origin='discovery';self.args.recommend_trials=3;self.args.cv_folds=3
  self.root.joinpath('r').mkdir();f=a.frequency_grid(self.t,self.args)
  r=recommend(self.t,self.y,None,f,self.args,self.root/'r')
  self.assertEqual(r['decision']['status'],'conditional_window_comparison');self.assertIsNone(r['decision']['method'])
  draws=pd.read_csv(self.root/'r/recommendation_injections.csv')
  self.assertTrue(all(a.grid_bounds(f,1/p) is not None for p in draws.true_period_days))
 def test_no_supported_method_does_not_invent_period(self):
  with patch.object(a,'evaluate',side_effect=lambda method,t,y,dy,f,args,centers:(np.full(len(f),np.nan),None)):
   out=m.run_combined(self.argv+['--basic','--methods','wwz','--no-clip','--bootstrap','2'])
  payload=json.loads((out/'run.json').read_text())
  self.assertEqual(payload['results'][0]['status'],'insufficient_support')
  self.assertNotIn('period_days',payload['results'][0])
  self.assertTrue(pd.read_csv(out/'FINAL_PERIODS.csv').empty)
  self.assertTrue((out/'wwz_monte_carlo.png').exists())
 def test_scout_regular_sampling_singularities(self):
  t=np.arange(40.);y=np.sin(2*np.pi*t/3.7)
  result=scout(t,y,None,1,10,top_count=2)
  self.assertTrue(any(abs(c['period_days']/3.7-1)<.01 for c in result['candidates']))
 def test_complete_menu_no_mc(self):
  folder=self.root/'UPLOAD_DATA_HERE';folder.mkdir();(folder/'s.csv').write_bytes(self.p.read_bytes())
  replies=['Demo','flux','days','time','flux','error','0','2','','2','days','.7','5','n']
  with patch.object(m,'APP_ROOT',self.root),patch.object(m,'_ask',side_effect=replies),patch('webbrowser.open'):
   flags=m.interactive_arguments()
  self.assertIn('--no-recommend',flags);self.assertEqual(flags[flags.index('--bootstrap')+1],'0')
  self.assertEqual(flags[flags.index('--search-origin')+1],'known')
unittest.main()

