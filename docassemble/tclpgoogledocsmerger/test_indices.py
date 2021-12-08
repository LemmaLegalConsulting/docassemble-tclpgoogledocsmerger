import unittest
from pathlib import Path

from .data import MultiSelectIndex

class TestMultiSelectIndex(unittest.TestCase):
  def setUp(self):
    self.index = MultiSelectIndex(None, Path(__file__).parent.joinpath('data/sources/Grid_view.csv'),
	cols_with_indices=["GIC Industry", 'GIC Industry Group', 'COP26 Net Zero Chapter', 
	    "NZ Scopes Field", 'Timeline Main Phase', 'Timeline Sub-Phase', 
	    'Practice Area'])

  def test_loaded_correctly(self):
    self.assertEqual(self.index.get_values('NZ Scopes Field'), ['Scope 1', 'Scope 2', 'Scope 3'])

  def test_index_query(self):
    simple = self.index.query([('GIC Industry', ['Information Technology'])])
    self.assertEqual(simple, ["Alex's Clause", "Ming's Clause", "Suki's Clause"])

    two_columns = self.index.query([('GIC Industry', ['Information Technology']),
        ('COP26 Net Zero Chapter', ['"Industry (including Heavy Industry; Retail & FMCG; ICT & Media)"'])])
    self.assertEqual(two_columns, ["Alex's Clause"])

    multiple_answers = two_columns = self.index.query(
        [('GIC Industry', ['Information Technology']),
             ('COP26 Net Zero Chapter', [
                  '"Industry (including Heavy Industry; Retail & FMCG; ICT & Media)"',
                  'Law & Legal Structures'
                  ])])
    self.assertEqual(multiple_answers, ["Alex's Clause", "Ming's Clause", "Suki's Clause"])
  
