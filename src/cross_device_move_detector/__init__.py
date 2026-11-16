"""Cross-device move detector: detect when a file move requires copy-and-delete.

This package provides a single function, :func:`is_cross_device`, which answers
whether moving a file between two paths would cross a filesystem boundary.
"""

from .core import is_cross_device

__all__ = ["is_cross_device"]
