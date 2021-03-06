from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl

from ..cell.text import Text
from ..utils.indexed_list import IndexedList

from ..xml.functions import iterparse
from ..xml.constants import SHEET_MAIN_NS

from .worksheet import _get_xml_iter


def read_string_table(xml_source):
    """Read in all shared strings in the table"""
    strings = []
    src = _get_xml_iter(xml_source)

    for _, node in iterparse(src):
        if node.tag == '{%s}si' % SHEET_MAIN_NS:

            text = Text.from_tree(node).content
            text = text.replace('x005F_', '')
            strings.append(text)

            node.clear()

    return IndexedList(strings)
