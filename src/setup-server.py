from distutils.core import setup

setup(name='deslicer_server',
version='0.1',
description='JSON RPC server for running Slic3r as a remote service',
url='https://github.com/hacxman/deslicer',
packages=['deslicer_server'],
data_files=[],
scripts=['deslicerd'])
