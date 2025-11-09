#!/usr/bin/env python3
"""
Example RAG Query Script

Test your Marxist theory RAG system with various query types.

Usage:
    python query_example.py --db chroma --query "What is surplus value?"
    python query_example.py --db qdrant --interactive
"""

import argparse
import sys
from pathlib import Path


try:
    import requests
except ImportError:
    print("Install requests: pip install requests --break-system-packages")
    sys.exit(1)


class RAGQuery:
    """Query interface for MIA RAG system"""

    def __init__(self, db_type: str, persist_dir: Path, embedding_model: str = "nomic-embed-text"):
        self.db_type = db_type
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model
        self.db = None

        self.setup_db()

    def setup_db(self):
        """Initialize database connection"""
        if self.db_type == "chroma":
            try:
                import chromadb
                from chromadb.config import Settings
            except ImportError:
                print("Install ChromaDB: pip install chromadb --break-system-packages")
                sys.exit(1)

            self.client = chromadb.Client(
                Settings(persist_directory=str(self.persist_dir), anonymized_telemetry=False)
            )

            try:
                self.db = self.client.get_collection("marxist_theory")
                print(f"✓ Connected to ChromaDB at {self.persist_dir}")
                print(f"  Collection size: {self.db.count()} chunks")
            except Exception as e:
                print(f"Error loading collection: {e}")
                sys.exit(1)

        elif self.db_type == "qdrant":
            try:
                from qdrant_client import QdrantClient
            except ImportError:
                print("Install Qdrant: pip install qdrant-client --break-system-packages")
                sys.exit(1)

            self.db = QdrantClient(path=str(self.persist_dir))
            print(f"✓ Connected to Qdrant at {self.persist_dir}")

            try:
                info = self.db.get_collection("marxist_theory")
                print(f"  Collection size: {info.points_count} chunks")
            except Exception as e:
                print(f"Error loading collection: {e}")
                sys.exit(1)

    def get_embedding(self, text: str) -> list:
        """Get embedding from Ollama"""
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.ConnectionError:
            print("\n❌ Cannot connect to Ollama. Make sure it's running:")
            print("   ollama serve")
            sys.exit(1)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def query_chroma(self, query: str, n_results: int = 5):
        """Query ChromaDB"""
        results = self.db.query(query_texts=[query], n_results=n_results)

        return [
            {"content": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                strict=False,
            )
        ]

    def query_qdrant(self, query: str, n_results: int = 5):
        """Query Qdrant"""
        embedding = self.get_embedding(query)
        if not embedding:
            return []

        results = self.db.search(
            collection_name="marxist_theory", query_vector=embedding, limit=n_results
        )

        return [
            {
                "content": result.payload["content"],
                "metadata": {k: v for k, v in result.payload.items() if k != "content"},
                "score": result.score,
            }
            for result in results
        ]

    def query(self, query_text: str, n_results: int = 5):
        """Query the RAG system"""
        print(f"\n🔍 Querying: {query_text}")
        print("=" * 80)

        if self.db_type == "chroma":
            results = self.query_chroma(query_text, n_results)
        else:
            results = self.query_qdrant(query_text, n_results)

        if not results:
            print("No results found.")
            return

        for i, result in enumerate(results, 1):
            meta = result["metadata"]
            content = result["content"]

            print(f"\n📄 Result {i}")
            print(f"   Title: {meta.get('title', 'Unknown')}")
            print(f"   Author: {meta.get('author', 'Unknown')}")
            print(f"   Date: {meta.get('date', 'Unknown')}")
            print(f"   Source: {meta.get('source_url', 'Unknown')}")

            if self.db_type == "chroma":
                print(f"   Distance: {result['distance']:.4f}")
            else:
                print(f"   Score: {result['score']:.4f}")

            print(f"\n   {content[:400]}...")
            print("-" * 80)

    def interactive_mode(self):
        """Interactive query mode"""
        print("\n" + "=" * 80)
        print("MARXIST THEORY RAG - INTERACTIVE MODE")
        print("=" * 80)
        print("\nCommands:")
        print("  Type your query and press Enter")
        print("  'exit' or 'quit' to exit")
        print("  'examples' to see example queries")
        print("=" * 80 + "\n")

        while True:
            try:
                query = input("Query> ").strip()

                if not query:
                    continue

                if query.lower() in ["exit", "quit", "q"]:
                    print("✌️ Solidarity forever")
                    break

                if query.lower() == "examples":
                    self.show_examples()
                    continue

                self.query(query)

            except KeyboardInterrupt:
                print("\n✌️ Solidarity forever")
                break
            except Exception as e:
                print(f"Error: {e}")

    def show_examples(self):
        """Show example queries"""
        examples = [
            "What is the theory of surplus value?",
            "How did Lenin organize the vanguard party?",
            "What is the role of the lumpenproletariat?",
            "Explain dialectical materialism",
            "What were the Paris Commune's organizational structures?",
            "How do wages relate to labor power?",
            "What is imperialism as highest stage of capitalism?",
            "Describe the withering away of the state",
            "What is the dictatorship of the proletariat?",
            "How does primitive accumulation work?",
        ]

        print("\n📚 Example Queries:")
        for i, ex in enumerate(examples, 1):
            print(f"   {i}. {ex}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Query the Marxist Theory RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  python query_example.py --db chroma --query "What is surplus value?"

  # Interactive mode
  python query_example.py --db chroma --interactive

  # More results
  python query_example.py --db chroma --query "organizing tactics" --results 10
        """,
    )

    parser.add_argument(
        "--db",
        choices=["chroma", "qdrant"],
        default="chroma",
        help="Vector database type (default: chroma)",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Path("./mia_vectordb/"),
        help="Vector DB directory (default: ./mia_vectordb/)",
    )
    parser.add_argument("--query", type=str, help="Query string")
    parser.add_argument("--results", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--interactive", action="store_true", help="Interactive query mode")
    parser.add_argument(
        "--embedding-model",
        default="nomic-embed-text",
        help="Ollama embedding model (default: nomic-embed-text)",
    )

    args = parser.parse_args()

    if not args.persist_dir.exists():
        print(f"Error: Vector DB directory does not exist: {args.persist_dir}")
        print("Have you run rag_ingest.py yet?")
        return 1

    # Initialize query interface
    rag = RAGQuery(
        db_type=args.db, persist_dir=args.persist_dir, embedding_model=args.embedding_model
    )

    if args.interactive:
        rag.interactive_mode()
    elif args.query:
        rag.query(args.query, args.results)
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for easier exploration")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
