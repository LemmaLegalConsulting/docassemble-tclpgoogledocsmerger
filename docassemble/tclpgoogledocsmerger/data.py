import pandas as pd
import numpy as np
from typing import Dict, List, Optional

def create_indices(table, cols:List[str], id_col:Optional[str]=None) -> List[Dict[str, List[str]]]:
  """Given a pandas "base" (from Airtable) and a list of columns / fields to make indices of,
  returns a list (one per requested column) of dictionaries from the entries in the given column to the
  rows that contained that entry"""
  if id_col is None:
    id_col = next(iter(table.keys()))
  return [_create_index(table, col, id_col) for col in cols]


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