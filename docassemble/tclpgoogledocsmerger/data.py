import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from docassemble.base.core import DAObject
from functools import reduce

def create_indices(table, cols:List[str], id_col:Optional[str]=None) -> Dict[str, Dict[str, List[str]]]:
  """Given a pandas "base" (from Airtable) and a list of columns / fields to make indices of,
  returns a list (one per requested column) of dictionaries from the entries in the given column to the
  rows that contained that entry"""
  if id_col is None:
    id_col = next(iter(table.keys()))
  return {col: _create_index(table, col, id_col) for col in cols}


def _create_index(table, col:str, id_col:str=None) -> Dict[str, List[str]]:
  """Returns a dict mapping entries in the given column to row ids that had said entry"""
  index = {}
  for row_id, col_vals in zip(table[id_col], table[col]):
    if isinstance(col_vals, str):
      col_vals = col_vals.strip()
      if col_vals not in index:
        index[col_vals] = []
      index[col_vals].append(row_id)
      continue
    if isinstance(col_vals, float) and np.isnan(col_vals):
      continue
      
    for col_val in col_vals:
      if isinstance(col_val, float) and np.isnan(col_val):
        continue
      col_val = col_val.strip()
      if col_val not in index:
        index[col_val] = []
      index[col_val].append(row_id)
  return index

class MultiSelectIndex(DAObject):
  def init(self, *pargs, **kwargs):
    super().init(*pargs, **kwargs)
    import_path = kwargs.get('import_path', '')
    clean_data = kwargs.get('clean_data', True)
    cols_with_indices = kwargs.get('cols_with_indices', [])
    self.table = pd.read_csv(import_path)
    if clean_data:
      # Some hardcoded cleaning on the data, particularly lists in columns
      pattern = r'.*\"(.*)\".*'
      repl = lambda m: m.group(0).replace(m.group(1), m.group(1).replace(',', ';'))
  
      # Fancy apostrophes are dumb, replace with a normal one
      self.table["Child's name"] = self.table["Child's name"].str.replace('’', "'")
  
      # Clean data in columns with list entries with commas in the strings
      cols_with_comma_entries = ["Practice Area", "COP26 Net Zero Chapter", "Timeline Sub-Phase"]
      for col in cols_with_comma_entries:
        self.table[col] = self.table[col].str.replace(pattern, repl, regex=True)
    
      # Actually split the comma separated lists in certain cells into actual lists
      cols_with_list_vals = cols_with_comma_entries + ["GIC Industry", "GIC Industry Group", "Timeline Main Phase", "NZ Scopes Field"]
      for col in cols_with_list_vals:
        self.table[col] = self.table[col].str.split(',')

    self.indices = create_indices(self.table, cols_with_indices, "Child's name")
  
  def query(self, col_values:List[Tuple[str, List[str]]]) -> List[str]:
    """For each column in the dataset, takes possible values of it. If multiple values are present for one column, rows that match either are taken.
    Then only the intersection of the rows that match all of the column queries are returned."""
    rows_per_col = {}
    for col_name, col_vals in col_values:
      rows_for_col = set()
      for col_val in col_vals:
        rows_for_col = rows_for_col.union(self.indices[col_name].get(col_val, []))
      rows_per_col[col_name] = rows_for_col

    # Get only the row ids that match all of the column queries
    return sorted(reduce(lambda a, b: a.intersection(b), rows_per_col.values(), next(iter(rows_per_col.values()))))

  def get_full_rows(self, row_ids, id_col="Child's name"):
    return self.table[self.table[id_col].isin(row_ids)]

  def get_values(self, col_name:str) -> List[str]:
    """Given a column name, gets all of the unique values in for that column
     from every row"""
    values = set(self.table[col_name].explode())
    values.discard(np.nan)
    return sorted(values)