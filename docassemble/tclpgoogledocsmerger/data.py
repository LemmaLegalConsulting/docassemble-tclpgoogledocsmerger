import re
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple, Mapping
from docassemble.base.util import DAObject, DAEmpty, log
from .airtable import get_airtable
from functools import reduce

__all__ = ['MultiSelectIndex']

def create_indices(table, cols:List[str], id_col:Optional[str]=None) -> Dict[str, Dict[str, List[str]]]:
  """Given a pandas "base" (from Airtable) and a list of columns / fields to make indices of,
  returns a list (one per requested column) of dictionaries from the entries in the given column to the
  rows that contained that entry"""
  if id_col is None:
    id_col = next(iter(table.keys()))
  return {col: _create_index(table, col, id_col) for col in cols}


def _create_index(table, col:str, id_col:str=None) -> Dict[str, List[str]]:
  """Returns a dict mapping entries in the given column to row ids that had said entry"""
  index:Dict[str, List[str]]= {}
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

# Matches all commas that are outside of quotes, i.e. only delimiter commas
# Wish I had written this one: https://stackoverflow.com/a/21106122/11416267
comma_outside_quotes = re.compile(r'(?!\B"[^"]*),(?![^"]*"\B)')

def split_and_strip(list_str):
  if not isinstance(list_str, str):
    return []
  return [entry.strip().strip('"') for entry in comma_outside_quotes.split(list_str) if entry.strip()]

def replace_quote(child_name):
  """Fancy apostrophes are dumb, replace with a normal one"""
  if not isinstance(child_name, str):
    return ""
  return child_name.replace(r'’', "'").strip()

ColumnQuery = Tuple[str, List[str]]

class MultiSelectIndex(DAObject):
  def init(self, *pargs, **kwargs):
    """Creates a select index, either using the latest airtable data, using cached airtable data
    in Redis, or by using the backup downloaded local CSV from airtable.
    
    """
    super().init(*pargs, **kwargs)
    airtable_info = kwargs.get('airtable_info')
    redis_cache = kwargs.get('redis_cache', DAEmpty)
    csv_path = kwargs.get('csv_path', '')
    url_file_path = kwargs.get('url_file_path', '')
    cols_with_indices = kwargs.get('cols_with_indices', [])
    # Some hardcoded cleaning on the data, particularly lists in columns
    converters = {
        "Child's name": replace_quote, 
        # Clean data in columns with list entries with commas in the strings
        "Practice Area": split_and_strip, 
        "COP26 Net Zero Chapter": split_and_strip, 
        # Split the comma separated lists into actual lists
        "GIC Industry": split_and_strip,
        "GIC Industry Group": split_and_strip,
        "Jurisdiction": split_and_strip,
        "F - Contract Emissions": split_and_strip,
        "F - Corp Gov": split_and_strip,
        "F - Reporting & Disclosures": split_and_strip,
        "F - Corporate Mechanisms": split_and_strip,
        "F - Organisation emissions": split_and_strip,
        "F - Incentives, Enforcement, Disputes": split_and_strip,
        "F - Other environmental function": split_and_strip,
        "F - Pre-contract": split_and_strip,
        "F - Just Transition": split_and_strip,
        "F - Resilience & Adaptation": split_and_strip,
        "F - Biodiversity": split_and_strip
    }
    airtable_table = get_airtable(airtable_info, converters)#, redis_cache)
    if airtable_table is not None:
      log('**getting data from airtable/redis**')
      self.table = airtable_table
    else:
      log(f'**Falling back to reading clause info from CSV at {csv_path}**')
      self.table = pd.read_csv(csv_path, converters=converters)

    self.table.sort_values(by=["Child's name"], inplace=True)

    if url_file_path:
      urls = pd.read_csv(url_file_path)
      self.table = self.table.merge(urls, on="Child's name", how="left")
      self.table["URL arg"] = np.where(self.table["URL Title"].isnull(), self.table["Full name"], self.table["URL Title"])
    else:
      # Assumes that the URL is the exact same as the full name (not usually true)
      self.table["URL arg"] = self.table["Full name"]
      self.table["Has URL"] = True

    self.indices = create_indices(self.table, cols_with_indices, id_col="Child's name")
  
  def query(self, one_of_each:List[List[ColumnQuery]]) -> List[str]:
    """For each column in the dataset, takes possible values of it. If multiple values are present for one column, rows that match either are taken.
    Then only the intersection of the rows that match all of the column queries are returned."""
    rows_per_query = []
    for col_queries in one_of_each:
      if not col_queries:
        continue
      rows_for_query = set()
      for col_name, col_vals in col_queries:
        if col_vals is None:
          for rows in self.indices[col_name].values():
            rows_for_query = rows_for_query.union(rows)
        else:
          for col_val in col_vals:
            rows_for_query = rows_for_query.union(self.indices[col_name].get(col_val, []))
      rows_per_query.append(rows_for_query)

    # Get only the row ids that match all of the column queries
    return sorted(reduce(lambda a, b: a.intersection(b), rows_per_query, next(iter(rows_per_query))))

  def query_with_explainations(self, one_of_each:List[List[ColumnQuery]]) -> Tuple[Set[Any], Mapping[str, List[str]]]:
    rows_per_query = []
    rows_per_tag = {}
    for col_queries in one_of_each:
      if not col_queries:
        continue
      rows_for_query = set()
      for col_name, col_vals in col_queries:
        if col_vals is None:
          for rows in self.indices[col_name].values():
            rows_for_query = rows_for_query.union(rows)
            rows_per_tag[f'{col_name}'] = sorted(rows_for_query)
        else:
          for col_val in col_vals:
            rows = self.indices[col_name].get(col_val, [])
            rows_for_query = rows_for_query.union(rows)
            rows_per_tag[f'{col_name}: {col_val}'] = sorted(rows)
      rows_per_query.append(rows_for_query)

    # Get only the row ids that match all of the column queries
    all_matches_rows = set(reduce(lambda a, b: a.intersection(b), rows_per_query, next(iter(rows_per_query))))
    for tag, rows in rows_per_tag.items():
      rows_per_tag[tag] = [row for row in rows if row in all_matches_rows]
    return all_matches_rows, rows_per_tag
  
  def get_full_rows(self, row_ids, id_col="Child's name"):
    return self.table[self.table[id_col].isin(row_ids)]

  def get_values(self, col_name:str) -> List[str]:
    """Given a column name, gets all of the unique values in for that column
     from every row"""
    values = set(self.table[col_name].explode())
    values.discard(np.nan)
    return sorted(values)
