"""
Unit tests for interface validation visitors.

Tests the Visitor pattern implementation for interface contract validation.
"""

import ast
import tempfile
from pathlib import Path

import pytest

from scripts.domain.interfaces import InterfaceDefinition, ValidationContext, InterfaceViolation
from scripts.patterns.repositories import InterfaceRepository
from scripts.patterns.visitors import (
    InterfaceInheritanceVisitor,
    InterfaceValidator,
    MethodImplementationVisitor,
    TypeAnnotationVisitor,
)


class TestInterfaceViolation:
    """Test the InterfaceViolation value object."""

    def test_violation_creation(self):
        """Test creating a violation."""
        violation = InterfaceViolation(
            file_path=Path("test.py"),
            line_number=10,
            violation_type="missing_method",
            message="Missing method foo()",
            severity="error",
            class_name="TestClass",
        )

        assert violation.file_path == Path("test.py")
        assert violation.line_number == 10
        assert violation.violation_type == "missing_method"
        assert violation.severity == "error"
        assert violation.class_name == "TestClass"

    def test_violation_string_representation(self):
        """Test violation string formatting."""
        violation = InterfaceViolation(
            file_path=Path("test.py"),
            line_number=10,
            violation_type="missing_method",
            message="Missing method foo()",
            class_name="TestClass",
        )

        result = str(violation)
        assert "test.py:10" in result
        assert "TestClass" in result
        assert "Missing method foo()" in result


class TestInterfaceDefinition:
    """Test the InterfaceDefinition domain entity."""

    def test_definition_creation(self):
        """Test creating an interface definition."""
        definition = InterfaceDefinition(
            name="TestInterface",
            methods=["foo()", "bar(x, y)"],
            properties=["prop1", "prop2"],
        )

        assert definition.name == "TestInterface"
        assert len(definition.methods) == 2
        assert len(definition.properties) == 2

    def test_get_method_name(self):
        """Test extracting method name from signature."""
        definition = InterfaceDefinition(
            name="TestInterface",
            methods=["foo()", "bar(x, y)"],
        )

        assert definition.get_method_name("foo()") == "foo"
        assert definition.get_method_name("bar(x, y)") == "bar"

    def test_get_all_method_names(self):
        """Test getting all method names."""
        definition = InterfaceDefinition(
            name="TestInterface",
            methods=["foo()", "bar(x, y)", "baz(a, b, c)"],
        )

        names = definition.get_all_method_names()
        assert names == {"foo", "bar", "baz"}


class TestValidationContext:
    """Test the ValidationContext."""

    def test_context_creation(self):
        """Test creating a validation context."""
        ctx = ValidationContext(file_path=Path("test.py"))

        assert ctx.file_path == Path("test.py")
        assert len(ctx.violations) == 0
        assert len(ctx.declared_interfaces) == 0

    def test_add_violation(self):
        """Test adding violations to context."""
        ctx = ValidationContext(file_path=Path("test.py"))

        ctx.add_violation(
            line_number=10,
            violation_type="test",
            message="Test violation",
        )

        assert len(ctx.violations) == 1
        assert ctx.violations[0].line_number == 10
        assert ctx.violations[0].message == "Test violation"

    def test_track_method(self):
        """Test tracking method implementations."""
        ctx = ValidationContext(file_path=Path("test.py"))

        ctx.track_method("ClassA", "method1")
        ctx.track_method("ClassA", "method2")
        ctx.track_method("ClassB", "method1")

        assert "method1" in ctx.implemented_methods["ClassA"]
        assert "method2" in ctx.implemented_methods["ClassA"]
        assert "method1" in ctx.implemented_methods["ClassB"]


