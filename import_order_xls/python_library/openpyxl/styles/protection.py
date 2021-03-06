from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl

from ..descriptors import Bool
from ..descriptors.serialisable import Serialisable


class Protection(Serialisable):
    """Protection options for use in styles."""

    tagname = "protection"

    locked = Bool()
    hidden = Bool()

    def __init__(self, locked=True, hidden=False):
        self.locked = locked
        self.hidden = hidden
