"""
Visitor pattern implementations for interface validation.

This module implements the Visitor pattern to separate AST traversal
logic from validation business rules. Each visitor focuses on a
specific aspect of interface contract validation.
"""

import ast
from abc import ABC, abstractmethod

from scripts.domain.interfaces import InterfaceDefinition, ValidationContext
from scripts.patterns.repositories import InterfaceRepository


class InterfaceVisitor(ast.NodeVisitor, ABC):
    """Base visitor for interface validation.

    This abstract base class defines the contract for all interface
    validation visitors. Each concrete visitor implements specific
    validation rules while the base class handles common functionality.

    The Visitor pattern allows us to:
    - Separate AST traversal from business logic
    - Add new validation rules without modifying existing code
    - Test each validation rule independently
    """

    def __init__(self, ctx: ValidationContext, repository: InterfaceRepository):
        """Initialize the visitor.

        Args:
            ctx: Shared validation context
            repository: Repository for looking up interface definitions
        """
        self.ctx = ctx
        self.repository = repository

    @abstractmethod
    def get_violations(self) -> list:
        """Return collected violations.

        Returns:
            List of InterfaceViolation objects found by this visitor
        """
        pass


class InterfaceInheritanceVisitor(InterfaceVisitor):
    """Validates that classes properly inherit from interfaces.

    This visitor checks:
    - Classes that claim to implement interfaces actually inherit from them
    - Interfaces being inherited are defined in the contracts
    - Interface imports are present
    """

    def __init__(self, ctx: ValidationContext, repository: InterfaceRepository):
        """Initialize the inheritance visitor.

        Args:
            ctx: Validation context
            repository: Interface repository
        """
        super().__init__(ctx, repository)
        self._imports: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Track imported names.

        Args:
            node: Import AST node
        """
        for alias in node.names:
            self._imports.add(alias.name.split(".")[-1])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imported names from modules.

        Args:
            node: ImportFrom AST node
        """
        for alias in node.names:
            self._imports.add(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate class interface inheritance.

        Args:
            node: ClassDef AST node
        """
        # Track which interfaces this class claims to implement
        for base in node.bases:
            interface_name = None

            if isinstance(base, ast.Name):
                interface_name = base.id
            elif isinstance(base, ast.Attribute):
                interface_name = base.attr

            if interface_name:
                # Check if this is a known interface
                if self.repository.has_interface(interface_name):
                    self.ctx.declared_interfaces.add(interface_name)

                    # Warn if interface not imported
                    if interface_name not in self._imports:
                        self.ctx.add_violation(
                            line_number=node.lineno,
                            violation_type="missing_import",
                            message=f"Interface '{interface_name}' not imported",
                            severity="warning",
                            class_name=node.name,
                        )

        self.generic_visit(node)

    def get_violations(self) -> list:
        """Return violations found by this visitor.

        Returns:
            List of violations (stored in shared context)
        """
        # Violations are added directly to context
        return []


class MethodImplementationVisitor(InterfaceVisitor):
    """Validates that interface methods are implemented.

    This visitor checks that classes implementing an interface
    provide all required methods with correct signatures.
    """

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check if class implements required interface methods.

        Args:
            node: ClassDef AST node
        """
        # Set current class in context
        old_class = self.ctx.current_class
        self.ctx.current_class = node.name

        # First, collect all methods in this class
        class_methods: set[str] = set()
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_methods.add(item.name)
                self.ctx.track_method(node.name, item.name)

        # Check each interface this class implements
        for base in node.bases:
            interface_name = None

            if isinstance(base, ast.Name):
                interface_name = base.id
            elif isinstance(base, ast.Attribute):
                interface_name = base.attr

            if interface_name:
                interface_def = self.repository.get_interface(interface_name)

                if interface_def:
                    # Check that all required methods are implemented
                    required_methods = interface_def.get_all_method_names()
                    missing_methods = required_methods - class_methods

                    for method_name in missing_methods:
                        # Find the full signature for better error message
                        full_sig = next(
                            (sig for sig in interface_def.methods if sig.startswith(method_name)),
                            method_name,
                        )

                        self.ctx.add_violation(
                            line_number=node.lineno,
                            violation_type="missing_method",
                            message=f"{node.name} missing method: {full_sig}",
                            severity="error",
                            class_name=node.name,
                        )

        # Continue traversal
        self.generic_visit(node)

        # Restore context
        self.ctx.current_class = old_class

    def get_violations(self) -> list:
        """Return violations found by this visitor.

        Returns:
            List of violations (stored in shared context)
        """
        # Violations are added directly to context
        return []


class TypeAnnotationVisitor(InterfaceVisitor):
    """Validates type hints match interface contracts.

    This visitor checks that method signatures include proper
    type annotations as required by interface contracts.

    Note: This is a simplified implementation. Full signature
    validation (argument types, return types) would require
    more sophisticated AST analysis.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function type annotations.

        Args:
            node: FunctionDef AST node
        """
        # Only check if we're in a class that implements an interface
        if self.ctx.current_class and self.ctx.declared_interfaces:
            # Check for return type annotation
            if node.returns is None and not node.name.startswith("_"):
                self.ctx.add_violation(
                    line_number=node.lineno,
                    violation_type="missing_return_type",
                    message=f"Method '{node.name}' missing return type annotation",
                    severity="warning",
                    class_name=self.ctx.current_class,
                )

            # Check for argument type annotations
            for arg in node.args.args:
                if arg.arg != "self" and arg.annotation is None:
                    self.ctx.add_violation(
                        line_number=node.lineno,
                        violation_type="missing_arg_type",
                        message=f"Method '{node.name}' argument '{arg.arg}' missing type annotation",
                        severity="warning",
                        class_name=self.ctx.current_class,
                    )

        self.generic_visit(node)

    def get_violations(self) -> list:
        """Return violations found by this visitor.

        Returns:
            List of violations (stored in shared context)
        """
        # Violations are added directly to context
        return []


class InterfaceValidator:
    """Orchestrates interface validation using multiple visitors.

    This class coordinates the execution of all interface validation
    visitors and aggregates their results. It provides a clean,
    high-level API for interface contract validation.
    """

    def __init__(self, repository: InterfaceRepository):
        """Initialize the validator.

        Args:
            repository: Repository for interface definitions
        """
        self.repository = repository

        # Register all visitor classes
        self.visitor_classes = [
            InterfaceInheritanceVisitor,
            MethodImplementationVisitor,
            TypeAnnotationVisitor,
        ]

    def validate(self, file_path, *, enable_type_checking: bool = False):
        """Validate interface implementation in a file.

        Args:
            file_path: Path to Python file to validate
            enable_type_checking: Whether to enable strict type annotation checking

        Returns:
            List of InterfaceViolation objects
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as e:
            from scripts.domain.interfaces import InterfaceViolation
            return [
                InterfaceViolation(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    violation_type="syntax_error",
                    message=f"Syntax error: {e.msg}",
                    severity="error",
                )
            ]
        except Exception as e:
            from scripts.domain.interfaces import InterfaceViolation
            return [
                InterfaceViolation(
                    file_path=file_path,
                    line_number=0,
                    violation_type="parse_error",
                    message=f"Error parsing file: {e}",
                    severity="error",
                )
            ]

        # Create validation context
        from scripts.domain.interfaces import ValidationContext
        ctx = ValidationContext(file_path=file_path)

        # Run all visitors
        visitor_classes = self.visitor_classes.copy()
        if not enable_type_checking:
            # Skip type annotation checking unless explicitly enabled
            visitor_classes = [
                v for v in visitor_classes if v != TypeAnnotationVisitor
            ]

        for visitor_class in visitor_classes:
            visitor = visitor_class(ctx, self.repository)
            visitor.visit(tree)

        return ctx.violations
