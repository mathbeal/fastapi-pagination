from __future__ import annotations

from fastapi import Query
from pydantic.dataclasses import dataclass

from .bases import LimitOffsetParams


@dataclass
class PaginationParams:
    page: int = Query(0, ge=0, description="Page number")
    size: int = Query(50, gt=0, le=100, description="Page size")

    def to_limit_offset(self) -> LimitOffsetParams:
        return LimitOffsetParams(
            limit=self.size,
            offset=self.size * self.page,
        )


@dataclass
class LimitOffsetPaginationParams:
    limit: int = Query(50, gt=0, le=100, description="Page size limit")
    offset: int = Query(0, ge=0, description="Page offset")

    def to_limit_offset(self) -> LimitOffsetParams:
        return LimitOffsetParams(
            limit=self.limit,
            offset=self.offset,
        )


__all__ = [
    "LimitOffsetPaginationParams",
    "PaginationParams",
]
