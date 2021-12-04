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
      version='0.0.3',
      description=('A docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata'),
      long_description='# docassemble.tclpgoogledocsmerger\r\n\r\nA docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata.\r\n\r\nMade in association with The [Chancery Lane Project](https://chancerylaneproject.org/)\r\n\r\n## Author\r\n\r\nBryce Willey, Quinten Steenhuis\r\n\r\n',
      long_description_content_type='text/markdown',
      author='Bryce Willey',
      author_email='bryce.steven.willey@gmail.com',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['airtable-python-wrapper>=0.15.2', 'google-api-python-client>=2.15.0', 'numpy>=1.0.4', 'pandas>=1.2.4'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/tclpgoogledocsmerger/', package='docassemble.tclpgoogledocsmerger'),
     )

