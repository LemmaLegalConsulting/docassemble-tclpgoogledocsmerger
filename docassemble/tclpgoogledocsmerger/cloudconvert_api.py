import cloudconvert
from docassemble.base.util import DAFile, log
from typing import Optional
import uuid

__all__ = ["convert_doc", "init_api"]

def convert_doc(the_file:DAFile) -> Optional[DAFile]:
  """Calls the cloudconvert API to convert a recently GDoc document into rtf, and back to docx,
  to fix merge issues."""

  if cloudconvert.get_existing_client() is None:
    log('Not converting files, no client api created. Call init_api')
    return None

  job_id = str(uuid.uuid4())
  log(f"Cloudconverting {the_file.path()} with job name of {job_id}")
  import_id = f"import-{job_id}"
  convert_id = f"convert-{job_id}"
  convert_back_id = f"convert-back-{job_id}"
  export_id = f"export_{job_id}"
  job = cloudconvert.Job.create(payload={
    "tasks": {
      import_id: {
        "operation": "import/upload",
      },
      convert_id: {
        "operation": "convert",
        "input": import_id,
        "input_format": "docx",
        "output_format": "rtf",
        "engine": "office",
      },
      convert_back_id: {
        "operation": "convert",
        "input": convert_id,
        "input_format": "rtf",
        "output_format": "docx",
      },
      export_id: {
        "operation": "export/url",
        "input": convert_back_id,
      }
    },
    "tag": "docassemble",
  })

  if not 'tasks' in job:
    log(f'Expected "tasks" in the job!: {job}')
    return None
  if not 'id' in job:
    log(f'Expected "id" in the job!: {job}')
    return None

  upload_task_id = job.get('tasks', [{}])[0].get('id')
  if upload_task_id is None:
    log(f'upload_task_id is None!: {job}')
    return None

  upload_task = cloudconvert.Task.find(id=upload_task_id)
  res = cloudconvert.Task.upload(file_name=the_file.path(), task=upload_task)
  res = cloudconvert.Task.find(id=upload_task_id)
  job = cloudconvert.Job.wait(id=job['id'])

  if "tasks" not in job:
    log(f'Cloudconvert job failed: {job}')
    return None

  export_task = None
  for task in job["tasks"]:
    if task.get("name") == export_id and task.get("status") == "finished":
      export_task = task
      break

  if not export_task:
    log(f'Could not find export task? {job}')
    return None 

  file_info = export_task.get("result", {}).get("files", [])[0]

  converted_file = DAFile()
  converted_file = set_random_instance_name()
  converted_file.initialize(filename=f"converted_{the_file.filename}")
  converted_file.set_attributes(private=False, persistent=True)
  cloudconvert.download(filename=converted_file.path(), url=file_info["url"])
  converted_file.commit()

  # delete the old file as much as we can
  the_file.set_attributes(persistent=False)
  converted_file.gdrive_file_id = the_file.gdrive_file_id

  return converted_file

def init_api(*, api_key:str, sandbox:bool) -> bool:
  if api_key is None or sandbox is None:
    log('Not initializing the cloudconvert api: need to pass in api_key')
    return False
  cloudconvert.configure(api_key=api_key, sandbox=sandbox)
  log('Initialized cloudconvert api!')
  return True