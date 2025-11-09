"""
Domain models for interface validation.

This module contains value objects and domain entities used in the
interface contract validation process.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class InterfaceViolation:
    """Represents a violation of an interface contract.

    This is an immutable value object representing a specific
    violation found during interface validation.

    Attributes:
        file_path: Path to the file containing the violation
        line_number: Line number where the violation occurs
        violation_type: Type of violation (e.g., "missing_method", "wrong_signature")
        message: Human-readable description of the violation
        severity: Severity level of the violation
        class_name: Name of the class with the violation (optional)
    """
    file_path: Path
    line_number: int
    violation_type: str
    message: str
    severity: Literal["error", "warning"] = "error"
    class_name: str | None = None

    def __str__(self) -> str:
        """Format violation as readable string."""
        location = f"{self.file_path}:{self.line_number}"
        if self.class_name:
            location = f"{location} ({self.class_name})"
        return f"[{self.severity.upper()}] {location}: {self.message}"


@dataclass
class InterfaceDefinition:
    """Represents an interface contract definition.

    This domain entity captures the specification of an interface,
    including all methods, properties, and class methods that
    implementations must provide.

    Attributes:
        name: Interface name
        methods: List of required method signatures
        properties: List of required property names
        class_methods: List of required class method signatures
        file_path: Path to the file defining the interface
    """
    name: str
    methods: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    class_methods: list[str] = field(default_factory=list)
    file_path: Path | None = None

    def get_method_name(self, signature: str) -> str:
        """Extract method name from signature.

        Args:
            signature: Method signature like "method_name(arg1, arg2)"

        Returns:
            Just the method name part
        """
        return signature.split("(")[0]

    def get_all_method_names(self) -> set[str]:
        """Get set of all method names (without signatures).

        Returns:
            Set of method names required by this interface
        """
        return {self.get_method_name(sig) for sig in self.methods}


@dataclass
class ValidationContext:
    """Shared context for interface validation visitors.

    This context object is passed to all visitors and accumulates
    validation state and violations during AST traversal.

    Attributes:
        file_path: Path to the file being validated
        declared_interfaces: Set of interface names this class declares
        implemented_methods: Map of class names to their implemented methods
        violations: Accumulated violations found during validation
        current_class: Name of the class currently being visited (internal state)
    """
    file_path: Path
    declared_interfaces: set[str] = field(default_factory=set)
    implemented_methods: dict[str, set[str]] = field(default_factory=dict)
    violations: list[InterfaceViolation] = field(default_factory=list)
    current_class: str | None = None

    def add_violation(
        self,
        line_number: int,
        violation_type: str,
        message: str,
        severity: Literal["error", "warning"] = "error",
        class_name: str | None = None,
    ) -> None:
        """Add a violation to the context.

        Args:
            line_number: Line where violation occurs
            violation_type: Type of violation
            message: Description of the violation
            severity: Severity level
            class_name: Optional class name for context
        """
        violation = InterfaceViolation(
            file_path=self.file_path,
            line_number=line_number,
            violation_type=violation_type,
            message=message,
            severity=severity,
            class_name=class_name or self.current_class,
        )
        self.violations.append(violation)

    def track_method(self, class_name: str, method_name: str) -> None:
        """Track that a class implements a method.

        Args:
            class_name: Name of the class
            method_name: Name of the method
        """
        if class_name not in self.implemented_methods:
            self.implemented_methods[class_name] = set()
        self.implemented_methods[class_name].add(method_name)
