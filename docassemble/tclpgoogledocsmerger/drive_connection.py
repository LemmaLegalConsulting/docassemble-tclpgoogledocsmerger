from docassemble.base.util import DAGoogleAPI, DAFile, log
import googleapiclient
from googleapiclient.errors import HttpError
from typing import List, Iterable, Union, Optional

from docassemble.base.util import DAObject
from .cloudconvert_api import convert_doc

api = DAGoogleAPI()
__all__ = ['download_drive_docx',
           'download_drive_docx_wrapper',
           'get_folder_id',
           'get_latest_file_for_clause',
           'get_files_in_folder']

def download_drive_docx_wrapper(
    clause_objs:Union[DAObject, Iterable[DAObject]],
    filename_base:str,
    *,
    export_as:str='docx',
    use_cloudconvert:bool=False,
    redis_cache=None
):
  service = api.drive_service()
  if isinstance(clause_objs, DAObject):
    clause_objs = [clause_objs]

  if filename_base[-5:].lower() == ".docx":
    filename_base = filename_base[:-5]

  return download_drive_docx(service, clause_objs, filename_base, export_as=export_as,
      use_cloudconvert=use_cloudconvert, redis_cache=redis_cache)

mime_types = {
  'gdoc': 'application/vnd.google-apps.document',
  'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'rtf': 'application/rtf'
}

def download_drive_docx(
    service,
    clause_objs:Iterable[DAObject],
    filename_base:str,
    *,
    export_as:str='docx',
    use_cloudconvert:bool=False,
    redis_cache=None
):
  done_files = []
  for idx, clause_obj in enumerate(clause_objs):
    file_id = clause_obj.file_id
    last_updated = clause_obj.modified_time
    if redis_cache and last_updated:
      redis_key = redis_cache.key(file_id)
      existing_data = redis_cache.get_data(redis_key)
      if existing_data and 'contents' in existing_data and existing_data.get('last_updated') >= last_updated:
        try:
          existing_data.get('contents').retrieve()
          log(f'using cached version of doc {clause_obj.name} with key: {redis_key}')
          done_files.append(existing_data.get('contents'))
          continue
        except ex:
          log(f'failed to use cached version of doc {clause_obj.name} with key: {redis_key}: {ex}')
          redis_cache.set_data(redis_key, None)
      else:
        log(f'invalidating cache of {redis_key}')
        redis_cache.set_data(redis_key, None)
    else:
      log(f'not using redis cache for {clause_obj.name}: {str(redis_cache)}, {last_updated}')

    the_file = DAFile()
    the_file.gdrive_file_id = file_id
    the_file.set_random_instance_name()
    the_file.initialize(filename=f'{filename_base}_{idx}.{export_as}')
    the_file.set_attributes(private=False, persistent=True)
    with open(the_file.path(), 'wb') as fh:
      try:
        if export_as == 'rtf':
          log('Exporting as rtf')
          response = service.files().export_media(fileId=file_id, 
              mimeType=mime_types['rtf'])
          need_to_convert = False
        elif clause_obj.mimeType == mime_types['docx'] and export_as == 'docx':
          log('exporting as docx from docx!')
          response = service.files().get_media(fileId=file_id)
          need_to_convert = False
        else: # mimeType is gdoc
          log('exporting from gdoc to ' + export_as)
          response = service.files().export_media(fileId=file_id,
              mimeType=mime_types[export_as])
          need_to_convert = True
        downloader = googleapiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
          status, done = downloader.next_chunk()
      except HttpError as ex:
        log(f"Could not download file {file_id} from Google: {ex}")
        the_file = None
    if the_file:
      the_file.commit()
    if the_file and need_to_convert:
      if use_cloudconvert:
        converted_file = convert_doc(the_file)
        if converted_file:
          the_file = converted_file
        else:
          log(f"Error: cloud convert process failed on {clause_obj.name}! Trying with the document downloaded")
      else:
        log(f'Warning: {clause_obj.name} was download as a gdoc, but cannot convert properly to docx without cloudconvert. Might cause issues')

    done_files.append(the_file)
    if the_file and redis_cache and last_updated:
      new_data = {'last_updated': last_updated, 'contents': the_file}
      redis_cache.set_data(redis_key, new_data)
  return done_files
  
def get_folder_id(folder_name) -> Optional[str]:
  try:
    service = api.drive_service()
    resp = service.files().list(spaces="drive", 
        fields="nextPageToken, files(id, name)",
        q=f"mimeType='application/vnd.google-apps.folder' and sharedWithMe and name='{str(folder_name)}'").execute()
  except HttpError as ex:
    log(f'Could not access Google Drive to find the folder with name {folder_name}')
  folder_id = None
  for item in resp.get('files', []):
    folder_id = item['id']
  return folder_id

def get_latest_file_for_clause(all_files: List, childs_name:str) -> Optional[str]:
  child_to_check = childs_name.replace("'", '_').replace('’', '_').replace('&', '_').lower().replace(' and ', ' _ ')
  matching_files = []
  for g_file in all_files:
    file_name = g_file.get('name', '')
    file_to_check = file_name.replace("'", "_").replace('’', '_').replace('&', '_').lower().replace(' and ', ' _ ')
    if file_to_check.lower().startswith(child_to_check) and 'Clause Amendment History'.lower() not in file_to_check:
      matching_files.append(g_file)
  sorted_files = sorted(matching_files, key=lambda l: l.get('name', '').upper(), reverse=True)
  if matching_files:
    return next(iter(sorted_files), None)
  else:
    return None

def get_files_in_folder(folder_name:str=None, folder_id:str=None):
  """Given a folder, get information about all of the files in that folder."""
  if folder_name is None and folder_id is None:
    raise Exception("Need to provide a folder name or an ID, you provided neither")
  if folder_id is None:
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
      raise Exception(f"The folder {folder_name} was not found")
  service = api.drive_service()
  items = list()
  page_token = None
  try:
    while True:
      # More metadata about the files in https://developers.google.com/drive/api/v3/reference/files
      response = service.files().list(spaces="drive", 
          fields="nextPageToken, files(id, name, mimeType, modifiedTime)", 
          q=f"trashed=false and '{folder_id}' in parents",
          pageToken=page_token).execute()
      for the_file in response.get('files', []):
        items.append(the_file)
      page_token = response.get('nextPageToken', None)
      # TODO(brycew): still concerned about the possibility of an infinite loop, so cap at 10000 items for now
      if page_token is None or len(items) > 10000:
        break
    return items
  except HttpError as ex:
    log(f"Could not connect to Google Drive to see files available: {ex}")
    return []