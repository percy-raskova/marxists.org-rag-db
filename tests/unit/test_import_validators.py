"""Unit tests for import validators using Chain of Responsibility pattern.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import tempfile
from pathlib import Path

import pytest

from scripts.patterns.ast_utils import ImportStatement, extract_imports
from scripts.patterns.validators import (
    CrossInstanceValidator,
    ImportViolation,
    OwnedPathValidator,
    SharedImportValidator,
    ValidationContext,
    create_validation_chain,
)


@pytest.fixture
def test_context() -> ValidationContext:
    """Create a test validation context for instance1."""
    return ValidationContext(
        instance_id="instance1",
        owned_paths={"src/mia_rag/storage/", "src/mia_rag/pipeline/"},
        allowed_imports={"src/mia_rag/common/", "src/mia_rag/interfaces/"},
        all_instance_boundaries={
            "instance1": ["src/mia_rag/storage/", "src/mia_rag/pipeline/"],
            "instance2": ["src/mia_rag/embeddings/"],
            "instance3": ["src/mia_rag/weaviate/"],
        },
    )


@pytest.fixture
def sample_import_owned() -> ImportStatement:
    """Create a sample import from owned path."""
    return ImportStatement(
        module="src.mia_rag.storage.adapter",
        names=["StorageAdapter"],
        level=0,
        source_file=Path("test.py"),
        line_number=1,
        is_from_import=True,
    )


@pytest.fixture
def sample_import_allowed() -> ImportStatement:
    """Create a sample import from allowed path (common)."""
    return ImportStatement(
        module="src.mia_rag.common.types",
        names=["Document"],
        level=0,
        source_file=Path("test.py"),
        line_number=2,
        is_from_import=True,
    )


@pytest.fixture
def sample_import_cross_instance() -> ImportStatement:
    """Create a sample import from another instance."""
    return ImportStatement(
        module="src.mia_rag.embeddings.generator",
        names=["EmbeddingGenerator"],
        level=0,
        source_file=Path("test.py"),
        line_number=3,
        is_from_import=True,
    )


@pytest.fixture
def sample_import_external() -> ImportStatement:
    """Create a sample import from external package."""
    return ImportStatement(
        module="requests",
        names=["get"],
        level=0,
        source_file=Path("test.py"),
        line_number=4,
        is_from_import=True,
    )


class TestOwnedPathValidator:
    """Test the OwnedPathValidator."""

    def test_owned_path_import_valid(self, test_context, sample_import_owned):
        """Test that imports from owned paths are valid."""
        validator = OwnedPathValidator()
        violation = validator.validate(sample_import_owned, test_context)
        assert violation is None

    def test_allowed_path_import_valid(self, test_context, sample_import_allowed):
        """Test that imports from allowed paths are valid."""
        validator = OwnedPathValidator()
        violation = validator.validate(sample_import_allowed, test_context)
        assert violation is None

    def test_external_import_valid(self, test_context, sample_import_external):
        """Test that external imports are not checked."""
        validator = OwnedPathValidator()
        violation = validator.validate(sample_import_external, test_context)
        assert violation is None


class TestSharedImportValidator:
    """Test the SharedImportValidator."""

    def test_shared_import_valid(self, test_context, sample_import_allowed):
        """Test that shared/common imports are valid."""
        validator = SharedImportValidator()
        violation = validator.validate(sample_import_allowed, test_context)
        assert violation is None

    def test_non_shared_import_passes(self, test_context, sample_import_owned):
        """Test that non-shared imports pass through this validator."""
        validator = SharedImportValidator()
        violation = validator.validate(sample_import_owned, test_context)
        assert violation is None


class TestCrossInstanceValidator:
    """Test the CrossInstanceValidator."""

    def test_cross_instance_import_invalid(self, test_context, sample_import_cross_instance):
        """Test that cross-instance imports are caught."""
        validator = CrossInstanceValidator()
        violation = validator.validate(sample_import_cross_instance, test_context)

        assert violation is not None
        assert isinstance(violation, ImportViolation)
        assert violation.severity == "error"
        assert "instance2" in violation.message
        assert violation.validator_name == "CrossInstanceValidator"

    def test_owned_path_import_valid(self, test_context, sample_import_owned):
        """Test that owned path imports are valid."""
        validator = CrossInstanceValidator()
        violation = validator.validate(sample_import_owned, test_context)
        assert violation is None

    def test_external_import_valid(self, test_context, sample_import_external):
        """Test that external imports are not checked."""
        validator = CrossInstanceValidator()
        violation = validator.validate(sample_import_external, test_context)
        assert violation is None


class TestValidationChain:
    """Test the full validation chain."""

    def test_chain_owned_path_valid(self, test_context, sample_import_owned):
        """Test that owned path imports pass the full chain."""
        chain = create_validation_chain()
        violations = chain.handle(sample_import_owned, test_context)
        assert len(violations) == 0

    def test_chain_allowed_path_valid(self, test_context, sample_import_allowed):
        """Test that allowed path imports pass the full chain."""
        chain = create_validation_chain()
        violations = chain.handle(sample_import_allowed, test_context)
        assert len(violations) == 0

    def test_chain_cross_instance_invalid(self, test_context, sample_import_cross_instance):
        """Test that cross-instance imports are caught by the chain."""
        chain = create_validation_chain()
        violations = chain.handle(sample_import_cross_instance, test_context)

        assert len(violations) == 1
        assert violations[0].severity == "error"
        assert "instance2" in violations[0].message

    def test_chain_external_import_valid(self, test_context, sample_import_external):
        """Test that external imports pass the chain."""
        chain = create_validation_chain()
        violations = chain.handle(sample_import_external, test_context)
        assert len(violations) == 0


class TestExtractImports:
    """Test the AST-based import extraction."""

    def test_extract_simple_import(self):
        """Test extraction of simple import statement."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            imports = extract_imports(temp_path)
            assert len(imports) == 1
            assert imports[0].module == "os"
            assert imports[0].is_from_import is False
        finally:
            temp_path.unlink()

    def test_extract_from_import(self):
        """Test extraction of from-import statement."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("from src.mia_rag.storage import StorageAdapter\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            imports = extract_imports(temp_path)
            assert len(imports) == 1
            assert imports[0].module == "src.mia_rag.storage"
            assert imports[0].names == ["StorageAdapter"]
            assert imports[0].is_from_import is True
            assert imports[0].module_path == "src/mia_rag/storage/"
        finally:
            temp_path.unlink()

    def test_extract_multiple_imports(self):
        """Test extraction of multiple import statements."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                "import os\n"
                "from src.mia_rag.common import types\n"
                "from src.mia_rag.storage import StorageAdapter\n"
            )
            f.flush()
            temp_path = Path(f.name)

        try:
            imports = extract_imports(temp_path)
            assert len(imports) == 3
        finally:
            temp_path.unlink()

    def test_extract_from_nonexistent_file(self):
        """Test that extraction fails gracefully for non-existent files."""
        with pytest.raises(FileNotFoundError):
            extract_imports(Path("/nonexistent/file.py"))

    def test_extract_from_invalid_syntax(self):
        """Test that extraction raises SyntaxError for invalid Python."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("this is not valid python syntax!!!\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(SyntaxError):
                extract_imports(temp_path)
        finally:
            temp_path.unlink()


class TestIntegration:
    """Integration tests for the full import checking workflow."""

    def test_full_validation_workflow(self, test_context):
        """Test the complete workflow from file to violations."""
        # Create a test file with various imports
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                "from src.mia_rag.storage import StorageAdapter\n"  # Valid: owned
                "from src.mia_rag.common import types\n"  # Valid: allowed
                "from src.mia_rag.embeddings import EmbeddingGenerator\n"  # Invalid: cross-instance
                "import requests\n"  # Valid: external
            )
            f.flush()
            temp_path = Path(f.name)

        try:
            # Extract imports
            imports = extract_imports(temp_path)
            assert len(imports) == 4

            # Validate with chain
            chain = create_validation_chain()
            all_violations = []
            for import_stmt in imports:
                violations = chain.handle(import_stmt, test_context)
                all_violations.extend(violations)

            # Should have exactly 1 violation (cross-instance import)
            assert len(all_violations) == 1
            assert "instance2" in all_violations[0].message

        finally:
            temp_path.unlink()
