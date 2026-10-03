"""Compatibility shim; use :mod:`mla_project.data.make_splits`."""

from mla_project.data.make_splits import make_splits, normalized_text_hash

__all__ = ["make_splits", "normalized_text_hash"]
