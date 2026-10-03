"""Compatibility shim; use :mod:`mla_project.data`."""

from mla_project.data.load_data import ELLIPSE_COLUMN_MAP, load_ellipse
from mla_project.data.validate_data import TARGET_COLUMNS, validate_ellipse_schema

load_dataset = load_ellipse
load_ellipse_corpus = load_ellipse
validate_schema = validate_ellipse_schema

__all__ = [
    "ELLIPSE_COLUMN_MAP",
    "TARGET_COLUMNS",
    "load_dataset",
    "load_ellipse",
    "load_ellipse_corpus",
    "validate_ellipse_schema",
    "validate_schema",
]
