"""Utilities for normalizing report type identifiers.

This module centralizes accepted variants and maps them to canonical
report type strings used across the codebase.
"""
from typing import Optional


def normalize_report_type(report_type: Optional[str]) -> str:
    """Normalize a report type from many possible variants to a canonical
    hyphen-separated identifier used by the schema loader.

    Accepted output values:
    - 'retail-data'
    - 'email-performance-data'
    - 'social-media-data'
    - 'all-categories'

    The function accepts kebab-case, snake_case, camelCase, PascalCase,
    space-separated, uppercase, and shorter synonyms (e.g. 'all', 'allcats').
    """
    if not report_type:
        return 'all-categories'

    s = report_type.strip().lower()

    # Replace common separators with nothing to make keyword checks simpler
    compact = s.replace('-', '').replace('_', '').replace(' ', '')

    # All categories
    if compact in ('all', 'allcategories', 'allcategory', 'allcats', 'all-categories') or 'allcategor' in compact:
        return 'all-categories'

    # Email performance
    if 'email' in compact and ('perform' in compact or 'performance' in compact):
        return 'email-performance-data'

    # Retail
    if 'retail' in compact or 'sale' in compact or 'transaction' in compact:
        return 'retail-data'

    # Social media
    if 'social' in compact or 'media' in compact or 'engage' in compact or 'impress' in compact:
        return 'social-media-data'

    # Fallback
    return 'all-categories'
