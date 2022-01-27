from docassemble.base.util import DAGoogleAPI, DAFile, log
from docassemble.base.functions import currency
import googleapiclient
from googleapiclient.errors import HttpError
from typing import List, Iterable, Union
from docassemble.base.pandoc import word_to_markdown

api = DAGoogleAPI()
__all__ = ['word_to_markdown', 
           'download_drive_docx_groups',
           'download_drive_docx_single',
           'get_folder_id',
           'get_files_for_clause',
           'get_files_in_folder']

def download_drive_docx_groups(file_ids_per_clause:Iterable[Iterable[str]], filename_base:str, export_to_docx:bool=False):
  if filename_base[-5:].lower() == ".docx":
    filename_base = filename_base[:-5]
    
  service = api.drive_service()
  done_groups = []
  for clause_ids in file_ids_per_clause:
    done_groups.append(download_drive_docx(service, clause_ids, filename_base, export_to_docx))
  return done_groups

def download_drive_docx_single(file_ids:Union[str, Iterable[str]], filename_base:str, export_to_docx:bool=False):
  """Downloads a list of files from google Drive, either as GDocs converted to DOCX, or directly as DOCX"""
  if isinstance(file_ids, str):
    file_ids = [file_ids]

  if filename_base[-5:].lower() == ".docx":
    filename_base = filename_base[:-5]

  service = api.drive_service()
  return download_drive_docx(service, file_ids, filename_base, export_to_docx)

def download_drive_docx(service, file_ids:Union[str, Iterable[str]], filename_base:str, export_to_docx:bool=False):
  done_files = []
  for idx, file_id in enumerate(file_ids):
    the_file = DAFile()
    the_file.gdrive_file_id = file_id
    the_file.set_random_instance_name()
    the_file.initialize(filename=f'{filename_base}_{idx}.docx')
    with open(the_file.path(), 'wb') as fh:
      try:
        if export_to_docx:
          response = service.files().export_media(fileId=file_id, 
              mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        else:
          response = service.files().get_media(fileId=file_id)
        downloader = googleapiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
          status, done = downloader.next_chunk()
      except HttpError as ex:
        log(f"Could not download file {file_id} from Google: {ex}")
    the_file.commit()
    done_files.append(the_file)
  return done_files
  
def get_folder_id(folder_name) -> str:
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

def get_files_for_clause(all_files, childs_name:str) -> List[str]:
  child_to_check = childs_name.replace("'", '_').replace('’', '_').lower()
  to_return = []
  for g_file in all_files:
    file_name = g_file.get('name', '')
    file_to_check = file_name.replace("'", "_").replace('’', '_').lower()
    if file_to_check.lower().startswith(child_to_check) and 'Clause Amendment History' not in file_to_check:
      to_return.append(g_file)
  return to_return

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
          fields="nextPageToken, files(id, name, modifiedTime)", 
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