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
      version='0.1.8.2',
      description=('A docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata'),
      long_description='# docassemble.tclpgoogledocsmerger\n\nA docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata.\n\nMade in association with The [Chancery Lane Project](https://chancerylaneproject.org/)\n\nSpecial dependencies:\n* a branch of [docxcompose](https://github.com/BryceStevenWilley/docxcompose/tree/master), version `1.3.5-devlemma`.\n  * this branch merges a [standing PR](https://github.com/4teamwork/docxcompose/pull/58) that works when certain styles aren\'t present\n  * also fixes some issues with [abstractNumId uniqueness](https://github.com/BryceStevenWilley/docxcompose/commit/a90e445857dbf61ce5c999bb50b13291b51d7b12)\n* a branch of [docxtpl](https://github.com/LemmaLegalConsulting/docxtpl/tree/subdoc_bookmark_issues)\n  * this branch fixed an issue where bookmark ids were only renumbered per subdocument, not over the whole document\n* a branch of [docassemble that supports optgroups](https://github.com/BryceStevenWilley/docassemble/tree/optgroups)\n  * also includes a [PR that prevents DA from crashing on newer versions of docxtpl](https://github.com/jhpyle/docassemble/pull/504), which the previous branch includes\n\n## Refreshing the Airtable Data Source.\n\nThis interview uses the data in [an Airtable](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY), exported to a CSV file, to\ndetermine which clause applies to a particular query.\n\nThere are two parts to updating this data source: setting up a way to modify the installed interview on a server, and\nactually updating the CSV file. The first step only needs to be done once, per user per server.\n\n### Modifying an installed interview\n\n1. Login to your server. You should have at least developer privileges.\n2. Go to the playground (click your email on the top right of the screen to reveal a drop down, then click on "Playground").\n  ![Use the drop down menu on the top right to then get to the playground](assets/get-to-playground.png)\n3. Once in the playground, you need to pull the latest version of the code from Github. Click "Folders > packages", then "Pull".\n  ![In the playground screen, press "Folders > packages"](assets/playground-packages.png)\n\n  ![On the packages screen, press "Pull"](assets/get-to-pull.png)\n\n4. There, enter the information of this github repo:\n  * github url: https://github.com/LemmaLegalConsulting/docassemble-tclpgoogledocsmerger\n  * branch: main\n  Press pull.\n  ![Enter the information into these screens, then press "Pull".](assets/pull-github.png)\n5. Press back (top left of the screen) until you are at the playground screen again.\n\n### Updating the CSV file.\n\n1. Go to the [Airtable with the clause data](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY).\n2. Press "download as CSV", hidden behind the three dots. Save the CSV file on your computer as `Grid_view.csv`.\n  ![On the Airtable base, press the three dots, then "Download as CSV"](airtable.png)\n3. Go back to your playground on the docassemble server.\n4. In the playground, go to "Folders > Sources".\n  ![Go to the sources file with "Folders > sources"](assets/playground-sources.png)\n5. On the sources page, upload the `Grid_view.csv` file by pressing "Browse..." and then "Upload".\n  ![The sources screen: upload the CSV file, then press "Upload"](upload-source.png)\n6. Press back (top left) to go back to the playground. Then go to "Folders > packages".\n  ![In the playground screen, press "Folders > packages", then "Pull" on the new screen](assets/playground-packages.png)\n7. (optional) on this screen, you can update the version. This allows you to easily know what version of the Airtable document\n  is being used in production. Change the version to anything you like. The default looks like 1.2.3, but you can add text as well, i.e.\n  1.2.3-march-data. Change this version number and press save at the bottom of the screen.\n8. Press "Install" at the bottom of the screen. This will cause the server to restart, so avoid updating during peak traffic times.\n\n\n## Authors\n\nBryce Willey, Quinten Steenhuis\n\n',
      long_description_content_type='text/markdown',
      author='Bryce Willey',
      author_email='bryce.steven.willey@gmail.com',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['airtable-python-wrapper>=0.15.2', 'google-api-python-client>=2.15.0', 'mammoth>=1.4.18', 'numpy>=1.0.4', 'pandas>=1.2.4'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/tclpgoogledocsmerger/', package='docassemble.tclpgoogledocsmerger'),
     )

