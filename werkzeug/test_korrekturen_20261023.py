"""Regression: geprüfte Sonderdetails und identische Besitzer-/DG-Auflösung."""
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
class Sonderdetails(unittest.TestCase):
 def test_gepruefte_zeichnungen(self):
  owners=json.loads((R/'rennfarben.json').read_text())['besitzer']
  dg=json.loads((R/'rennfarben-dg.json').read_text())['dg']
  for i,name,colors,count in [('1593424','Stall Nannippus',{'#2A86E8','#E3202A'},7),('38618313','Bn Bygg Malmö Ab / Schweden',{'#2A86E8','#FFFFFF'},0),('1594742','Gestüt Ebbesloh',{'#111111','#FFFFFF','#178A38'},3)]:
   with self.subTest(i=i):
    self.assertEqual(owners[name]['svg_override'],dg[i]['svg_override'])
    self.assertIn(i,owners[name]['dg_ids'])
    root=ET.fromstring((R/dg[i]['svg_override']).read_text())
    fills={x.get('fill') for x in root.iter()}
    self.assertTrue(colors<=fills)
    polys=[x for x in root.iter() if x.tag.endswith('polygon')]
    self.assertGreaterEqual(len(polys),count)
    self.assertNotIn('weggelassen',dg[i])
if __name__=='__main__':unittest.main()
