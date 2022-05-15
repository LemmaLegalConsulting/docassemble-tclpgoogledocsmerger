import cloudconvert
from docxtpl import DocxTemplate, RichText
import os

def merge(all_docs, out_name):
  tpl = DocxTemplate('docassemble/tclpgoogledocsmerger/data/templates/ClausesTemplate_fixed.docx')
  subdocs = []
  for doc in all_docs:
    link = RichText('Online resources at no where')
    subdocs.append((doc, 'mydate', link, tpl.new_subdoc(doc)))

  context = {
    'mysubdoc': subdocs,
    'today_date': 'mydate_global',
    'tags_with_rows': [],
  }

  tpl.render(context)
  tpl.save(out_name) 
  return

def use_cloudconvert(in_name):
  cloudconvert.default() 

  job = cloudconvert.Job.create(payload={"tasks": {
    'import-my-file': {
      'operation': 'import/upload',
    },
    'convert-my-file': {
      'operation': 'convert',
      'input': 'import-my-file',
      'input_format': 'docx',
      'output_format': 'rtf',
      'engine': 'office',
    },
    'convert-my-file-back': {
      'operation': 'convert',
      'input': 'convert-my-file',
      'input_format': 'rtf',
      'output_format': 'docx',
     # 'engine': 'office',
    },
    'export-my-file': {
      'operation': 'export/url',
      'input': 'convert-my-file-back'
    }
    },
    "tag": "jobbuilder",
  })

  upload_task_id = job['tasks'][0]['id']
  upload_task = cloudconvert.Task.find(id=upload_task_id)
  res = cloudconvert.Task.upload(file_name=in_name, task=upload_task)
  print(f'Task.upload res: {res}')
  res = cloudconvert.Task.find(id=upload_task_id)
  print(f'Task.find res: {res}')
  job = cloudconvert.Job.wait(id=job['id'])
  
  if 'tasks' not in job:
    print(f'failed!: {job}')
    return
    
  
  for task in job["tasks"]:
    if task.get("name") == "export-my-file" and task.get("status") == "finished":
      export_task = task
      break

  file_info = export_task.get("result").get("files")[0]
  cloudconvert.download(filename='post-' + file_info['filename'], url=file_info['url'])


if __name__ == '__main__':
  merge(['aatmay.docx', 'robyn.docx', 'elsie.docx', 'aiden.docx'], 'pre-convert.docx')
  use_cloudconvert('aatmay.docx')
  use_cloudconvert('robyn.docx')
  use_cloudconvert('elsie.docx')
  use_cloudconvert('aiden.docx')
  merge(['post-aatmay.docx', 'post-robyn.docx', 'post-elsie.docx', 'post-aiden.docx'], 'post-convert.docx')


