from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl


from ..compat import deprecated


@deprecated("""Use from ..writer.write_only import WriteOnlyCell""")
def WriteOnlyCell(ws=None, value=None):
    from .write_only import WriteOnlyCell
    return WriteOnlyCell(ws, value)
