from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl

from ..descriptors.serialisable import Serialisable
from ..descriptors import (
    Integer,
    String,
    Sequence,
)


class MergeCell(Serialisable):

    tagname = "mergeCell"

    ref = String()

    def __init__(self,
                 ref=None,
                ):
        self.ref = ref


class MergeCells(Serialisable):

    tagname = "mergeCells"

    count = Integer(allow_none=True)
    mergeCell = Sequence(expected_type=MergeCell, )

    __elements__ = ('mergeCell',)
    __attrs__ = ('count',)

    def __init__(self,
                 count=None,
                 mergeCell=(),
                ):
        self.mergeCell = mergeCell


    @property
    def count(self):
        return len(self.mergeCell)
