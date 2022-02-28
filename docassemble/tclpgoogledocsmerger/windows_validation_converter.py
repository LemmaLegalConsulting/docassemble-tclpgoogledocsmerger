"""A script that does the manual conversion process of our docs automatically. Takes ~15 minutes.
TODO(brycew): Robin's doesn't quite work, it's too big as an RTF for some reason.

To Install:
1. Install python on Windows: https://www.python.org/downloads/windows/
   (remember to put python on the PATH so you can call `python` from shell or powershell)
2. Install pywin: https://pypi.org/project/pywin32/
3. Install the google python libraries: `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
4. Create Google Credentials and download to this directory with the filename "credentials.json"
5. Run the script with `python -m windows_validation_converter C:\\Users\\Full\\Path\\To\\Documents\\Dir

Sources: 
* https://stackoverflow.com/a/65724761
* https://developers.google.com/drive/api/v3/manage-uploads#python
* https://developers.google.com/drive/api/v3/quickstart/python
"""

import glob
import sys
import os.path
import tempfile

import win32com.client

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def ConvertRtfToDocx(from_files):
    """convert rtf to docx and embed all pictures in the final document. Windows only"""
    word = win32com.client.Dispatch("Word.Application")
    wdFormatDocumentDefault = 16
    wdHeaderFooterPrimary = 1
    for from_file in from_files:
        print(from_file)
        doc = word.Documents.Open(from_file)
        for pic in doc.InlineShapes:
            pic.LinkFormat.SavePictureWithDocument = True
        for hPic in doc.sections(1).headers(wdHeaderFooterPrimary).Range.InlineShapes:
            hPic.LinkFormat.SavePictureWithDocument = True
        new_name = from_file[:-3] + 'docx'
        doc.SaveAs(new_name, FileFormat=wdFormatDocumentDefault)
        doc.Close()
    word.Quit()


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_creds():
    """Creates a credential token for the user on this machine.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def download_docs(creds, download_from_folder, out_target_dir):
    """Downloads all documents from the given drive folder to out_target_dir"""
    service = build('drive', 'v3', credentials=creds)
    all_files = []
    page_token = None
    try:
        while True:
            # Call the Drive v3 API
            results = service.files().list(spaces='drive', fields='nextPageToken, files(id, name, modifiedTime)',
                q=f"trashed=false and '{download_from_folder}' in parents",
                pageToken=page_token).execute()
            for the_file in results.get('files', []):
                all_files.append(the_file)
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break
    except HttpError as error:
        print(f'An error occurred when listing all files to download: {error}: {page_token}')
        
    # Now Download all of the files
    status = None
    for idx, file in enumerate(all_files):
        try:
            drive_name = file.get('name', f'drive_doc_{idx}') + '.rtf'
            if 'Amendment_History' in drive_name.replace(' ', '_'):
                # Skip: no need to convert
                continue
            new_file_name = out_target_dir + '\\' + file.get('name', f'drive_doc_{idx}') + '.rtf'
            with open(new_file_name, 'wb') as fh:
                response = service.files().export_media(fileId=file.get('id'),
                    mimeType='application/rtf')
                downloader = googleapiclient.http.MediaIoBaseDownload(fh, response)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
        except HttpError as error:
            print(f'An error occurred when getting file {file.get("name", "")} to download: {error}: {status}')
            os.remove(new_file_name)

def upload_docs(creds, drive_folder_id, files_to_upload):
    """Uploads all documents from the given files_to_upload list to the given drive_folder_id"""
    service = build('drive', 'v3', credentials=creds)
    for file_to_upload in files_to_upload:
        try:
            file_name = file_to_upload.split('\\')[-1]
            file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
            media = MediaFileUpload(file_to_upload, 
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        except HttpError as error:
            print(f'An error occured when uploading file {file.get("id", "")}: {error}')


if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else tempfile.TemporaryDirectory()
    creds = get_creds()
    download_docs(creds, os.env["SOURCE_DRIVE_FOLDER"], target_dir)
    print('Starting conversion for docs')
    ConvertRtfToDocx(list(glob.glob(target_dir + r'/*.rtf')))
    print('starting upload')
    upload_docs(creds, os.env["TARGET_DRIVE_FOLDER"], list(glob.glob(target_dir + r'/*.docx')))
