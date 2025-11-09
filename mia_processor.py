#!/usr/bin/env python3
"""
Marxists Internet Archive (MIA) Processing Pipeline
Converts HTML/PDF to Markdown with metadata preservation for RAG ingestion

Usage:
    python mia_processor.py --download-json    # Fetch MIA metadata
    python mia_processor.py --process-archive /path/to/dump_www-marxists-org/
"""

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


try:
    import pymupdf4llm
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
except ImportError as e:
    print(f"Missing dependency: {e}")
    print(
        "Install with: pip install requests beautifulsoup4 markdownify pymupdf4llm --break-system-packages"
    )
    exit(1)


@dataclass
class DocumentMetadata:
    """Metadata for each processed document"""

    source_url: str
    title: str
    author: str | None = None
    date: str | None = None
    language: str = "en"
    doc_type: str = "html"  # html, pdf
    original_path: str = ""
    processed_date: str = ""
    content_hash: str = ""
    word_count: int = 0


class MIAProcessor:
    """Process MIA archive into RAG-ready markdown"""

    def __init__(self, output_dir: Path = Path("~/marxists-processed").expanduser()):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_dir = self.output_dir / "metadata"
        self.markdown_dir = self.output_dir / "markdown"
        self.json_dir = self.output_dir / "json"

        for d in [self.metadata_dir, self.markdown_dir, self.json_dir]:
            d.mkdir(exist_ok=True)

        self.authors_data = {}
        self.sections_data = {}
        self.periodicals_data = {}

        self.stats = {
            "html_processed": 0,
            "pdf_processed": 0,
            "errors": 0,
            "skipped_non_english": 0,
            "total_words": 0,
        }

    def download_json_metadata(self):
        """Fetch MIA's JSON metadata files"""
        json_urls = {
            "authors": "https://www.marxists.org/admin/js/data/authors.json",
            "sections": "https://www.marxists.org/admin/js/data/sections.json",
            "periodicals": "https://www.marxists.org/admin/js/data/periodicals.json",
        }

        print("Downloading MIA JSON metadata...")
        for name, url in json_urls.items():
            try:
                print(f"  Fetching {name}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.json()
                output_path = self.json_dir / f"{name}.json"
                output_path.write_text(json.dumps(data, indent=2))

                # Store in memory for processing
                if name == "authors":
                    self.authors_data = data
                elif name == "sections":
                    self.sections_data = data
                elif name == "periodicals":
                    self.periodicals_data = data

                print(f"    ✓ Saved to {output_path}")
            except Exception as e:
                print(f"    ✗ Error fetching {name}: {e}")

    def load_json_metadata(self):
        """Load previously downloaded JSON metadata"""
        for name in ["authors", "sections", "periodicals"]:
            json_path = self.json_dir / f"{name}.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                    if name == "authors":
                        self.authors_data = data
                    elif name == "sections":
                        self.sections_data = data
                    elif name == "periodicals":
                        self.periodicals_data = data

    def is_english_content(self, path: Path) -> bool:
        """Heuristic to detect English content based on path"""
        path_str = str(path).lower()

        # Skip non-English language directories
        non_english_dirs = [
            "/chinese/",
            "/deutsch/",
            "/espanol/",
            "/francais/",
            "/italiano/",
            "/japanese/",
            "/polski/",
            "/portugues/",
            "/russian/",
            "/turkce/",
            "/arabic/",
            "/svenska/",
            "/catala/",
            "/greek/",
            "/korean/",
            "/farsi/",
        ]

        for lang_dir in non_english_dirs:
            if lang_dir in path_str:
                return False

        # Archive and history sections are primarily English
        if "/archive/" in path_str or "/history/" in path_str:
            return True

        # Reference section is English
        if "/reference/" in path_str or "/glossary/" in path_str:
            return True

        return True  # Default to processing

    def extract_metadata_from_html(self, html_path: Path, content: str) -> DocumentMetadata:
        """Extract metadata from HTML file"""
        soup = BeautifulSoup(content, "html.parser")

        # Try to extract title
        title = "Unknown"
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else "Unknown"
        elif soup.h1:
            title = soup.h1.get_text().strip()

        # Try to extract author from path or content
        author = None
        path_str = str(html_path)
        if "/archive/" in path_str:
            parts = path_str.split("/archive/")[-1].split("/")
            if len(parts) > 0:
                author = parts[0].replace("-", " ").title()

        # Try to extract date
        date = None
        date_meta = soup.find("meta", {"name": "date"})
        if date_meta:
            date = date_meta.get("content")

        # Construct source URL
        source_url = str(html_path).replace(str(self.archive_root), "https://www.marxists.org")

        return DocumentMetadata(
            source_url=source_url,
            title=title,
            author=author,
            date=date,
            language="en",
            doc_type="html",
            original_path=str(html_path),
            processed_date=datetime.now().isoformat(),
        )

    def html_to_markdown(self, html_path: Path) -> tuple[str, DocumentMetadata] | None:
        """Convert HTML file to markdown with metadata"""
        try:
            content = html_path.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")

            # Remove script, style, nav elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Extract metadata
            metadata = self.extract_metadata_from_html(html_path, content)

            # Convert to markdown
            markdown_content = md(str(soup), heading_style="ATX")

            # Clean up excessive whitespace
            markdown_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown_content)

            # Calculate word count and hash
            word_count = len(markdown_content.split())
            content_hash = hashlib.sha256(markdown_content.encode()).hexdigest()[:16]

            metadata.word_count = word_count
            metadata.content_hash = content_hash

            return markdown_content, metadata

        except Exception as e:
            print(f"Error processing {html_path}: {e}")
            return None

    def pdf_to_markdown(self, pdf_path: Path) -> tuple[str, DocumentMetadata] | None:
        """Convert PDF to markdown using pymupdf4llm"""
        try:
            # Convert PDF to markdown
            markdown_content = pymupdf4llm.to_markdown(str(pdf_path))

            # Extract basic metadata
            source_url = str(pdf_path).replace(str(self.archive_root), "https://www.marxists.org")
            title = pdf_path.stem.replace("-", " ").title()

            # Try to infer author from path
            author = None
            path_str = str(pdf_path)
            if "/archive/" in path_str:
                parts = path_str.split("/archive/")[-1].split("/")
                if len(parts) > 0:
                    author = parts[0].replace("-", " ").title()

            word_count = len(markdown_content.split())
            content_hash = hashlib.sha256(markdown_content.encode()).hexdigest()[:16]

            metadata = DocumentMetadata(
                source_url=source_url,
                title=title,
                author=author,
                language="en",
                doc_type="pdf",
                original_path=str(pdf_path),
                processed_date=datetime.now().isoformat(),
                word_count=word_count,
                content_hash=content_hash,
            )

            return markdown_content, metadata

        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return None

    def save_document(self, content: str, metadata: DocumentMetadata):
        """Save markdown content and metadata"""
        # Create safe filename
        safe_title = re.sub(r"[^\w\s-]", "", metadata.title)[:100]
        safe_title = re.sub(r"[-\s]+", "-", safe_title)

        filename = f"{safe_title}_{metadata.content_hash}"

        # Save markdown
        md_path = self.markdown_dir / f"{filename}.md"

        # Add metadata header to markdown
        header = f"""---
title: {metadata.title}
author: {metadata.author or 'Unknown'}
source_url: {metadata.source_url}
date: {metadata.date or 'Unknown'}
language: {metadata.language}
doc_type: {metadata.doc_type}
word_count: {metadata.word_count}
processed_date: {metadata.processed_date}
---

"""
        md_path.write_text(header + content, encoding="utf-8")

        # Save metadata JSON
        meta_path = self.metadata_dir / f"{filename}.json"
        meta_path.write_text(json.dumps(asdict(metadata), indent=2))

        self.stats["total_words"] += metadata.word_count

    def process_archive(self, archive_path: Path):
        """Process entire MIA archive directory"""
        self.archive_root = archive_path
        print(f"Processing archive at: {archive_path}")
        print(f"Output directory: {self.output_dir}")

        # Load metadata if available
        self.load_json_metadata()

        # Find all HTML files
        html_files = list(archive_path.rglob("*.htm")) + list(archive_path.rglob("*.html"))
        pdf_files = list(archive_path.rglob("*.pdf"))

        print(f"\nFound {len(html_files)} HTML files and {len(pdf_files)} PDFs")

        # Process HTML files
        print("\n=== Processing HTML files ===")
        for i, html_path in enumerate(html_files, 1):
            if not self.is_english_content(html_path):
                self.stats["skipped_non_english"] += 1
                continue

            if i % 100 == 0:
                print(f"  Processed {i}/{len(html_files)} HTML files...")

            result = self.html_to_markdown(html_path)
            if result:
                content, metadata = result
                self.save_document(content, metadata)
                self.stats["html_processed"] += 1
            else:
                self.stats["errors"] += 1

        # Process PDFs
        print("\n=== Processing PDF files ===")
        for i, pdf_path in enumerate(pdf_files, 1):
            if not self.is_english_content(pdf_path):
                self.stats["skipped_non_english"] += 1
                continue

            if i % 10 == 0:
                print(f"  Processed {i}/{len(pdf_files)} PDFs...")

            result = self.pdf_to_markdown(pdf_path)
            if result:
                content, metadata = result
                self.save_document(content, metadata)
                self.stats["pdf_processed"] += 1
            else:
                self.stats["errors"] += 1

        self.print_stats()
        self.save_processing_report()

    def print_stats(self):
        """Print processing statistics"""
        print("\n" + "=" * 50)
        print("PROCESSING COMPLETE")
        print("=" * 50)
        print(f"HTML files processed: {self.stats['html_processed']}")
        print(f"PDF files processed: {self.stats['pdf_processed']}")
        print(f"Non-English skipped: {self.stats['skipped_non_english']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Total words: {self.stats['total_words']:,}")
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Markdown files: {self.markdown_dir}")
        print(f"Metadata files: {self.metadata_dir}")

    def save_processing_report(self):
        """Save processing report"""
        report_path = self.output_dir / "processing_report.json"
        report = {
            "processed_date": datetime.now().isoformat(),
            "statistics": self.stats,
            "output_directory": str(self.output_dir),
        }
        report_path.write_text(json.dumps(report, indent=2))
        print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Process Marxists Internet Archive for RAG ingestion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download JSON metadata
  python mia_processor.py --download-json

  # Process archive
  python mia_processor.py --process-archive ~/Downloads/dump_www-marxists-org/

  # Custom output directory
  python mia_processor.py --process-archive ~/Downloads/dump_www-marxists-org/ --output ~/my-rag-data/
        """,
    )

    parser.add_argument(
        "--download-json", action="store_true", help="Download MIA JSON metadata files"
    )
    parser.add_argument("--process-archive", type=Path, help="Path to MIA archive directory")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("~/marxists-processed").expanduser(),
        help="Output directory (default: ~/marxists-processed)",
    )

    args = parser.parse_args()

    processor = MIAProcessor(output_dir=args.output)

    if args.download_json:
        processor.download_json_metadata()

    if args.process_archive:
        if not args.process_archive.exists():
            print(f"Error: Archive path does not exist: {args.process_archive}")
            return 1
        processor.process_archive(args.process_archive)

    if not args.download_json and not args.process_archive:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
