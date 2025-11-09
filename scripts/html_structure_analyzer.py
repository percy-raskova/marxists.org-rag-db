#!/usr/bin/env python3
"""
HTML Structure Analyzer for Corpus Investigation

Extracts structural metadata from HTML files WITHOUT reading full content.
This is a token-efficient tool for corpus investigation that provides:
- Document structure (headings, sections, nesting)
- Metadata tags (author, title, keywords, etc.)
- Link patterns (internal/external references)
- CSS classes (semantic structure hints)
- File statistics (paragraphs, lists, tables)

Usage:
    python html_structure_analyzer.py <html_file>
    python html_structure_analyzer.py --sample <directory> --count 5
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup not installed", file=sys.stderr)
    print("Install with: pip install beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)


class HTMLStructureAnalyzer:
    """Analyze HTML file structure without reading full content."""

    def __init__(self, html_path: Path):
        self.path = html_path
        with open(html_path, encoding="utf-8", errors="ignore") as f:
            self.soup = BeautifulSoup(f.read(), "html.parser")

    def analyze(self) -> dict[str, Any]:
        """Extract structural metadata."""
        return {
            "path": str(self.path),
            "file_size": self.path.stat().st_size,
            "title": self._extract_title(),
            "doctype": self._extract_doctype(),
            "meta_tags": self._extract_meta_tags(),
            "structure": self._analyze_structure(),
            "links": self._analyze_links(),
            "css_classes": self._extract_css_classes(),
            "semantic_markers": self._extract_semantic_markers(),
            "mia_patterns": self._extract_mia_patterns(),
        }

    def _extract_title(self) -> str | None:
        """Extract document title."""
        if self.soup.title:
            return self.soup.title.string.strip() if self.soup.title.string else None
        return None

    def _extract_doctype(self) -> str | None:
        """Extract DOCTYPE declaration."""
        for item in self.soup.contents:
            if hasattr(item, "name") and item.name is None:
                # This is a declaration (DOCTYPE, comment, etc.)
                doctype_str = str(item).strip()
                if doctype_str.upper().startswith("<!DOCTYPE"):
                    return doctype_str
        return None

    def _extract_meta_tags(self) -> dict[str, str]:
        """Extract all meta tags."""
        meta_data = {}
        for meta in self.soup.find_all("meta"):
            # name-content pairs
            if meta.get("name"):
                meta_data[meta.get("name")] = meta.get("content", "")
            # property-content pairs (Open Graph, etc.)
            elif meta.get("property"):
                meta_data[meta.get("property")] = meta.get("content", "")
            # http-equiv pairs
            elif meta.get("http-equiv"):
                meta_data[f"http-equiv:{meta.get('http-equiv')}"] = meta.get(
                    "content", ""
                )
        return meta_data

    def _analyze_structure(self) -> dict[str, Any]:
        """Analyze document structure."""
        return {
            "headings": {
                "h1": len(self.soup.find_all("h1")),
                "h2": len(self.soup.find_all("h2")),
                "h3": len(self.soup.find_all("h3")),
                "h4": len(self.soup.find_all("h4")),
                "h5": len(self.soup.find_all("h5")),
                "h6": len(self.soup.find_all("h6")),
            },
            "heading_hierarchy": [
                {"level": h.name, "text": h.get_text(strip=True)[:100]}
                for h in self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            ][:20],  # First 20 headings only
            "paragraphs": len(self.soup.find_all("p")),
            "lists": {
                "ul": len(self.soup.find_all("ul")),
                "ol": len(self.soup.find_all("ol")),
            },
            "tables": len(self.soup.find_all("table")),
            "blockquotes": len(self.soup.find_all("blockquote")),
            "code_blocks": len(self.soup.find_all("pre")) + len(self.soup.find_all("code")),
        }

    def _analyze_links(self) -> dict[str, Any]:
        """Analyze link patterns."""
        all_links = self.soup.find_all("a", href=True)
        hrefs = [a["href"] for a in all_links]

        # Categorize links
        internal = [h for h in hrefs if h.startswith(("/", "./", "../", "#"))]
        external = [h for h in hrefs if h.startswith(("http://", "https://"))]
        anchors = [h for h in hrefs if h.startswith("#")]

        return {
            "total": len(all_links),
            "internal": len(internal),
            "external": len(external),
            "anchors": len(anchors),
            "sample_internal": internal[:5],
            "sample_external": external[:3],
        }

    def _extract_css_classes(self) -> dict[str, int]:
        """Extract CSS class usage (semantic structure hints)."""
        class_counts = {}
        for elem in self.soup.find_all(class_=True):
            for cls in elem.get("class", []):
                class_counts[cls] = class_counts.get(cls, 0) + 1
        # Return top 20 most common classes
        return dict(sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:20])

    def _extract_semantic_markers(self) -> dict[str, Any]:
        """Extract semantic markers specific to MIA corpus."""
        return {
            # Navigation and structure
            "has_breadcrumb": bool(self.soup.find(class_="breadcrumb")),
            "has_title_class": bool(self.soup.find(class_="title")),
            "has_fst_class": bool(self.soup.find(class_="fst")),  # First paragraph

            # Content annotations
            "has_quoteb_class": bool(self.soup.find(class_="quoteb")),  # Block quote
            "has_context_class": bool(self.soup.find(class_="context")),  # Historical context
            "has_information_class": bool(self.soup.find(class_="information")),  # Provenance

            # MIA-specific patterns
            "has_info_class": bool(self.soup.find(class_="info")),  # Info boxes
            "has_infotop_class": bool(self.soup.find(class_="infotop")),
            "has_infobot_class": bool(self.soup.find(class_="infobot")),
            "has_toplink_class": bool(self.soup.find(class_="toplink")),  # Top navigation
            "has_updat_class": bool(self.soup.find(class_="updat")),  # Update metadata

            # Citation and reference patterns
            "has_footnotes": bool(
                self.soup.find("a", href=lambda h: h and h.startswith("#footnote"))
            ),
            "has_anchors": bool(self.soup.find("a", attrs={"name": True})),
            "has_section_anchors": bool(
                self.soup.find("a", attrs={"name": lambda n: n and n.startswith("s")})
            ),
        }

    def _extract_mia_patterns(self) -> dict[str, Any]:
        """Extract MIA-specific organizational patterns based on corpus analysis."""
        import re

        path_parts = Path(self.path).parts
        title = self._extract_title()

        # === PATH-BASED METADATA EXTRACTION ===
        # Archive pattern: /archive/{author}/works/{year}/{work}/{chapter}.htm
        author_from_path = None
        year_from_path = None
        work_from_path = None
        section_type = None

        if "archive" in path_parts:
            archive_idx = path_parts.index("archive")
            if len(path_parts) > archive_idx + 1:
                author_from_path = path_parts[archive_idx + 1].replace("-", " ").title()
            if "works" in path_parts:
                works_idx = path_parts.index("works")
                if len(path_parts) > works_idx + 1:
                    year_candidate = path_parts[works_idx + 1]
                    # Extract year like "1867-c1" -> "1867"
                    year_match = re.match(r'(\d{4})', year_candidate)
                    if year_match:
                        year_from_path = year_match.group(1)
                        work_from_path = year_candidate
            section_type = "archive"
        elif "history" in path_parts:
            section_type = "history"
            if "etol" in path_parts:
                section_type = "history/etol"
            elif "erol" in path_parts:
                section_type = "history/erol"
        elif "subject" in path_parts:
            section_type = "subject"
        elif "glossary" in path_parts:
            section_type = "glossary"
        elif "reference" in path_parts:
            section_type = "reference"

        # === BREADCRUMB EXTRACTION ===
        breadcrumb = []
        breadcrumb_elem = self.soup.find(class_="title")
        if breadcrumb_elem:
            links = breadcrumb_elem.find_all("a", class_="title")
            breadcrumb = [link.get_text(strip=True) for link in links]

        # === DATE EXTRACTION FROM TITLE ===
        date_from_title = None
        if title:
            # Match (1917), (1848-1850), (March 1917), (Spring 1848)
            date_match = re.search(r'\(([A-Za-z\s]*\d{4}(?:-\d{4})?)\)', title)
            if date_match:
                date_from_title = date_match.group(1)

        # === DOCUMENT TYPE DETECTION ===
        doc_type_indicators = {
            "article": self.soup.find("h1") and len(self.soup.find_all("p")) > 10,
            "index_page": "index" in self.path.name and len(self.soup.find_all("a")) > 20,
            "chapter": bool(re.match(r'ch\d+\.htm', self.path.name)),
            "letter": bool(self.soup.find(string=lambda t: t and "Dear" in t[:50] if t else False)),
            "speech": bool(self.soup.find(string=lambda t: t and ("Comrades" in t[:100]) if t else False)) or ("Speech" in title or "Address" in title if title else False),
        }

        # === PUBLICATION PROVENANCE INFO ===
        provenance_markers = ["First published:", "Source:", "Written:", "Transcription:", "Translated:", "Scanned:"]
        has_publication_info = bool(
            self.soup.find(class_="info") or
            self.soup.find(class_="information") or
            self.soup.find(string=lambda t: t and any(marker in t for marker in provenance_markers) if t else False)
        )

        # === FOOTNOTE DETECTION ===
        footnote_patterns = {
            "has_footnote_refs": bool(self.soup.find("sup", class_="enote")),
            "has_footnote_section": bool(self.soup.find("a", attrs={"name": lambda n: n and n.isdigit()})),
            "footnote_count": len(self.soup.find_all("sup", class_="enote")),
        }

        # === CONTENT STRUCTURE METRICS ===
        headings = self.soup.find_all(["h1", "h2", "h3", "h4"])
        paragraphs = self.soup.find_all("p")
        links = self.soup.find_all("a")

        return {
            # Path-based extraction
            "section_type": section_type,
            "author_from_path": author_from_path,
            "year_from_path": year_from_path,
            "work_from_path": work_from_path,

            # Breadcrumb navigation
            "breadcrumb": breadcrumb if breadcrumb else None,

            # Date extraction
            "date_from_title": date_from_title,

            # Document classification
            "doc_type_indicators": {k: v for k, v in doc_type_indicators.items() if v},

            # Provenance
            "has_publication_info": has_publication_info,

            # Footnote structure
            "footnote_info": footnote_patterns,

            # Structure metrics
            "appears_hierarchical": len(headings) >= 3,
            "max_heading_depth": max([int(h.name[1]) for h in headings]) if headings else 0,
            "content_density": len(paragraphs) / max(len(links), 1),
            "avg_paragraph_length": sum(len(p.get_text()) for p in paragraphs) / max(len(paragraphs), 1),
        }


def analyze_file(html_path: Path, output_format: str = "json") -> None:
    """Analyze a single HTML file."""
    analyzer = HTMLStructureAnalyzer(html_path)
    result = analyzer.analyze()

    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif output_format == "summary":
        mia = result['mia_patterns']
        print(f"=== {result['path']} ===")
        print(f"Size: {result['file_size']:,} bytes")
        print(f"Title: {result['title']}")
        print(f"DOCTYPE: {result['doctype']}")

        print("\nMIA Classification:")
        print(f"  Section: {mia['section_type']}")
        if mia['author_from_path']:
            print(f"  Author: {mia['author_from_path']}")
        if mia['year_from_path']:
            print(f"  Year: {mia['year_from_path']}")
        if mia['date_from_title']:
            print(f"  Date (title): {mia['date_from_title']}")
        if mia['breadcrumb']:
            print(f"  Breadcrumb: {' > '.join(mia['breadcrumb'])}")
        if mia['doc_type_indicators']:
            print(f"  Doc Types: {', '.join(mia['doc_type_indicators'].keys())}")

        print(f"\nMeta Tags ({len(result['meta_tags'])}):")
        for key, value in list(result["meta_tags"].items())[:8]:
            print(f"  {key}: {value[:80]}")

        print("\nStructure:")
        print(f"  Headings: {result['structure']['headings']} (max depth: h{mia['max_heading_depth']})")
        print(f"  Paragraphs: {result['structure']['paragraphs']} (avg: {mia['avg_paragraph_length']:.0f} chars)")
        print(f"  Links: {result['links']['total']} (internal: {result['links']['internal']}, external: {result['links']['external']})")
        print(f"  Content density: {mia['content_density']:.2f} (paragraphs per link)")
        if mia['footnote_info']['footnote_count'] > 0:
            print(f"  Footnotes: {mia['footnote_info']['footnote_count']}")

        print("\nTop CSS Classes:")
        for cls, count in list(result["css_classes"].items())[:8]:
            print(f"  .{cls}: {count}")

        print("\nKey Features:")
        features = []
        if mia['appears_hierarchical']:
            features.append("Hierarchical structure")
        if mia['has_publication_info']:
            features.append("Publication provenance")
        for marker in ["has_fst_class", "has_info_class", "has_anchors", "has_footnotes"]:
            if result["semantic_markers"].get(marker):
                features.append(marker.replace("has_", "").replace("_", " "))
        if features:
            print(f"  {', '.join(features)}")


def sample_directory(directory: Path, count: int = 5, output_format: str = "summary") -> None:
    """Analyze a random sample of HTML files from directory."""
    import random

    html_files = list(directory.rglob("*.htm")) + list(directory.rglob("*.html"))
    if not html_files:
        print(f"No HTML files found in {directory}", file=sys.stderr)
        return

    sample = random.sample(html_files, min(count, len(html_files)))
    print(f"Analyzing {len(sample)} files from {directory}...\n")

    for i, html_file in enumerate(sample, 1):
        print(f"\n{'='*80}")
        print(f"Sample {i}/{len(sample)}")
        print(f"{'='*80}\n")
        analyze_file(html_file, output_format)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze HTML file structure without reading full content"
    )
    parser.add_argument("path", nargs="?", help="Path to HTML file or directory")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Sample random files from directory",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of files to sample (default: 5)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )

    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        sys.exit(1)

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    if args.sample or path.is_dir():
        sample_directory(path, args.count, args.format)
    else:
        analyze_file(path, args.format)


if __name__ == "__main__":
    main()
