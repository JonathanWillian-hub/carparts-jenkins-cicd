# Dados sintéticos somente para testes; nunca usados como evidência E6.
import importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('metrics', Path(__file__).parents[2]/'metrics/summarize.py')
metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
class MetricsTests(unittest.TestCase):
 def row(self, n):
  return dict(schema=1,buildUrl=f'https://jenkins.example/job/main/{n}/',commit='a'*40,
   recordedAt='2026-09-02T00:00:00Z',commitEpoch=1788220800,
   productionAttempted=True,productionSucceeded=True,productionFailed=False,
   deployedAt='2026-09-01T12:00:00Z',approvedAt='2026-09-01T11:00:00Z',
   approver='release-manager',image='demo.azurecr.io/carparts@sha256:'+'b'*64)
 def calc(self, rows):
  with tempfile.TemporaryDirectory() as directory:
   paths=[]
   for n,row in enumerate(rows):
    p=Path(directory)/f'{n}.json';p.write_text(json.dumps(row));paths.append(p)
   return metrics.summarize(paths,metrics.instant('2026-09-01T00:00:00Z'),metrics.instant('2026-09-03T00:00:00Z'))
 def test_minimum(self):
  with self.assertRaises(ValueError):self.calc([self.row(1)])
 def test_duplicate(self):
  with self.assertRaises(ValueError):self.calc([self.row(1)]*10)
 def test_rates(self):
  rows=[self.row(n) for n in range(10)]
  rows[0].update(productionSucceeded=False,productionFailed=True)
  result=self.calc(rows)
  self.assertEqual(result['changeFailureRatePercent'],10)
  self.assertEqual(result['deploymentsPerDay'],4.5)
  self.assertEqual(result['leadMeanHours'],12)
 def test_approval(self):
  rows=[self.row(n) for n in range(10)];rows[0]['approver']=None
  with self.assertRaises(ValueError):self.calc(rows)
if __name__=='__main__':unittest.main()
