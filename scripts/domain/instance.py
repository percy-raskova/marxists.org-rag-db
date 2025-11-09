"""Domain models for instance management."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class InstanceInfo:
    """Value object representing instance metadata and ownership."""

    name: str
    modules: list[str]
    directories: list[str]
    description: str = ""
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_mappings(
        cls,
        instance_name: str,
        module_map: dict[str, list[str]],
        directory_map: dict[str, list[str]],
        description: str = "",
    ) -> "InstanceInfo":
        """
        Create InstanceInfo from instance mappings.

        Args:
            instance_name: Name of the instance (e.g., "instance1")
            module_map: Dictionary mapping instances to modules
            directory_map: Dictionary mapping instances to directories
            description: Optional description of the instance

        Returns:
            InstanceInfo value object
        """
        modules = module_map.get(instance_name, [])
        directories = directory_map.get(instance_name, [])

        return cls(
            name=instance_name,
            modules=modules,
            directories=directories,
            description=description,
        )

    @property
    def primary_module(self) -> str | None:
        """Get the primary module name for this instance."""
        return self.modules[0] if self.modules else None

    def owns_path(self, path: str) -> bool:
        """Check if this instance owns the given path."""
        return any(path.startswith(directory) for directory in self.directories)

    def exists_on_filesystem(self) -> dict[str, bool]:
        """Check which directories exist on the filesystem."""
        return {directory: Path(directory).exists() for directory in self.directories}


@dataclass(frozen=True)
class SharedResource:
    """Value object representing shared resources that require coordination."""

    category: str
    paths: list[str]

    def contains_path(self, path: str) -> bool:
        """Check if the given path is in this shared resource."""
        return any(
            path.startswith(shared_path) or path == shared_path
            for shared_path in self.paths
        )


@dataclass(frozen=True)
class OwnershipInfo:
    """Value object representing file ownership information."""

    path: str
    owner: str | None
    is_shared: bool
    requires_coordination: bool

    @classmethod
    def for_path(
        cls,
        path: str,
        instances: list[InstanceInfo],
        shared_resources: list[SharedResource],
    ) -> "OwnershipInfo":
        """
        Determine ownership information for a path.

        Args:
            path: File path to check
            instances: List of all instances
            shared_resources: List of shared resources

        Returns:
            OwnershipInfo value object
        """
        # Check if path is shared
        for resource in shared_resources:
            if resource.contains_path(path):
                return cls(
                    path=path,
                    owner="shared",
                    is_shared=True,
                    requires_coordination=True,
                )

        # Check instance ownership
        for instance in instances:
            if instance.owns_path(path):
                return cls(
                    path=path,
                    owner=instance.name,
                    is_shared=False,
                    requires_coordination=False,
                )

        # No owner found
        return cls(
            path=path,
            owner=None,
            is_shared=False,
            requires_coordination=False,
        )
