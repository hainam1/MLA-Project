# -*- coding: utf-8 -*-
"""
Model 1: Translator Module (CapyVocab ML Pipeline).
Base Model: Helsinki-NLP/opus-mt-vi-en (MarianMT).
Task: Vietnamese -> English translation.
"""

from .service import TranslatorService

__all__ = ["TranslatorService"]
