from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Sequence, Type, TypeVar

from pydantic.generics import GenericModel
from typing_extensions import Protocol

T = TypeVar("T")
C = TypeVar("C")


@dataclass
class LimitOffsetParams:
    limit: int
    offset: int


class AbstractParams(Protocol):
    @abstractmethod
    def to_limit_offset(self) -> LimitOffsetParams:
        pass  # pragma: no cover


class AbstractPage(GenericModel, Generic[T], ABC):
    @classmethod
    @abstractmethod
    def create(cls: Type[C], items: Sequence[T], total: int, params: AbstractParams) -> C:
        pass  # pragma: no cover

    class Config:
        arbitrary_types_allowed = True


__all__ = [
    "AbstractPage",
    "AbstractParams",
    "LimitOffsetParams",
]
