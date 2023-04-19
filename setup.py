import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.tclpgoogledocsmerger',
      version='1.1.0',
      description=('A docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata'),
      long_description='# docassemble.tclpgoogledocsmerger\r\n\r\nA docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata.\r\n\r\nMade in association with The [Chancery Lane Project](https://chancerylaneproject.org/)\r\n\r\nSpecial dependencies:\r\n\r\n* a branch of [docxcompose](https://github.com/BryceStevenWilley/docxcompose/tree/master), version `1.3.5-devlemma`.\r\n  * this branch merges a [standing PR](https://github.com/4teamwork/docxcompose/pull/58) that works when certain styles aren\'t present\r\n  * also fixes some issues with [abstractNumId uniqueness](https://github.com/BryceStevenWilley/docxcompose/commit/a90e445857dbf61ce5c999bb50b13291b51d7b12)\r\n* a branch of [docxtpl](https://github.com/LemmaLegalConsulting/docxtpl/tree/subdoc_bookmark_issues)\r\n  * this branch fixed an issue where bookmark ids were only renumbered per subdocument, not over the whole document\r\n* the bleeding edge of [cloudconvert-python](https://github.com/cloudconvert/cloudconvert-python), specifically anything after [commit 5aedec17578107c0f28edaa7b4ab0b3d0a65c6f7](https://github.com/cloudconvert/cloudconvert-python/commit/5aedec17578107c0f28edaa7b4ab0b3d0a65c6f7)\r\n  * The 2.1.0 release on pypi does _not_ have the correct patches to work\r\n  * docassemble will complain when installing this directly from the github link. You will need to download the git repository, and upload it as a\r\n    zip file to docassemble in order to install it\r\n\r\n## Airtable Config\r\n\r\nThis interview uses the data in [an Airtable](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY), to\r\ndetermine which clause applies to a particular query.\r\n\r\nIn your docassemble configuration, you should add the following YAML dictionary, replacing the example values on the right with your Airtable information:\r\n\r\n```yaml\r\ndocs airtable:\r\n  api key: keyabcDEF12345678\r\n  base id: appabcDEF12345678\r\n  table name: "Grid View"\r\n```\r\n\r\nIf there are issues connecting to the Airtable, those issues will be\r\nprinted in the [docassemble logs](https://docassemble.org/docs/admin.html#logs).\r\n\r\n## Google Drive Config\r\n\r\nIn your docassemble configuration, you should add the following YAML key-value pair:\r\n\r\n```yaml\r\ndrive doc bank: "google-drive-folder-id-abc123"\r\n```\r\n\r\nThe Google drive folder id should be visible in the URL of the drive folder, after `/u/0/folders/`.\r\n\r\n## The Cache\r\n\r\nAn on server cache of the airtable data and the google drive data is kept. You can directly tinker with this cache\r\nby using the `cache_settings.yml` interview. You must be logged in as a server admin to use that interview.\r\n\r\n## Cloud Convert Config\r\n\r\n```yaml\r\ncloud convert api key: "myapikeyabc123aoserhc"\r\n```\r\n\r\nFor instructions on making a cloud convert API Key, you can visit [this page while logged in](https://cloudconvert.com/dashboard/api/v2/keys).\r\n\r\n## Adding new Clauses\r\n\r\nOnce a clause is present in the Airtable data (see above), you can add its corresponding DOCX to the Google Drive folder, and it will be found and downloaded by this interview. It\'s important that the name of the DOCX in the Drive folder have the exact name of the clause somewhere in it, with the same spelling as in the Airtable. Otherwise, it won\'t be found and downloaded by this interview (ignoring `&` and `\'`). For example, if the DOCX\'s name is "Gilbert _ Sullivan_s Clause - V3", and the Airtable "Child name" is "Gilbert & Sullivan\'s Clause", that\'s okay. But if the DOCX\'s name is "Chris_s Clause - V4" and the Airtable name is "Chris\' Clause", it won\'t be found.\r\n\r\nFor some reason, the documents that we have been starting with have 10\'s to 100\'s of DOCX validation errors. These documents will generally open okay in Word or Google Docs on their own, but these validation errors cause problems when working with the open source libraries that we use to combine\r\nthe documents. We currently use cloud convert (converting from a DOCX file to an RTF file back to a DOCX file) to get rid of what seems to be most of the more serious errors, but the best way (and only way to\r\nget rid of all of the errors that I\'ve seen) is to use Microsoft Word\'s functionality for doing so. The process for doing that is recorded in the `windows_validation_converter.py` file. That file essentially does the below process, just automatically:\r\n\r\n1. Download the document from Google Drive or other cloud editor and open locally with Desktop Word (works with Word 2019, but later versions probably should too).\r\n2. Go to File > Save As, and save the file as a Rich Text Format (.rtf), and close Word.\r\n3. Open the newly saved .rtf file in Word. Go to File > Save As, and now save as a Word Document (DOCX). Make sure that the "Maintain compatibility with previous versions of Word" is checked.\r\n4. (optional) Sometimes, this process causes Word to make the background style of the tables in the document orange. To change this back to a normal white background, move your cursor into the table, and click on the "Design" tab above the ribbon. You should see the orange background in the "Table Styles". Delete it (right click > delete table style) from the document, and click on the desired table style. Save the document.\r\n5. Upload the corrected DOCX files to the Google Drive folder that this interview is using.\r\n\r\n## Authors\r\n\r\nBryce Willey, Quinten Steenhuis\r\n',
      long_description_content_type='text/markdown',
      author='Bryce Willey',
      author_email='bryce.steven.willey@gmail.com',
      license='The MIT License (MIT)',
      url='https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['airtable-python-wrapper>=0.15.2', 'docassemble.ALToolbox>=0.3.7', 'google-api-python-client>=2.15.0', 'mammoth>=1.4.18', 'numpy>=1.0.4', 'pandas>=1.2.4', 'pyairtable>=1.1.0'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/tclpgoogledocsmerger/', package='docassemble.tclpgoogledocsmerger'),
     )