class TestInterfaceRepository:
    """Test the InterfaceRepository."""

    def test_repository_with_nonexistent_file(self):
        """Test repository handles missing contracts file gracefully."""
        repo = InterfaceRepository(contracts_path=Path("/nonexistent/file.py"))
        repo.load()

        assert len(repo.get_all_interfaces()) == 0
        assert not repo.has_interface("TestInterface")

    def test_repository_loads_interfaces(self):
        """Test repository can load interface definitions."""
        # Create a temporary contracts file
        contracts_content = '''
from abc import ABC, abstractmethod

class TestInterface(ABC):
    @abstractmethod
    def foo(self):
        pass

    @abstractmethod
    def bar(self, x, y):
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(contracts_content)
            f.flush()
            contracts_path = Path(f.name)

        try:
            repo = InterfaceRepository(contracts_path=contracts_path)
            repo.load()

            assert repo.has_interface("TestInterface")
            interface = repo.get_interface("TestInterface")
            assert interface is not None
            assert interface.name == "TestInterface"
            assert len(interface.methods) == 2

            required_methods = repo.get_required_methods("TestInterface")
            assert "foo" in required_methods
            assert "bar" in required_methods

        finally:
            contracts_path.unlink()


class TestMethodImplementationVisitor:
    """Test the MethodImplementationVisitor."""

    def test_detects_missing_methods(self):
        """Test visitor detects missing method implementations."""
        # Create a simple interface definition
        interface_def = InterfaceDefinition(
            name="TestInterface",
            methods=["foo()", "bar(x, y)"],
        )

        # Create a mock repository
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Mock contracts file")
            f.flush()
            contracts_path = Path(f.name)

        try:
            repo = InterfaceRepository(contracts_path=contracts_path)
            repo._contracts = {"TestInterface": interface_def}
            repo._loaded = True

            # Test code with incomplete implementation
            test_code = '''
class TestClass(TestInterface):
    def foo(self):
        pass
    # Missing bar() method
'''

            tree = ast.parse(test_code)
            ctx = ValidationContext(file_path=Path("test.py"))
            ctx.declared_interfaces.add("TestInterface")

            visitor = MethodImplementationVisitor(ctx, repo)
            visitor.visit(tree)

            # Should detect missing bar() method
            violations = [v for v in ctx.violations if v.violation_type == "missing_method"]
            assert len(violations) == 1
            assert "bar" in violations[0].message

        finally:
            contracts_path.unlink()

    def test_accepts_complete_implementation(self):
        """Test visitor accepts complete implementations."""
        interface_def = InterfaceDefinition(
            name="TestInterface",
            methods=["foo()", "bar(x, y)"],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Mock contracts file")
            f.flush()
            contracts_path = Path(f.name)

        try:
            repo = InterfaceRepository(contracts_path=contracts_path)
            repo._contracts = {"TestInterface": interface_def}
            repo._loaded = True

            # Test code with complete implementation
            test_code = '''
class TestClass(TestInterface):
    def foo(self):
        pass

    def bar(self, x, y):
        pass
'''

            tree = ast.parse(test_code)
            ctx = ValidationContext(file_path=Path("test.py"))
            ctx.declared_interfaces.add("TestInterface")

            visitor = MethodImplementationVisitor(ctx, repo)
            visitor.visit(tree)

            # Should have no violations
            violations = [v for v in ctx.violations if v.violation_type == "missing_method"]
            assert len(violations) == 0

        finally:
            contracts_path.unlink()


class TestInterfaceValidator:
    """Test the InterfaceValidator orchestrator."""

    def test_validator_integration(self):
        """Test the full validation pipeline."""
        # Create interface definition
        contracts_content = '''
from abc import ABC, abstractmethod

class TestInterface(ABC):
    @abstractmethod
    def required_method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(contracts_content)
            f.flush()
            contracts_path = Path(f.name)

        # Create implementation file with violation
        impl_content = '''
class TestClass(TestInterface):
    pass  # Missing required_method
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as impl_f:
            impl_f.write(impl_content)
            impl_f.flush()
            impl_path = Path(impl_f.name)

        try:
            repo = InterfaceRepository(contracts_path=contracts_path)
            repo.load()

            validator = InterfaceValidator(repo)
            violations = validator.validate(impl_path)

            # Should detect missing method
            assert len(violations) > 0
            assert any("required_method" in str(v.message) for v in violations)

        finally:
            contracts_path.unlink()
            impl_path.unlink()

    def test_validator_handles_syntax_errors(self):
        """Test validator handles syntax errors gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Mock contracts")
            f.flush()
            contracts_path = Path(f.name)

        # Create file with syntax error
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as impl_f:
            impl_f.write("class TestClass(:\n    pass")  # Invalid syntax
            impl_f.flush()
            impl_path = Path(impl_f.name)

        try:
            repo = InterfaceRepository(contracts_path=contracts_path)
            validator = InterfaceValidator(repo)
            violations = validator.validate(impl_path)

            # Should return syntax error violation
            assert len(violations) == 1
            assert violations[0].violation_type == "syntax_error"

        finally:
            contracts_path.unlink()
            impl_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
