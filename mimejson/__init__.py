"""
MIMEJSON Serialization

MIMEJSON extends JSON to allow automatically serialization of large binary objects as "attached" objects.

These large object can then be LAZILY loaded. This is an ALPHA software - the exact specification
of MIMEJSON is likely to evolve through iteration.
"""
from .mimejson import MIMEJSON

__all__ = (MIMEJSON,)
