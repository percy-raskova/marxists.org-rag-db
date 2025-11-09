"""
Repository pattern for interface contract access.

This module implements the Repository pattern to encapsulate
the data access logic for loading and querying interface contracts.
"""

import ast
from pathlib import Path
from typing import Optional

from scripts.domain.interfaces import InterfaceDefinition


class InterfaceRepository:
    """Repository for loading and querying interface definitions.

    This class encapsulates the logic for parsing interface contract
    definitions from Python source files and providing a clean API
    for querying interface specifications.

    The repository pattern isolates data access concerns from
    business logic, making the code more testable and maintainable.
    """

    def __init__(self, contracts_path: Path | None = None):
        """Initialize the repository.

        Args:
            contracts_path: Path to the contracts file. If None, uses default
                           location: PROJECT_ROOT/src/mia_rag/interfaces/contracts.py
        """
        if contracts_path is None:
            # Default to standard contracts location
            project_root = Path(__file__).parent.parent.parent
            contracts_path = project_root / "src" / "mia_rag" / "interfaces" / "contracts.py"

        self.contracts_path = contracts_path
        self._contracts: dict[str, InterfaceDefinition] = {}
        self._loaded = False

    def load(self) -> None:
        """Load interface definitions from the contracts file.

        This method parses the contracts file and extracts all interface
        definitions. It's called lazily on first access.

        Raises:
            FileNotFoundError: If contracts file doesn't exist
            SyntaxError: If contracts file has invalid Python syntax
        """
        if not self.contracts_path.exists():
            # Contracts might not exist yet in early development
            self._contracts = {}
            self._loaded = True
            return

        try:
            with open(self.contracts_path) as f:
                tree = ast.parse(f.read(), filename=str(self.contracts_path))

            checker = _InterfaceExtractor()
            checker.visit(tree)

            self._contracts = {
                name: InterfaceDefinition(
                    name=name,
                    methods=definition["methods"],
                    properties=definition.get("properties", []),
                    class_methods=definition.get("class_methods", []),
                    file_path=self.contracts_path,
                )
                for name, definition in checker.interfaces.items()
            }
            self._loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load contracts from {self.contracts_path}: {e}")

    def _ensure_loaded(self) -> None:
        """Ensure contracts are loaded before access."""
        if not self._loaded:
            self.load()

    def get_interface(self, name: str) -> Optional[InterfaceDefinition]:
        """Get an interface definition by name.

        Args:
            name: Interface name

        Returns:
            InterfaceDefinition if found, None otherwise
        """
        self._ensure_loaded()
        return self._contracts.get(name)

    def get_all_interfaces(self) -> dict[str, InterfaceDefinition]:
        """Get all interface definitions.

        Returns:
            Dictionary mapping interface names to definitions
        """
        self._ensure_loaded()
        return self._contracts.copy()

    def get_required_methods(self, interface_name: str) -> set[str]:
        """Get required method names for an interface.

        Args:
            interface_name: Name of the interface

        Returns:
            Set of method names (without signatures)

        Raises:
            KeyError: If interface not found
        """
        self._ensure_loaded()
        if interface_name not in self._contracts:
            raise KeyError(f"Interface '{interface_name}' not found")

        return self._contracts[interface_name].get_all_method_names()

    def has_interface(self, name: str) -> bool:
        """Check if an interface exists.

        Args:
            name: Interface name

        Returns:
            True if interface exists, False otherwise
        """
        self._ensure_loaded()
        return name in self._contracts


class _InterfaceExtractor(ast.NodeVisitor):
    """Internal AST visitor to extract interface definitions from contracts.

    This class is private to the repository and handles the low-level
    details of parsing Python AST to find ABC interface definitions.
    """

    def __init__(self):
        """Initialize the extractor."""
        self.interfaces: dict[str, dict[str, list[str]]] = {}
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to find ABC interfaces.

        Args:
            node: AST ClassDef node
        """
        # Check if it's an ABC
        is_abc = any(
            (isinstance(base, ast.Name) and base.id == "ABC")
            or (isinstance(base, ast.Attribute) and base.attr == "ABC")
            for base in node.bases
        )

        if is_abc:
            self.current_class = node.name
            self.interfaces[node.name] = {
                "methods": [],
                "properties": [],
                "class_methods": [],
            }

        # Visit nested nodes
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract interface methods.

        Args:
            node: AST FunctionDef node
        """
        if self.current_class:
            # Check if it's abstract
            is_abstract = any(
                isinstance(dec, ast.Name) and dec.id == "abstractmethod"
                for dec in node.decorator_list
            )

            if is_abstract:
                # Get method signature
                args = [arg.arg for arg in node.args.args if arg.arg != "self"]
                method_sig = f"{node.name}({', '.join(args)})"
                self.interfaces[self.current_class]["methods"].append(method_sig)

        self.generic_visit(node)
