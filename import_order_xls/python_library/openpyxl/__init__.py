# Copyright (c) 2010-2016 openpyxl

# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file


import json
import os

try:
    here = os.path.abspath(os.path.dirname(__file__))
    src_file = os.path.join(here, ".constants.json")
    with open(src_file) as src:
        constants = json.load(src)
        __author__ = constants['__author__']
        __author_email__ = constants["__author_email__"]
        __license__ = constants["__license__"]
        __maintainer_email__ = constants["__maintainer_email__"]
        __url__ = constants["__url__"]
        __version__ = constants["__version__"]
except IOError:
    # packaged
    pass

"""Imports for the openpyxl package."""

from .compat.numbers import NUMPY, PANDAS
from .xml import LXML

from .workbook import Workbook
from .reader.excel import load_workbook
