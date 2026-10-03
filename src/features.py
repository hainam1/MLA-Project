"""Compatibility shim; use :mod:`mla_project.features`."""

from mla_project.features.build_features import FeatureExtractor, load_default_extractor

__all__ = ["FeatureExtractor", "load_default_extractor"]
