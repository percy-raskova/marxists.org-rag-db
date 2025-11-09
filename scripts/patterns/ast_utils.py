"""AST-based utilities for parsing Python import statements.

This module provides tools to parse Python files using AST instead of string manipulation,
extracting structured import information for validation.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportStatement:
    """Represents a structured import statement from Python code.

    Attributes:
        module: The module being imported (e.g., 'src.mia_rag.storage')
        names: List of names imported from the module (e.g., ['StorageAdapter'])
        level: Relative import level (0 for absolute, >0 for relative)
        source_file: Path to the file containing this import
        line_number: Line number where the import appears
        is_from_import: True if this is a 'from X import Y' statement
    """
    module: str
    names: list[str]
    level: int
    source_file: Path
    line_number: int
    is_from_import: bool

    @property
    def module_path(self) -> str:
        """Convert module name to file path format (dots to slashes).

        Returns:
            Module path with slashes, ending with '/' (e.g., 'src/mia_rag/storage/')
        """
        if not self.module:
            return ""
        return self.module.replace(".", "/") + "/"


class ImportExtractor(ast.NodeVisitor):
    """AST visitor that extracts import statements from Python code."""

    def __init__(self, source_file: Path):
        """Initialize the import extractor.

        Args:
            source_file: Path to the source file being parsed
        """
        self.source_file = source_file
        self.imports: list[ImportStatement] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Visit a simple import statement (import X).

        Args:
            node: AST Import node
        """
        for alias in node.names:
            self.imports.append(
                ImportStatement(
                    module=alias.name,
                    names=[alias.asname] if alias.asname else [alias.name],
                    level=0,
                    source_file=self.source_file,
                    line_number=node.lineno,
                    is_from_import=False,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit a from-import statement (from X import Y).

        Args:
            node: AST ImportFrom node
        """
        module = node.module or ""
        names = [alias.name for alias in node.names]

        self.imports.append(
            ImportStatement(
                module=module,
                names=names,
                level=node.level,
                source_file=self.source_file,
                line_number=node.lineno,
                is_from_import=True,
            )
        )
        self.generic_visit(node)


def extract_imports(file_path: Path) -> list[ImportStatement]:
    """Extract all import statements from a Python file using AST.

    Args:
        file_path: Path to the Python file to parse

    Returns:
        List of ImportStatement objects found in the file

    Raises:
        SyntaxError: If the file contains invalid Python syntax
        FileNotFoundError: If the file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix != ".py":
        return []

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        extractor = ImportExtractor(file_path)
        extractor.visit(tree)

        return extractor.imports
    except SyntaxError as e:
        # Re-raise with more context
        raise SyntaxError(f"Failed to parse {file_path}: {e}") from e
