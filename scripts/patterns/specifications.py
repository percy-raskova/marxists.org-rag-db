"""Specification pattern for composable business rules."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Abstract base class for specifications with boolean operators."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies this specification."""

    @abstractmethod
    def reason(self) -> str:
        """Human-readable reason for this specification."""

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Combine specifications with AND logic."""
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Combine specifications with OR logic."""
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        """Negate specification with NOT logic."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Composite specification: both specs must be satisfied."""

    def __init__(self, *specs: Specification[T]):
        self.specs = specs

    def is_satisfied_by(self, candidate: T) -> bool:
        return all(spec.is_satisfied_by(candidate) for spec in self.specs)

    def reason(self) -> str:
        reasons = [spec.reason() for spec in self.specs]
        return " AND ".join(reasons)


class OrSpecification(Specification[T]):
    """Composite specification: at least one spec must be satisfied."""

    def __init__(self, *specs: Specification[T]):
        self.specs = specs

    def is_satisfied_by(self, candidate: T) -> bool:
        return any(spec.is_satisfied_by(candidate) for spec in self.specs)

    def reason(self) -> str:
        reasons = [spec.reason() for spec in self.specs]
        return " OR ".join(reasons)


class NotSpecification(Specification[T]):
    """Composite specification: spec must NOT be satisfied."""

    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def reason(self) -> str:
        return f"NOT ({self.spec.reason()})"
