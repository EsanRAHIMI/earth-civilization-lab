import csv,io,zipfile,unittest
from src.faostat_crop_source import extract

class FAOWheatSourceTests(unittest.TestCase):
 def fixture(self,records):
  fields=["Area Code","Item Code","Element Code","Year","Unit","Value","Flag"]
  text=io.StringIO()
  writer=csv.DictWriter(text,fieldnames=fields);writer.writeheader();writer.writerows(records)
  target=io.BytesIO()
  with zipfile.ZipFile(target,"w") as z:z.writestr("Test_E_All_Data_(Normalized).csv",text.getvalue())
  return target.getvalue()
 def test_yield_hg_and_area_ha(self):
  record=lambda code,unit,val:{"Area Code":"100","Item Code":"15","Element Code":code,
    "Year":"2019","Unit":unit,"Value":str(val),"Flag":"A"}
  observed=extract(self.fixture([record("5412","hg/ha",30000),record("5312","ha",1000),record("5510","t",3000)]))
  self.assertEqual(observed[("100",2019,"5412")]["value"],3.)
  self.assertEqual(observed[("100",2019,"5312")]["value"],1000.)
  self.assertEqual(observed[("100",2019,"5412")]["flag"],"A")
 def test_wrong_measurement_unit_rejected(self):
  row={"Area Code":"100","Item Code":"15","Element Code":"5412","Year":"2019",
       "Unit":"kg","Value":"2000","Flag":"A"}
  with self.assertRaisesRegex(ValueError,"unit"):
   extract(self.fixture([row]))
 def test_duplicate_country_year_measure_rejected(self):
  row={"Area Code":"100","Item Code":"15","Element Code":"5412","Year":"2019",
       "Unit":"hg/ha","Value":"30000","Flag":"A"}
  with self.assertRaisesRegex(ValueError,"Duplicate"):
   extract(self.fixture([row,row]))
if __name__=="__main__":unittest.main()
