"""Concrete commands for instance operations."""

from pathlib import Path

from scripts.domain.instance import InstanceInfo, OwnershipInfo, SharedResource
from scripts.patterns.commands import Command, CommandContext, CommandInvoker, CommandResult


class CheckOwnershipCommand(Command):
    """Command to check ownership of a specific file."""

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Check and display file ownership."""
        filepath = ctx.get_option("filepath")
        if not filepath:
            return CommandResult.error("No file path provided")

        # Create ownership info
        ownership = OwnershipInfo.for_path(
            filepath,
            instances=ctx.instances,
            shared_resources=ctx.shared_resources,
        )

        # Format output
        if ownership.owner:
            message = f"Owner: {ownership.owner}"
            if ownership.requires_coordination:
                message += "\nRequires coordination: Yes"
        else:
            message = "Owner: none (unrestricted)"

        return CommandResult.ok(message=message, data=ownership)


class GetDirectoriesCommand(Command):
    """Command to get space-separated directories for an instance."""

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Get directories for instance as space-separated string."""
        instance_name = ctx.get_option("instance_name")
        if not instance_name:
            return CommandResult.error("No instance name provided")

        # Look up directories
        directories = ctx.directory_map.get(instance_name, [])

        if not directories:
            return CommandResult.error(
                f"Unknown instance {instance_name}",
                exit_code=1,
            )

        # Return space-separated for shell scripts
        message = " ".join(directories)
        return CommandResult.ok(message=message, data=directories)


class GetPathsCommand(Command):
    """Command to get newline-separated paths for an instance."""

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Get paths for instance as newline-separated string."""
        instance_name = ctx.get_option("instance_name")
        if not instance_name:
            return CommandResult.error("No instance name provided")

        # Look up directories
        directories = ctx.directory_map.get(instance_name, [])

        if not directories:
            return CommandResult.error(
                f"Unknown instance {instance_name}",
                exit_code=1,
            )

        # Return newline-separated
        message = "\n".join(directories)
        return CommandResult.ok(message=message, data=directories)


class ValidateMappingsCommand(Command):
    """Command to validate all instance ownership mappings."""

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Validate mappings for duplicates and filesystem existence."""
        all_valid = True
        all_paths: set[str] = set()
        output_lines = ["Validating instance ownership mappings..."]

        # Check each instance
        for instance in ctx.instances:
            output_lines.append(f"\n{instance.name}:")

            for directory in instance.directories:
                # Check for duplicates
                if directory in all_paths:
                    output_lines.append(f"  ❌ {directory} - DUPLICATE OWNERSHIP")
                    all_valid = False
                else:
                    all_paths.add(directory)

                    # Check filesystem existence
                    if Path(directory).exists():
                        output_lines.append(f"  ✅ {directory}")
                    else:
                        output_lines.append(f"  ⚠️  {directory} - does not exist yet")

        # Summary
        if all_valid:
            output_lines.append("\n✅ All mappings are valid")
            message = "\n".join(output_lines)
            return CommandResult.ok(message=message, data={"valid": True})
        else:
            output_lines.append("\n❌ Issues found in mappings")
            message = "\n".join(output_lines)
            return CommandResult.error(message=message, exit_code=1)


class ShowHelpCommand(Command):
    """Command to display help information."""

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Display help text."""
        help_text = ctx.get_option("help_text", "")
        return CommandResult.ok(message=help_text)


class InstanceCommandFactory:
    """Factory for creating instance commands with proper context."""

    @staticmethod
    def create_context(
        module_map: dict[str, list[str]],
        directory_map: dict[str, list[str]],
        shared_paths: dict[str, list[str]],
        **options,
    ) -> CommandContext:
        """
        Create a command context with instance mappings.

        Args:
            module_map: Instance to modules mapping
            directory_map: Instance to directories mapping
            shared_paths: Shared resource paths
            **options: Additional options to pass to context

        Returns:
            Configured CommandContext
        """
        # Create InstanceInfo objects
        instances = [
            InstanceInfo.from_mappings(name, module_map, directory_map)
            for name in module_map
        ]

        # Create SharedResource objects
        shared_resources = [
            SharedResource(category=category, paths=paths)
            for category, paths in shared_paths.items()
        ]

        return CommandContext(
            options=options,
            instances=instances,
            shared_resources=shared_resources,
            module_map=module_map,
            directory_map=directory_map,
        )

    @staticmethod
    def create_command_invoker() -> CommandInvoker:
        """
        Create and configure a command invoker with all instance commands.

        Returns:
            Configured CommandInvoker with registered commands
        """
        invoker = CommandInvoker()
        invoker.register("check_ownership", CheckOwnershipCommand())
        invoker.register("get_directories", GetDirectoriesCommand())
        invoker.register("get_paths", GetPathsCommand())
        invoker.register("validate_mappings", ValidateMappingsCommand())
        invoker.register("show_help", ShowHelpCommand())

        return invoker
