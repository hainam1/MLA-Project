"""Compatibility shim; use :mod:`mla_project.evaluation.error_analysis`."""

from mla_project.evaluation.error_analysis import build_error_analysis

prediction_frame = build_error_analysis

__all__ = ["build_error_analysis", "prediction_frame"]
