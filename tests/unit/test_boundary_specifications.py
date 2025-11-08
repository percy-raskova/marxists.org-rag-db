"""Unit tests for boundary specifications."""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path so we can import like the scripts do
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from domain.boundaries import FilePath
from patterns.boundary_specifications import (
    BoundaryAllowed,
    InSharedPath,
    IsConfigFile,
    IsCriticalFile,
    IsTestFile,
    OwnedByInstance,
    create_boundary_rules,
)


@pytest.fixture
def mock_owner_resolver():
    """Mock instance owner resolver."""

    def resolver(path_str: str) -> str | None:
        if "instance1_storage" in path_str:
            return "instance1"
        elif "instance2_embeddings" in path_str:
            return "instance2"
        return None

    return resolver


@pytest.fixture
def mock_shared_checker():
    """Mock shared path checker."""

    def checker(path_str: str) -> bool:
        return "shared/" in path_str or path_str.startswith("src/mia_rag/interfaces/")

    return checker


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root."""
    return tmp_path


def test_owned_by_instance_satisfied(mock_owner_resolver, mock_shared_checker, project_root):
    """Test OwnedByInstance specification when file is owned by instance."""
    file_path = FilePath.from_path(
        "tests/unit/instance1_storage/test_storage.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = OwnedByInstance("instance1")
    assert spec.is_satisfied_by(file_path)
    assert "instance1" in spec.reason()


def test_owned_by_instance_not_satisfied(mock_owner_resolver, mock_shared_checker, project_root):
    """Test OwnedByInstance specification when file is owned by different instance."""
    file_path = FilePath.from_path(
        "tests/unit/instance2_embeddings/test_embeddings.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = OwnedByInstance("instance1")
    assert not spec.is_satisfied_by(file_path)


def test_in_shared_path(mock_owner_resolver, mock_shared_checker, project_root):
    """Test InSharedPath specification."""
    file_path = FilePath.from_path(
        "src/mia_rag/interfaces/contracts.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = InSharedPath()
    assert spec.is_satisfied_by(file_path)
    assert "shared" in spec.reason().lower()


def test_is_test_file(mock_owner_resolver, mock_shared_checker, project_root):
    """Test IsTestFile specification."""
    file_path = FilePath.from_path(
        "tests/unit/test_something.py", project_root, mock_owner_resolver, mock_shared_checker
    )

    spec = IsTestFile()
    assert spec.is_satisfied_by(file_path)
    assert "test" in spec.reason().lower()


def test_is_config_file(mock_owner_resolver, mock_shared_checker, project_root):
    """Test IsConfigFile specification."""
    file_path = FilePath.from_path(
        "pyproject.toml", project_root, mock_owner_resolver, mock_shared_checker
    )

    spec = IsConfigFile()
    assert spec.is_satisfied_by(file_path)
    assert "config" in spec.reason().lower()


def test_is_critical_file_python(mock_owner_resolver, mock_shared_checker, project_root):
    """Test IsCriticalFile specification for Python files."""
    file_path = FilePath.from_path(
        "src/module.py", project_root, mock_owner_resolver, mock_shared_checker
    )

    spec = IsCriticalFile()
    assert spec.is_satisfied_by(file_path)


def test_is_critical_file_non_critical(mock_owner_resolver, mock_shared_checker, project_root):
    """Test IsCriticalFile specification for non-critical files."""
    file_path = FilePath.from_path(
        "image.png", project_root, mock_owner_resolver, mock_shared_checker
    )

    spec = IsCriticalFile()
    assert not spec.is_satisfied_by(file_path)


def test_boundary_allowed_owned(mock_owner_resolver, mock_shared_checker, project_root):
    """Test BoundaryAllowed when file is owned by instance."""
    file_path = FilePath.from_path(
        "src/instance1_storage/storage.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = BoundaryAllowed("instance1")
    assert spec.is_satisfied_by(file_path)


def test_boundary_allowed_shared(mock_owner_resolver, mock_shared_checker, project_root):
    """Test BoundaryAllowed for shared files."""
    file_path = FilePath.from_path(
        "src/mia_rag/interfaces/contracts.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = BoundaryAllowed("instance1")
    assert spec.is_satisfied_by(file_path)


def test_boundary_allowed_not_owned(mock_owner_resolver, mock_shared_checker, project_root):
    """Test BoundaryAllowed when file is owned by different instance."""
    file_path = FilePath.from_path(
        "src/instance2_embeddings/embeddings.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    spec = BoundaryAllowed("instance1")
    # Should fail because owned by instance2, not shared, not test, not config
    assert not spec.is_satisfied_by(file_path)


def test_boundary_allowed_non_critical(mock_owner_resolver, mock_shared_checker, project_root):
    """Test BoundaryAllowed for non-critical files."""
    file_path = FilePath.from_path(
        "docs/image.png", project_root, mock_owner_resolver, mock_shared_checker
    )

    spec = BoundaryAllowed("instance1")
    # Should pass because non-critical files are allowed
    assert spec.is_satisfied_by(file_path)


def test_create_boundary_rules(mock_owner_resolver, mock_shared_checker, project_root):
    """Test create_boundary_rules factory."""
    spec = create_boundary_rules("instance1")

    # Test owned file
    owned_file = FilePath.from_path(
        "src/instance1_storage/storage.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )
    assert spec.is_satisfied_by(owned_file)

    # Test not owned file
    not_owned_file = FilePath.from_path(
        "src/instance2_embeddings/embeddings.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )
    assert not spec.is_satisfied_by(not_owned_file)


def test_specification_and_operator(mock_owner_resolver, mock_shared_checker, project_root):
    """Test AND operator for specifications."""
    file_path = FilePath.from_path(
        "tests/unit/instance1_storage/test_storage.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    # File is both a test file AND owned by instance1
    spec = IsTestFile() & OwnedByInstance("instance1")
    assert spec.is_satisfied_by(file_path)


def test_specification_or_operator(mock_owner_resolver, mock_shared_checker, project_root):
    """Test OR operator for specifications."""
    file_path = FilePath.from_path(
        "tests/unit/instance2_embeddings/test_embeddings.py",
        project_root,
        mock_owner_resolver,
        mock_shared_checker,
    )

    # File is either a test file OR owned by instance1 (it's a test file)
    spec = IsTestFile() | OwnedByInstance("instance1")
    assert spec.is_satisfied_by(file_path)


def test_specification_not_operator(mock_owner_resolver, mock_shared_checker, project_root):
    """Test NOT operator for specifications."""
    file_path = FilePath.from_path(
        "image.png", project_root, mock_owner_resolver, mock_shared_checker
    )

    # File is NOT a critical file
    spec = ~IsCriticalFile()
    assert spec.is_satisfied_by(file_path)
