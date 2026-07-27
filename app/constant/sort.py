"""Sorting constants and enums."""

from enum import StrEnum


class SortOrder(StrEnum):
    """Sort direction enumeration."""

    ASC = "asc"
    DESC = "desc"


BaseSortField = StrEnum
