"""Domain models for boundary checking."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FilePath:
    """Value object representing a file path with boundary metadata."""

    absolute: Path
    relative_to_project: Path
    instance_owner: str | None
    is_test_file: bool
    is_shared: bool
    is_config: bool
    file_extension: str

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        project_root: Path,
        owner_resolver,  # Callable[[str], Optional[str]]
        shared_checker,  # Callable[[str], bool]
    ) -> "FilePath":
        """
        Create FilePath from a path string.

        Args:
            path: File path (absolute or relative)
            project_root: Project root directory
            owner_resolver: Function to determine instance owner
            shared_checker: Function to check if path is shared

        Returns:
            FilePath value object
        """
        # Convert to Path and make absolute
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = (project_root / path_obj).resolve()

        # Make relative to project
        try:
            relative = path_obj.relative_to(project_root)
        except ValueError:
            # Path is outside project
            relative = Path(path)

        # Analyze path characteristics
        path_str = str(relative)
        is_test_file = "tests/" in path_str or path_str.startswith("tests/")
        is_shared = shared_checker(path_str)
        is_config = cls._is_config_file(path_str)
        file_extension = path_obj.suffix

        # Get owner
        instance_owner = owner_resolver(path_str) if not is_shared and not is_config else None

        return cls(
            absolute=path_obj,
            relative_to_project=relative,
            instance_owner=instance_owner,
            is_test_file=is_test_file,
            is_shared=is_shared,
            is_config=is_config,
            file_extension=file_extension,
        )

    @staticmethod
    def _is_config_file(path_str: str) -> bool:
        """Check if file is a project-level config file."""
        config_patterns = [
            ".github/",
            "pyproject.toml",
            "poetry.lock",
            ".gitignore",
            ".pre-commit-config.yaml",
            ".instance",
            "mise.toml",
            "README.md",
            "LICENSE",
        ]
        return any(pattern in path_str or path_str == pattern for pattern in config_patterns)


@dataclass(frozen=True)
class BoundaryViolation:
    """Value object representing a boundary violation."""

    file_path: FilePath
    reason: str
    severity: str  # "error" | "warning" | "info"

    def __str__(self) -> str:
        """Human-readable violation message."""
        emoji = {"error": "❌", "warning": "⚠️ ", "info": "i"}
        return f"{emoji.get(self.severity, '')} {self.file_path.relative_to_project}: {self.reason}"
