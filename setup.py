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
      version='0.3.0',
      description=('A docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata'),
      long_description='# docassemble.tclpgoogledocsmerger\r\n\r\nA docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata.\r\n\r\nMade in association with The [Chancery Lane Project](https://chancerylaneproject.org/)\r\n\r\nSpecial dependencies:\r\n* a branch of [docxcompose](https://github.com/BryceStevenWilley/docxcompose/tree/master), version `1.3.5-devlemma`.\r\n  * this branch merges a [standing PR](https://github.com/4teamwork/docxcompose/pull/58) that works when certain styles aren\'t present\r\n  * also fixes some issues with [abstractNumId uniqueness](https://github.com/BryceStevenWilley/docxcompose/commit/a90e445857dbf61ce5c999bb50b13291b51d7b12)\r\n* a branch of [docxtpl](https://github.com/LemmaLegalConsulting/docxtpl/tree/subdoc_bookmark_issues)\r\n  * this branch fixed an issue where bookmark ids were only renumbered per subdocument, not over the whole document\r\n* a branch of [docassemble that supports optgroups](https://github.com/BryceStevenWilley/docassemble/tree/optgroups)\r\n  * also includes a [PR that prevents DA from crashing on newer versions of docxtpl](https://github.com/jhpyle/docassemble/pull/504), which the previous branch includes\r\n\r\n## Refreshing the Airtable Data Source.\r\n\r\nThis interview uses the data in [an Airtable](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY), exported to a CSV file, to\r\ndetermine which clause applies to a particular query.\r\n\r\nThere are two parts to updating this data source: setting up a way to modify the installed interview on a server, and\r\nactually updating the CSV file. The first step only needs to be done once, per user per server.\r\n\r\n### Modifying an installed interview\r\n\r\n1. Login to your server. You should have at least developer privileges.\r\n2. Go to the playground (click your email on the top right of the screen to reveal a drop down, then click on "Playground").\r\n  ![Use the drop down menu on the top right to then get to the playground](assets/get-to-playground.png)\r\n3. Once in the playground, you need to pull the latest version of the code from Github. Click "Folders > packages", then "Pull".\r\n  ![In the playground screen, press "Folders > packages"](assets/playground-packages.png)\r\n\r\n  ![On the packages screen, press "Pull"](assets/get-to-pull.png)\r\n\r\n4. There, enter the information of this github repo:\r\n  * github url: https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger\r\n  * branch: main\r\n  Press pull.\r\n  ![Enter the information into these screens, then press "Pull".](assets/pull-github.png)\r\n5. Press back (top left of the screen) until you are at the playground screen again.\r\n\r\n### Updating the CSV file.\r\n\r\n1. Go to the [Airtable with the clause data](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY).\r\n2. Press "download as CSV", hidden behind the three dots. Save the CSV file on your computer as `Grid_view.csv`.\r\n  ![On the Airtable base, press the three dots, then "Download as CSV"](airtable.png)\r\n3. Go back to your playground on the docassemble server.\r\n4. In the playground, go to "Folders > Sources".\r\n  ![Go to the sources file with "Folders > sources"](assets/playground-sources.png)\r\n5. On the sources page, upload the `Grid_view.csv` file by pressing "Browse..." and then "Upload".\r\n  ![The sources screen: upload the CSV file, then press "Upload"](upload-source.png)\r\n6. Press back (top left) to go back to the playground. Then go to "Folders > packages".\r\n  ![In the playground screen, press "Folders > packages", then "Pull" on the new screen](assets/playground-packages.png)\r\n7. (optional) on this screen, you can update the version. This allows you to easily know what version of the Airtable document\r\n  is being used in production. Change the version to anything you like. The default looks like 1.2.3, but you can add text as well, i.e.\r\n  1.2.3-march-data. Change this version number and press save at the bottom of the screen.\r\n8. Press "Install" at the bottom of the screen. This will cause the server to restart, so avoid updating during peak traffic times.\r\n\r\n## Adding new Clauses\r\n\r\nOnce a clause is present in the Airtable data (see above), you can add its corresponding DOCX to the Google Drive folder, and it will be found and downloaded by this interview. It\'s important that the name of the DOCX in the Drive folder have the exact name of the clause somewhere in it, with the same spelling as in the Airtable. Otherwise, it won\'t be found and downloaded by this interview (ignoring `&` and `\'`). For example, if the DOCX\'s name is "Gilbert _ Sullivan_s Clause - V3", and the Airtable "Child name" is "Gilbert & Sullivan\'s Clause", that\'s okay. But if the DOCX\'s name is "Chris_s Clause - V4" and the Aritable name is "Chris\' Clause", it won\'t be found.\r\n\r\nFor some reason, the documents that we have been starting with have 10\'s to 100\'s of DOCX validation errors. These documents will generally open okay in Word or Google Docs on their own, but these validation errors cause problems when working with the open source libraries that we use to combine\r\nthe documents. The easiest way to prevent these validation errors from causing problems is to just\r\nremove them from the original documents. That process is described below:\r\n\r\n1. Download the document from Google Drive or other cloud editor and open locally with Destop Word (works with Word 2019, but later versions probably should too).\r\n2. Go to File > Save As, and save the file as a Rich Text Format (.rtf), and close Word.\r\n3. Open the newly saved .rtf file in Word. Go to File > Save As, and now save as a Word Document (DOCX). Make sure that the "Maintain compatability with previous versions of Word" is checked.\r\n4. (optional) Sometimes, this process causes Word to make the background style of the tables in the document orange. To change this back to a normal white background, move your cursor into the table, and click on the "Design" tab above the ribbon. You should see the orange background in the "Table Styles". Delete it (right click > delete table style) from the document, and click on the desired table style. Save the document.\r\n5. Upload the corrected DOCX files to the Google Drive folder that this interview is using.\r\n\r\n## Authors\r\n\r\nBryce Willey, Quinten Steenhuis\r\n\r\n',
      long_description_content_type='text/markdown',
      author='Bryce Willey',
      author_email='bryce.steven.willey@gmail.com',
      license='The MIT License (MIT)',
      url='https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['airtable-python-wrapper>=0.15.2', 'docassemble.ALToolbox>=0.3.7', 'google-api-python-client>=2.15.0', 'pyairtable', 'mammoth>=1.4.18', 'numpy>=1.0.4', 'pandas>=1.2.4'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/tclpgoogledocsmerger/', package='docassemble.tclpgoogledocsmerger'),
     )

