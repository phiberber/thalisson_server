# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Python37-32\lib\site-packages\cx_Freeze\initscripts\Console.py
# Compiled at: 2020-05-21 13:43:41
# Size of source mod 2**32: 1363 bytes
import os, sys, BUILD_CONSTANTS
sys.frozen = True
FILE_NAME = sys.executable
DIR_NAME = os.path.dirname(sys.executable)
if hasattr(BUILD_CONSTANTS, 'TCL_LIBRARY'):
    os.environ['TCL_LIBRARY'] = os.path.join(DIR_NAME, BUILD_CONSTANTS.TCL_LIBRARY)
if hasattr(BUILD_CONSTANTS, 'TK_LIBRARY'):
    os.environ['TK_LIBRARY'] = os.path.join(DIR_NAME, BUILD_CONSTANTS.TK_LIBRARY)
if hasattr(BUILD_CONSTANTS, 'MATPLOTLIBDATA'):
    os.environ['MATPLOTLIBDATA'] = os.path.join(DIR_NAME, BUILD_CONSTANTS.MATPLOTLIBDATA)
if hasattr(BUILD_CONSTANTS, 'PYTZ_TZDATADIR'):
    os.environ['PYTZ_TZDATADIR'] = os.path.join(DIR_NAME, BUILD_CONSTANTS.PYTZ_TZDATADIR)

def run():
    name, ext = os.path.splitext(os.path.basename(os.path.normcase(FILE_NAME)))
    moduleName = '%s__main__' % name
    code = __loader__.get_code(moduleName)
    exec(code, {'__name__': '__main__'})