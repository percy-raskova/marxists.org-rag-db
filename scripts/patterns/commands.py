"""Command pattern for encapsulating requests as objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandContext:
    """Context object for command execution with shared state and options."""

    options: dict[str, Any] = field(default_factory=dict)
    instances: list[Any] = field(default_factory=list)
    shared_resources: list[Any] = field(default_factory=list)
    module_map: dict[str, list[str]] = field(default_factory=dict)
    directory_map: dict[str, list[str]] = field(default_factory=dict)

    def get_option(self, key: str, default: Any = None) -> Any:
        """Get option value with default fallback."""
        return self.options.get(key, default)

    def set_option(self, key: str, value: Any) -> None:
        """Set option value."""
        self.options[key] = value


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution."""

    success: bool
    message: str
    data: Any = None
    exit_code: int = 0

    @classmethod
    def ok(cls, message: str = "", data: Any = None) -> "CommandResult":
        """Create successful result."""
        return cls(success=True, message=message, data=data, exit_code=0)

    @classmethod
    def error(cls, message: str, exit_code: int = 1) -> "CommandResult":
        """Create error result."""
        return cls(success=False, message=message, data=None, exit_code=exit_code)


class Command(ABC):
    """Abstract base class for commands."""

    @abstractmethod
    def execute(self, ctx: CommandContext) -> CommandResult:
        """
        Execute the command.

        Args:
            ctx: Command execution context

        Returns:
            CommandResult with execution outcome
        """

    def can_execute(self, ctx: CommandContext) -> bool:  # noqa: ARG002
        """
        Check if command can be executed with given context.

        Default implementation returns True. Override for validation.
        """
        return True

    def validate(self, ctx: CommandContext) -> CommandResult | None:
        """
        Validate command preconditions.

        Returns:
            None if valid, CommandResult with error if invalid
        """
        if not self.can_execute(ctx):
            return CommandResult.error("Command cannot be executed with given context")
        return None


class CompositeCommand(Command):
    """Command that executes multiple commands in sequence."""

    def __init__(self, *commands: Command):
        self.commands = list(commands)

    def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute all commands in sequence, stopping on first error."""
        results = []
        for command in self.commands:
            result = command.execute(ctx)
            results.append(result)
            if not result.success:
                return result
        return CommandResult.ok(
            message=f"Executed {len(self.commands)} commands successfully",
            data=results,
        )

    def add_command(self, command: Command) -> None:
        """Add a command to the sequence."""
        self.commands.append(command)


class CommandInvoker:
    """Invoker that manages and executes commands."""

    def __init__(self):
        self._commands: dict[str, Command] = {}
        self._history: list[tuple[str, CommandResult]] = []

    def register(self, name: str, command: Command) -> None:
        """Register a command with a name."""
        self._commands[name] = command

    def execute(self, name: str, ctx: CommandContext) -> CommandResult:
        """
        Execute a registered command by name.

        Args:
            name: Name of the command to execute
            ctx: Command execution context

        Returns:
            CommandResult from execution
        """
        command = self._commands.get(name)
        if not command:
            result = CommandResult.error(
                f"Unknown command: {name}. Available: {', '.join(self._commands.keys())}"
            )
            self._history.append((name, result))
            return result

        # Validate before executing
        validation_error = command.validate(ctx)
        if validation_error:
            self._history.append((name, validation_error))
            return validation_error

        # Execute
        result = command.execute(ctx)
        self._history.append((name, result))
        return result

    def has_command(self, name: str) -> bool:
        """Check if a command is registered."""
        return name in self._commands

    def list_commands(self) -> list[str]:
        """Get list of registered command names."""
        return list(self._commands.keys())

    def get_history(self) -> list[tuple[str, CommandResult]]:
        """Get command execution history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear command execution history."""
        self._history.clear()
