from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from ..descriptors.serialisable import Serialisable
from ..descriptors import (
    Sequence
)
from ..descriptors.excel import (
    Relation,
)

class ExternalReference(Serialisable):

    tagname = "externalReference"

    id = Relation()

    def __init__(self, id):
        self.id = id
