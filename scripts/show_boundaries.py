#!/usr/bin/env python3
"""
Display instance boundaries and ownership information.

This script provides a clear view of which files and modules
each instance owns and can modify.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import sys
from pathlib import Path
from typing import ClassVar


class BoundaryViewer:
    """View and explore instance boundaries."""

    # Instance information with emojis for visual distinction
    INSTANCE_INFO: ClassVar[dict[str, dict]] = {
        "instance1": {
            "name": "Storage & Pipeline",
            "emoji": "💾",
            "color": "\033[94m",  # Blue
            "description": "Handles GCS storage, data pipeline orchestration, and file management",
            "tech_stack": ["Google Cloud Storage", "Apache Beam", "Airflow", "Pandas"],
            "responsibilities": [
                "Download and store raw MIA archive files",
                "Process HTML/PDF to clean markdown",
                "Manage data pipeline workflows",
                "Handle batch processing jobs",
                "Implement data versioning",
            ],
        },
        "instance2": {
            "name": "Embeddings",
            "emoji": "🧮",
            "color": "\033[92m",  # Green
            "description": "Generates embeddings using GPU resources on Runpod",
            "tech_stack": ["Runpod", "Sentence Transformers", "PyTorch", "Accelerate"],
            "responsibilities": [
                "Generate document embeddings",
                "Manage GPU resource allocation",
                "Implement batch processing for efficiency",
                "Handle checkpoint/resume for long jobs",
                "Optimize embedding models",
            ],
        },
        "instance3": {
            "name": "Weaviate",
            "emoji": "🔍",
            "color": "\033[93m",  # Yellow
            "description": "Manages Weaviate vector database for billion-scale search",
            "tech_stack": ["Weaviate", "Kubernetes", "GraphQL"],
            "responsibilities": [
                "Store and index vector embeddings",
                "Implement semantic search",
                "Manage Weaviate schema",
                "Handle backup and recovery",
                "Optimize query performance",
            ],
        },
        "instance4": {
            "name": "API",
            "emoji": "🌐",
            "color": "\033[95m",  # Magenta
            "description": "Provides REST API for querying the RAG system",
            "tech_stack": ["FastAPI", "Redis", "Pydantic", "Uvicorn"],
            "responsibilities": [
                "Expose search endpoints",
                "Implement caching layer",
                "Handle rate limiting",
                "Manage authentication",
                "Provide API documentation",
            ],
        },
        "instance5": {
            "name": "MCP",
            "emoji": "🤖",
            "color": "\033[96m",  # Cyan
            "description": "Model Context Protocol server for AI tool integration",
            "tech_stack": ["MCP", "JSON-RPC", "WebSocket"],
            "responsibilities": [
                "Expose RAG tools via MCP",
                "Handle tool invocation",
                "Manage streaming responses",
                "Implement context management",
                "Provide tool discovery",
            ],
        },
        "instance6": {
            "name": "Monitoring",
            "emoji": "📊",
            "color": "\033[91m",  # Red
            "description": "Observability stack for system monitoring",
            "tech_stack": ["Prometheus", "Grafana", "AlertManager"],
            "responsibilities": [
                "Collect system metrics",
                "Create monitoring dashboards",
                "Implement alerting rules",
                "Track performance KPIs",
                "Generate cost reports",
            ],
        },
    }

    # Detailed file ownership
    FILE_OWNERSHIP: ClassVar[dict[str, dict]] = {
        "instance1": {
            "src": ["src/mia_rag/storage/", "src/mia_rag/pipeline/"],
            "tests": ["tests/unit/instance1_storage/", "tests/integration/storage_pipeline/"],
            "docs": ["docs/instance1-storage.md", "docs/architecture/storage.md"],
            "configs": ["configs/gcs.yaml", "configs/pipeline.yaml"],
        },
        "instance2": {
            "src": ["src/mia_rag/embeddings/"],
            "tests": ["tests/unit/instance2_embeddings/", "tests/integration/embeddings/"],
            "docs": ["docs/instance2-embeddings.md", "docs/architecture/embeddings.md"],
            "configs": ["configs/runpod.yaml", "configs/models.yaml"],
        },
        "instance3": {
            "src": ["src/mia_rag/weaviate/"],
            "tests": ["tests/unit/instance3_weaviate/", "tests/integration/weaviate/"],
            "docs": ["docs/instance3-weaviate.md", "docs/architecture/weaviate.md"],
            "configs": ["configs/weaviate.yaml", "configs/schema.json"],
        },
        "instance4": {
            "src": ["src/mia_rag/api/"],
            "tests": ["tests/unit/instance4_api/", "tests/integration/api/"],
            "docs": ["docs/instance4-api.md", "docs/api-reference.md"],
            "configs": ["configs/api.yaml", "configs/redis.yaml"],
        },
        "instance5": {
            "src": ["src/mia_rag/mcp/"],
            "tests": ["tests/unit/instance5_mcp/", "tests/integration/mcp/"],
            "docs": ["docs/instance5-mcp.md", "docs/mcp-tools.md"],
            "configs": ["configs/mcp.yaml"],
        },
        "instance6": {
            "src": ["src/mia_rag/monitoring/"],
            "tests": ["tests/unit/instance6_monitoring/", "tests/integration/monitoring/"],
            "docs": ["docs/instance6-monitoring.md", "docs/dashboards.md"],
            "configs": ["configs/prometheus.yaml", "configs/grafana.json", "configs/alerts.yaml"],
        },
    }

    # Interface contracts
    INTERFACES: ClassVar[dict[str, dict]] = {
        "storage_embeddings": {
            "from": "instance1",
            "to": "instance2",
            "interface": "src/mia_rag/interfaces/document_processor.py",
            "methods": ["process_document", "batch_process"],
            "data_format": "ProcessedDocument",
        },
        "embeddings_weaviate": {
            "from": "instance2",
            "to": "instance3",
            "interface": "src/mia_rag/interfaces/embedding_store.py",
            "methods": ["store_embeddings", "batch_store"],
            "data_format": "EmbeddingBatch",
        },
        "weaviate_api": {
            "from": "instance3",
            "to": "instance4",
            "interface": "src/mia_rag/interfaces/vector_search.py",
            "methods": ["search", "hybrid_search"],
            "data_format": "SearchResult",
        },
        "weaviate_mcp": {
            "from": "instance3",
            "to": "instance5",
            "interface": "src/mia_rag/interfaces/vector_search.py",
            "methods": ["search", "get_by_id"],
            "data_format": "SearchResult",
        },
        "all_monitoring": {
            "from": "*",
            "to": "instance6",
            "interface": "src/mia_rag/interfaces/metrics.py",
            "methods": ["record_metric", "get_metrics"],
            "data_format": "MetricData",
        },
    }

    def __init__(self):
        """Initialize boundary viewer."""
        self.reset_color = "\033[0m"

    def show_instance_details(self, instance: str):
        """Show detailed information for a specific instance."""
        info = self.INSTANCE_INFO.get(instance)
        if not info:
            print(f"❌ Unknown instance: {instance}")
            return

        color = info["color"]
        print(f"\n{color}{'='*60}{self.reset_color}")
        print(f"{info['emoji']} {color}{instance.upper()}: {info['name']}{self.reset_color}")
        print(f"{color}{'='*60}{self.reset_color}")

        print("\n📝 Description:")
        print(f"  {info['description']}")

        print("\n🛠️  Tech Stack:")
        for tech in info["tech_stack"]:
            print(f"  • {tech}")

        print("\n📋 Responsibilities:")
        for resp in info["responsibilities"]:
            print(f"  • {resp}")

        # Show file ownership
        ownership = self.FILE_OWNERSHIP.get(instance, {})
        if ownership:
            print("\n📁 File Ownership:")
            for category, paths in ownership.items():
                print(f"\n  {category.upper()}:")
                for path in paths:
                    exists = "✅" if Path(path).exists() else "⚠️"
                    print(f"    {exists} {path}")

        # Show interfaces
        print("\n🔗 Interfaces:")
        for interface in self.INTERFACES.values():
            if interface["from"] == instance:
                print(f"  → {interface['to']}: {interface['interface']}")
            elif interface["to"] == instance:
                print(f"  ← {interface['from']}: {interface['interface']}")

    def show_all_boundaries(self):
        """Show overview of all instance boundaries."""
        print("\n" + "=" * 80)
        print("🗺️  INSTANCE BOUNDARIES OVERVIEW")
        print("=" * 80)

        for instance, info in self.INSTANCE_INFO.items():
            color = info["color"]
            print(f"\n{info['emoji']} {color}{instance}: {info['name']}{self.reset_color}")
            print(f"  {info['description']}")

            ownership = self.FILE_OWNERSHIP.get(instance, {})
            src_count = len(ownership.get("src", []))
            test_count = len(ownership.get("tests", []))
            print(f"  📁 Owns: {src_count} source dirs, {test_count} test dirs")

        print("\n" + "=" * 80)

    def show_interfaces(self):
        """Show all interface contracts between instances."""
        print("\n" + "=" * 60)
        print("🔗 INTERFACE CONTRACTS")
        print("=" * 60)

        for interface in self.INTERFACES.values():
            from_info = self.INSTANCE_INFO.get(interface["from"], {"emoji": "🌍", "name": "All"})
            to_info = self.INSTANCE_INFO.get(interface["to"], {"emoji": "❓", "name": "Unknown"})

            print(
                f"\n{from_info['emoji']} {interface['from']} → {to_info['emoji']} {interface['to']}"
            )
            print(f"  Interface: {interface['interface']}")
            print(f"  Format: {interface['data_format']}")
            print(f"  Methods: {', '.join(interface['methods'])}")

    def check_current_instance(self):
        """Check and display current instance setting."""
        instance_file = Path(".instance")

        if instance_file.exists():
            current = instance_file.read_text().strip()
            info = self.INSTANCE_INFO.get(current)
            if info:
                print(f"\n🤖 Current Instance: {info['emoji']} {current} - {info['name']}")
                return current
            else:
                print(f"\n⚠️  Unknown instance in .instance file: {current}")
        else:
            print("\n⚠️  No instance set. Run 'mise run identify' to set your instance.")

        return None

    def export_boundaries_json(self, output_file: Path):
        """Export boundaries to JSON for tooling integration."""
        data = {
            "instances": self.INSTANCE_INFO,
            "ownership": self.FILE_OWNERSHIP,
            "interfaces": self.INTERFACES,
        }

        output_file.write_text(json.dumps(data, indent=2))
        print(f"📄 Boundaries exported to {output_file}")


def main():
    """Main entry point for boundary viewer."""
    parser = argparse.ArgumentParser(description="Display instance boundaries and ownership")
    parser.add_argument(
        "--instance",
        help="Show details for specific instance",
        choices=[f"instance{i}" for i in range(1, 7)],
    )
    parser.add_argument("--interfaces", action="store_true", help="Show interface contracts")
    parser.add_argument("--current", action="store_true", help="Show current instance details")
    parser.add_argument("--export", help="Export boundaries to JSON file", type=Path)

    args = parser.parse_args()

    viewer = BoundaryViewer()

    if args.export:
        viewer.export_boundaries_json(args.export)
    elif args.current:
        current = viewer.check_current_instance()
        if current:
            viewer.show_instance_details(current)
    elif args.instance:
        viewer.show_instance_details(args.instance)
    elif args.interfaces:
        viewer.show_interfaces()
    else:
        # Default: show overview
        viewer.show_all_boundaries()
        viewer.check_current_instance()
        print("\n💡 Tips:")
        print("  • Use --instance <name> to see details for a specific instance")
        print("  • Use --interfaces to see all interface contracts")
        print("  • Use --current to see details for your current instance")

    return 0


if __name__ == "__main__":
    sys.exit(main())
