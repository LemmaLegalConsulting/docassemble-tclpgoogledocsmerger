import os
from pyairtable import Table 
from typing import Mapping, Optional, List
import pandas as pd
import requests
from docassemble.base.util import current_datetime, date_interval, log

def get_airtable(
    airtable_info:Mapping[str, str],
    converters:Mapping[str, callable],
    redis_cache=None,
) -> Optional[pd.DataFrame]:
  """Gets the airtable into the same dataframe that we would read it from a CSV"""
  just_rows = get_airtable_or_cache(airtable_info, redis_cache)
  if not just_rows:
    return None
  df = pd.DataFrame(just_rows)
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
  try:
    my_airtable = Table(airtable_key, airtable_base, airtable_table) 
    all_table = my_airtable.all()
  except requests.exceptions.HTTPError as ex:
    log(f'HTTPError when retrieving airtable: {ex}')
    return None
  just_rows = [row['fields'] for row in all_table]
  if redis_cache:
    new_data = {'last_updated': current_datetime(), 'contents': just_rows}
    redis_cache.set_data(redis_key, new_data)
  return just_rows
