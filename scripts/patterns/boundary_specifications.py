"""Concrete specifications for boundary validation."""

from typing import ClassVar

from domain.boundaries import FilePath
from patterns.specifications import Specification


class OwnedByInstance(Specification[FilePath]):
    """File belongs to instance's owned paths."""

    def __init__(self, instance_id: str):
        self.instance_id = instance_id

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return file_path.instance_owner == self.instance_id

    def reason(self) -> str:
        return f"owned by {self.instance_id}"


class InSharedPath(Specification[FilePath]):
    """File is in shared/common directory."""

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return file_path.is_shared

    def reason(self) -> str:
        return "in shared path (coordinate changes)"


class IsTestFile(Specification[FilePath]):
    """File is in tests/ directory."""

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return file_path.is_test_file

    def reason(self) -> str:
        return "in tests directory"


class IsConfigFile(Specification[FilePath]):
    """File is project-level config (.github, pyproject.toml, etc.)."""

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return file_path.is_config

    def reason(self) -> str:
        return "project-level config"


class IsCriticalFile(Specification[FilePath]):
    """File requires boundary checking (Python, YAML, TOML, JSON, Markdown)."""

    CRITICAL_EXTENSIONS: ClassVar[set[str]] = {".py", ".yaml", ".yml", ".toml", ".json", ".md"}

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return file_path.file_extension in self.CRITICAL_EXTENSIONS

    def reason(self) -> str:
        return "critical file type"


class BoundaryAllowed(Specification[FilePath]):
    """
    Composite specification: file modification is allowed.

    A file can be modified if it is:
    - Owned by the instance, OR
    - In a shared path, OR
    - A test file, OR
    - A project config file, OR
    - Not a critical file type
    """

    def __init__(self, instance_id: str):
        self.instance_id = instance_id
        self.spec = (
            OwnedByInstance(instance_id)
            | InSharedPath()
            | IsTestFile()
            | IsConfigFile()
            | ~IsCriticalFile()
        )

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return self.spec.is_satisfied_by(file_path)

    def reason(self) -> str:
        return self.spec.reason()


def create_boundary_rules(instance_id: str) -> Specification[FilePath]:
    """
    Factory for instance boundary rules.

    Creates a composite specification that allows modification if:
    - File is owned by instance
    - File is in shared directory (with warning)
    - File is a test file
    - File is a project config file
    - File is not a critical type
    """
    return BoundaryAllowed(instance_id)
