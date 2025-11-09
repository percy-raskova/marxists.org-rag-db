"""Unit tests for instance commands."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path so we can import like the scripts do
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from domain.instance import InstanceInfo, OwnershipInfo, SharedResource
from patterns.commands import CommandContext, CommandResult
from patterns.instance_commands import (
    CheckOwnershipCommand,
    GetDirectoriesCommand,
    GetPathsCommand,
    InstanceCommandFactory,
    ShowHelpCommand,
    ValidateMappingsCommand,
)


@pytest.fixture
def module_map():
    """Sample module mapping."""
    return {
        "instance1": ["storage", "pipeline"],
        "instance2": ["embeddings"],
        "instance3": ["vectordb"],
    }


@pytest.fixture
def directory_map():
    """Sample directory mapping."""
    return {
        "instance1": ["src/storage", "tests/unit/storage"],
        "instance2": ["src/embeddings", "tests/unit/embeddings"],
        "instance3": ["src/vectordb"],
    }


@pytest.fixture
def shared_paths():
    """Sample shared resource paths."""
    return {
        "interfaces": ["src/interfaces", "src/common"],
        "configuration": ["pyproject.toml", ".gitignore"],
    }


@pytest.fixture
def instances(module_map, directory_map):
    """Create sample instances."""
    return [
        InstanceInfo.from_mappings("instance1", module_map, directory_map),
        InstanceInfo.from_mappings("instance2", module_map, directory_map),
        InstanceInfo.from_mappings("instance3", module_map, directory_map),
    ]


@pytest.fixture
def shared_resources(shared_paths):
    """Create sample shared resources."""
    return [
        SharedResource(category=cat, paths=paths)
        for cat, paths in shared_paths.items()
    ]


@pytest.fixture
def command_context(module_map, directory_map, instances, shared_resources):
    """Create a command context for testing."""
    return CommandContext(
        instances=instances,
        shared_resources=shared_resources,
        module_map=module_map,
        directory_map=directory_map,
    )


class TestInstanceInfo:
    """Test InstanceInfo domain model."""

    def test_from_mappings(self, module_map, directory_map):
        """Test creating InstanceInfo from mappings."""
        info = InstanceInfo.from_mappings("instance1", module_map, directory_map)

        assert info.name == "instance1"
        assert info.modules == ["storage", "pipeline"]
        assert info.directories == ["src/storage", "tests/unit/storage"]

    def test_primary_module(self, instances):
        """Test primary_module property."""
        assert instances[0].primary_module == "storage"
        assert instances[1].primary_module == "embeddings"

    def test_owns_path(self, instances):
        """Test owns_path method."""
        assert instances[0].owns_path("src/storage/file.py")
        assert instances[0].owns_path("tests/unit/storage/test_foo.py")
        assert not instances[0].owns_path("src/embeddings/file.py")

    def test_exists_on_filesystem(self, instances, tmp_path):
        """Test exists_on_filesystem method."""
        # Create a test instance with paths we can control
        test_dir = str(tmp_path / "test_dir")
        Path(test_dir).mkdir()

        test_instance = InstanceInfo(
            name="test",
            modules=["test"],
            directories=[test_dir, str(tmp_path / "nonexistent")],
        )

        existence = test_instance.exists_on_filesystem()
        assert existence[test_dir] is True
        assert existence[str(tmp_path / "nonexistent")] is False


class TestSharedResource:
    """Test SharedResource domain model."""

    def test_contains_path(self, shared_resources):
        """Test contains_path method."""
        interfaces_resource = shared_resources[0]

        assert interfaces_resource.contains_path("src/interfaces/base.py")
        assert interfaces_resource.contains_path("src/common/utils.py")
        assert not interfaces_resource.contains_path("src/storage/file.py")


class TestOwnershipInfo:
    """Test OwnershipInfo domain model."""

    def test_for_instance_owned_path(self, instances, shared_resources):
        """Test ownership determination for instance-owned path."""
        ownership = OwnershipInfo.for_path(
            "src/storage/file.py",
            instances,
            shared_resources,
        )

        assert ownership.owner == "instance1"
        assert not ownership.is_shared
        assert not ownership.requires_coordination

    def test_for_shared_path(self, instances, shared_resources):
        """Test ownership determination for shared path."""
        ownership = OwnershipInfo.for_path(
            "src/interfaces/base.py",
            instances,
            shared_resources,
        )

        assert ownership.owner == "shared"
        assert ownership.is_shared
        assert ownership.requires_coordination

    def test_for_unowned_path(self, instances, shared_resources):
        """Test ownership determination for unowned path."""
        ownership = OwnershipInfo.for_path(
            "random/file.py",
            instances,
            shared_resources,
        )

        assert ownership.owner is None
        assert not ownership.is_shared
        assert not ownership.requires_coordination


class TestCheckOwnershipCommand:
    """Test CheckOwnershipCommand."""

    def test_check_instance_owned_file(self, command_context):
        """Test checking ownership of instance-owned file."""
        command_context.set_option("filepath", "src/storage/file.py")
        cmd = CheckOwnershipCommand()

        result = cmd.execute(command_context)

        assert result.success
        assert "instance1" in result.message
        assert isinstance(result.data, OwnershipInfo)

    def test_check_shared_file(self, command_context):
        """Test checking ownership of shared file."""
        command_context.set_option("filepath", "src/interfaces/base.py")
        cmd = CheckOwnershipCommand()

        result = cmd.execute(command_context)

        assert result.success
        assert "shared" in result.message
        assert "coordination" in result.message.lower()

    def test_check_without_filepath(self, command_context):
        """Test command without filepath option."""
        cmd = CheckOwnershipCommand()

        result = cmd.execute(command_context)

        assert not result.success
        assert "No file path" in result.message


class TestGetDirectoriesCommand:
    """Test GetDirectoriesCommand."""

    def test_get_directories_success(self, command_context):
        """Test getting directories for valid instance."""
        command_context.set_option("instance_name", "instance1")
        cmd = GetDirectoriesCommand()

        result = cmd.execute(command_context)

        assert result.success
        assert "src/storage" in result.message
        assert "tests/unit/storage" in result.message
        # Should be space-separated
        assert " " in result.message

    def test_get_directories_unknown_instance(self, command_context):
        """Test getting directories for unknown instance."""
        command_context.set_option("instance_name", "unknown")
        cmd = GetDirectoriesCommand()

        result = cmd.execute(command_context)

        assert not result.success
        assert "Unknown instance" in result.message
        assert result.exit_code == 1

    def test_get_directories_without_name(self, command_context):
        """Test command without instance name."""
        cmd = GetDirectoriesCommand()

        result = cmd.execute(command_context)

        assert not result.success
        assert "No instance name" in result.message


class TestGetPathsCommand:
    """Test GetPathsCommand."""

    def test_get_paths_success(self, command_context):
        """Test getting paths for valid instance."""
        command_context.set_option("instance_name", "instance1")
        cmd = GetPathsCommand()

        result = cmd.execute(command_context)

        assert result.success
        assert "src/storage" in result.message
        assert "tests/unit/storage" in result.message
        # Should be newline-separated
        assert "\n" in result.message

    def test_get_paths_unknown_instance(self, command_context):
        """Test getting paths for unknown instance."""
        command_context.set_option("instance_name", "unknown")
        cmd = GetPathsCommand()

        result = cmd.execute(command_context)

        assert not result.success
        assert result.exit_code == 1


class TestValidateMappingsCommand:
    """Test ValidateMappingsCommand."""

    def test_validate_success(self, command_context):
        """Test validation with valid mappings."""
        cmd = ValidateMappingsCommand()

        result = cmd.execute(command_context)

        # May succeed or have warnings about non-existent paths
        # Just verify it runs and produces output
        assert result.message
        assert "Validating" in result.message

    def test_validate_duplicate_paths(self):
        """Test validation detects duplicate ownership."""
        # Create instances with duplicate paths
        module_map = {"instance1": ["mod1"], "instance2": ["mod2"]}
        directory_map = {
            "instance1": ["src/shared"],  # Duplicate
            "instance2": ["src/shared"],  # Duplicate
        }

        instances = [
            InstanceInfo.from_mappings("instance1", module_map, directory_map),
            InstanceInfo.from_mappings("instance2", module_map, directory_map),
        ]

        ctx = CommandContext(
            instances=instances,
            module_map=module_map,
            directory_map=directory_map,
        )

        cmd = ValidateMappingsCommand()
        result = cmd.execute(ctx)

        assert not result.success
        assert "DUPLICATE" in result.message
        assert result.exit_code == 1


class TestShowHelpCommand:
    """Test ShowHelpCommand."""

    def test_show_help(self, command_context):
        """Test showing help text."""
        help_text = "Usage: instance_map [OPTIONS]"
        command_context.set_option("help_text", help_text)

        cmd = ShowHelpCommand()
        result = cmd.execute(command_context)

        assert result.success
        assert help_text in result.message


class TestInstanceCommandFactory:
    """Test InstanceCommandFactory."""

    def test_create_context(self, module_map, directory_map, shared_paths):
        """Test creating command context."""
        ctx = InstanceCommandFactory.create_context(
            module_map,
            directory_map,
            shared_paths,
            test_option="test_value",
        )

        assert len(ctx.instances) == 3
        assert len(ctx.shared_resources) == 2
        assert ctx.get_option("test_option") == "test_value"

    def test_create_command_invoker(self):
        """Test creating command invoker."""
        invoker = InstanceCommandFactory.create_command_invoker()

        # Verify all commands are registered
        assert invoker.has_command("check_ownership")
        assert invoker.has_command("get_directories")
        assert invoker.has_command("get_paths")
        assert invoker.has_command("validate_mappings")
        assert invoker.has_command("show_help")

        # Verify we have 5 commands
        assert len(invoker.list_commands()) == 5


class TestCommandResult:
    """Test CommandResult value object."""

    def test_ok_result(self):
        """Test creating successful result."""
        result = CommandResult.ok("Success!", data={"key": "value"})

        assert result.success
        assert result.message == "Success!"
        assert result.data == {"key": "value"}
        assert result.exit_code == 0

    def test_error_result(self):
        """Test creating error result."""
        result = CommandResult.error("Error occurred", exit_code=2)

        assert not result.success
        assert result.message == "Error occurred"
        assert result.data is None
        assert result.exit_code == 2
