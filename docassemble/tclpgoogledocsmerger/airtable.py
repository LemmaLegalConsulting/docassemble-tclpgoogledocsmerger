from pyairtable import Table 
from typing import Callable, Mapping, Optional, List
import pandas as pd
import requests
from docassemble.base.util import current_datetime, date_interval, log

def get_airtable(
    airtable_info:Mapping[str, str],
    converters:Mapping[str, Callable],
    redis_cache=None,
) -> Optional[pd.DataFrame]:
  """Gets the airtable into the same dataframe that we would read it from a CSV"""
  just_rows = get_airtable_or_cache(airtable_info, redis_cache)
  if not just_rows:
    return None
  df = pd.DataFrame(just_rows)
  df.dropna(subset=["Child's name", "Full name"])
  df.reset_index(drop=True)
  for col_name in converters.keys():
    df[col_name] = df[col_name].apply(converters[col_name])
  return df

def get_airtable_or_cache(airtable_info:Mapping[str, str], redis_cache=None) -> Optional[List]:
  """Gets information about the airtable, either directly from it or from the cache, as
  long as the cache is less than an hour old."""
  if not airtable_info:
    log('You need to define all of the airtable information: see https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger#airtable-config')
    return None
  if 'api key' not in airtable_info or not airtable_info['api key']:
    log('You need to define an api key for airtable! see https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger#airtable-config')
    return None
  if 'base id' not in airtable_info or not airtable_info['base id']:
    log('You need to define a base id for airtable! see https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger#airtable-config')
    return None
  if 'table name' not in airtable_info or not airtable_info['table name']:
    log('You need to define a table name for airtable! see https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger#airtable-config')
    return None

  airtable_key = airtable_info['api key']
  airtable_base = airtable_info['base id']
  airtable_table = airtable_info['table name']

  if redis_cache:
    redis_key = redis_cache.key('clause_airtable')
    existing_data = redis_cache.get_data(redis_key)
    if existing_data and 'contents' in existing_data \
        and existing_data.get('last_updated') + date_interval(hours=1) > current_datetime():
      return existing_data['contents']
    else:
      log('Invalidating clause_airtable cache')
      redis_cache.set_data(redis_key, None)

  reference_cols = [
    ('Practice Area', 'Practice Area'),
    ('GIC Industry', 'GIC Industry'),
    ('COP26 Net Zero Chapter', 'COP26 Net Zero Chapter'),
    ('GIC Industry Group', 'GIC Industry Group'),
    ('Timeline Main Phase', 'Timeline Main Phase'),
    ('Timeline Sub-Phase', 'Timeline Sub-Phase'),
    ('F - Corp Gov', 'F - Corp Gov'),
    ('F - Reporting & Disclosures', 'F - Reporting & Disclosures'),
    ('F - Corporate Mechanisms', 'F - Corporate Mechanims'),
    ('F - Organisation emissions', 'F - Org Emissions'),
    ('F - Incentives, Enforcement, Disputes', 'F - Incentives & Disincentives, Enforcement, Disputes'),
    ('F - Other environmental function', 'F - Other environmental function'), 
    ('F - Pre-contract', 'F - Pre-contract'),
    ('F - Just Transition', 'F - Just Transition'), 
    ('F - Resilience & Adaptation', 'F - Resilience & Adaptation'),
    ('F - Biodiversity', 'F - Biodiversity'), 
  ]
  
  try:
    my_airtable = Table(airtable_key, airtable_base, airtable_table) 
    all_table = my_airtable.all()
    just_rows = [row['fields'] for row in all_table]
    for col, table_name in reference_cols:
      t = Table(airtable_key, airtable_base, table_name)
      name_map = {r["id"]: r["fields"].get("Name") for r in t.all()}
      for row in just_rows:
        row[col] = ','.join([name_map.get(val, '') for val in row.get(col, [])])
  except requests.exceptions.HTTPError as ex:
    log(f'HTTPError when retrieving airtable: {ex}')
    return None

  if redis_cache:
    new_data = {'last_updated': current_datetime(), 'contents': just_rows}
    redis_cache.set_data(redis_key, new_data)
  return just_rows
