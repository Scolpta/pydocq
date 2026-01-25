"""SDK for adding custom metadata to Python code.

This module provides decorators and utilities for adding structured
metadata to Python code for better documentation and AI agent understanding.
"""

from pydocq.sdk.decorators import (
    author,
    category,
    deprecated,
    example,
    metadata,
    note,
    param,
    returns,
    see_also,
    tag,
    when,
)
from pydocq.sdk.decorators import (
    clear_metadata,
    get_metadata,
    get_metadata_dict,
)
from pydocq.sdk.decorators import Metadata as Metadata

__all__ = [
    "Metadata",
    "metadata",
    "example",
    "deprecated",
    "param",
    "returns",
    "category",
    "when",
    "tag",
    "note",
    "author",
    "see_also",
    "get_metadata",
    "get_metadata_dict",
    "clear_metadata",
]
