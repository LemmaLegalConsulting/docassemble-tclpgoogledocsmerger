from docxtpl import DocxTemplate, RichText
from typing import List, Mapping
from docassemble.base.util import DAFile, DAObject, format_date, today

def merge_docs(template_doc:str, all_docs:List[DAObject], tags_with_rows:Mapping[str, List[str]]):
  tpl = DocxTemplate(template_doc)
  subdocs = []
  for doc in all_docs:
    link = RichText('Online resource at ')
    link.add(doc.full_name, url_id=tpl.build_url_id(doc.url), color="0000ee", underline=True)
    subdocs.append( (doc, format_date(doc.modified_time), link, tpl.new_subdoc(doc.file.path())) )
  
  context = {
    'mysubdoc': subdocs,
    'today_date': format_date(today()),
    'tags_with_rows': tags_with_rows
  }
  tpl.render(context)
  the_file = DAFile()
  the_file.set_random_instance_name()
  the_file.initialize(filename='final_document.docx')
  tpl.save(the_file.path())
  return the_file