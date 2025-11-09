"""Import validation using Chain of Responsibility pattern.

This module provides a flexible validation chain for Python import statements,
allowing modular and testable validation rules.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .ast_utils import ImportStatement


@dataclass(frozen=True)
class ValidationContext:
    """Context information for import validation.

    Attributes:
        instance_id: The instance doing the importing (e.g., 'instance1')
        owned_paths: Set of paths that this instance owns
        allowed_imports: Set of paths this instance can import from
        all_instance_boundaries: Dictionary mapping instance IDs to their owned paths
    """
    instance_id: str
    owned_paths: set[str]
    allowed_imports: set[str]
    all_instance_boundaries: dict[str, list[str]]


@dataclass(frozen=True)
class ImportViolation:
    """Represents an import validation violation.

    Attributes:
        import_statement: The import statement that violated the rule
        validator_name: Name of the validator that caught this violation
        message: Human-readable description of the violation
        severity: Severity level ('error', 'warning', 'info')
    """
    import_statement: ImportStatement
    validator_name: str
    message: str
    severity: str = "error"


class ImportValidator(ABC):
    """Abstract base class for import validators using Chain of Responsibility pattern.

    Each validator in the chain checks one specific aspect of import validity,
    then passes to the next validator if one is configured.
    """

    def __init__(self, next_handler: Optional["ImportValidator"] = None):
        """Initialize the validator with optional next handler.

        Args:
            next_handler: Next validator in the chain, or None if this is the last
        """
        self._next = next_handler

    @abstractmethod
    def validate(
        self, import_stmt: ImportStatement, ctx: ValidationContext
    ) -> Optional[ImportViolation]:
        """Validate a single import statement.

        Args:
            import_stmt: The import statement to validate
            ctx: Validation context with instance boundaries

        Returns:
            ImportViolation if validation fails, None if valid
        """
        pass

    def handle(
        self, import_stmt: ImportStatement, ctx: ValidationContext
    ) -> list[ImportViolation]:
        """Handle validation by checking this validator and passing to next.

        Args:
            import_stmt: The import statement to validate
            ctx: Validation context with instance boundaries

        Returns:
            List of all violations found in the chain
        """
        violations = []

        # Check this validator
        if violation := self.validate(import_stmt, ctx):
            violations.append(violation)

        # Pass to next handler if configured
        if self._next:
            violations.extend(self._next.handle(import_stmt, ctx))

        return violations


class OwnedPathValidator(ImportValidator):
    """Validates that instance only imports from owned or allowed paths.

    This validator checks if an import comes from a path that the instance
    either owns or is explicitly allowed to import from.
    """

    def validate(
        self, import_stmt: ImportStatement, ctx: ValidationContext
    ) -> Optional[ImportViolation]:
        """Check if import is from owned or allowed path.

        Args:
            import_stmt: The import statement to validate
            ctx: Validation context

        Returns:
            None if import is valid, ImportViolation otherwise
        """
        # Only check imports from src/ paths
        if not import_stmt.module.startswith("src"):
            return None

        module_path = import_stmt.module_path

        # Check if import is from owned paths
        for owned in ctx.owned_paths:
            if module_path.startswith(owned):
                return None

        # Check if import is from allowed paths
        for allowed in ctx.allowed_imports:
            if module_path.startswith(allowed):
                return None

        # Import is not from owned or allowed paths
        # (will be caught by CrossInstanceValidator if it's from another instance)
        return None


class SharedImportValidator(ImportValidator):
    """Validates shared module usage patterns.

    This validator ensures that shared/common modules are used correctly
    and don't create circular dependencies.
    """

    def validate(
        self, import_stmt: ImportStatement, ctx: ValidationContext
    ) -> Optional[ImportViolation]:
        """Check if shared module import is valid.

        Args:
            import_stmt: The import statement to validate
            ctx: Validation context

        Returns:
            None if import is valid, ImportViolation otherwise
        """
        # Currently, shared modules (common/, interfaces/) are always allowed
        # This validator can be extended to check for circular dependencies
        # or enforce specific shared module usage patterns

        module_path = import_stmt.module_path

        # Check if this is a shared module import
        shared_prefixes = ["src/mia_rag/common/", "src/mia_rag/interfaces/"]
        is_shared = any(module_path.startswith(prefix) for prefix in shared_prefixes)

        if is_shared:
            # Could add additional validation logic here
            # For now, shared imports are always valid
            pass

        return None


class CrossInstanceValidator(ImportValidator):
    """Detects forbidden cross-instance imports.

    This validator ensures that instances don't import from each other's
    owned paths, which would violate boundary separation.
    """

    def validate(
        self, import_stmt: ImportStatement, ctx: ValidationContext
    ) -> Optional[ImportViolation]:
        """Check if import violates instance boundaries.

        Args:
            import_stmt: The import statement to validate
            ctx: Validation context

        Returns:
            ImportViolation if import crosses instance boundary, None otherwise
        """
        # Only check imports from src/ paths
        if not import_stmt.module.startswith("src"):
            return None

        module_path = import_stmt.module_path

        # Check if this import is from another instance's owned paths
        for other_instance, owned_paths in ctx.all_instance_boundaries.items():
            # Skip our own instance
            if other_instance == ctx.instance_id:
                continue

            # Check if importing from this instance's paths
            for other_path in owned_paths:
                if module_path.startswith(other_path):
                    return ImportViolation(
                        import_statement=import_stmt,
                        validator_name="CrossInstanceValidator",
                        message=f"Cannot import from {other_instance}'s module: "
                        f"{import_stmt.module} (line {import_stmt.line_number})",
                        severity="error",
                    )

        return None


def create_validation_chain() -> ImportValidator:
    """Create the standard validation chain for import checking.

    Returns:
        Root validator in the chain (OwnedPathValidator)
    """
    return OwnedPathValidator(
        SharedImportValidator(
            CrossInstanceValidator()
        )
    )
