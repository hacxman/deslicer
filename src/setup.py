from distutils.core import setup

setup(name='deslicer',
version='0.1',
description='Deslicer client for Slic3r',
url='https://github.com/hacxman/deslicer',
packages=['deslicer'],
data_files=[],
scripts=['deslicer/deslicer',
         'utils/deslicer_merge',
         'utils/deslicer_refresh'])
