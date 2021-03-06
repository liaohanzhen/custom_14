from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl

from ..descriptors.serialisable import Serialisable
from ..descriptors.excel import Relation


class Drawing(Serialisable):

    tagname = "drawing"

    id = Relation()

    def __init__(self, id=None):
        self.id = id
