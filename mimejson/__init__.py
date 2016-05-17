"""
MIMEJSON Serialization

MIMEJSON extends JSON to allow automatically serialization of large binary objects as "attached" objects.

These large object can then be LAZILY loaded. This is an ALPHA software - the exact specification
of MIMEJSON is likely to evolve through iteration.
"""
import os
from .mimejson import MIMEJSON

__version__ = open(os.path.join(os.path.dirname(__file__), "VERSION"), "r").read()
__all__ = (MIMEJSON, __version__)
