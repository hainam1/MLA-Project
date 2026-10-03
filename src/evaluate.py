"""Compatibility shim; use :mod:`mla_project.evaluation`."""

from mla_project.evaluation.regression_metrics import regression_metrics

__all__ = ["regression_metrics"]
