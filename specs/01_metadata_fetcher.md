# Component Specification: MIA JSON Metadata Fetcher

**Version:** 1.0  
**Status:** Ready for Implementation  
**Estimated Complexity:** Low  
**Estimated Time:** 30-60 minutes  

## 1. Objective

Fetch and cache JSON metadata files from marxists.org that provide structured information about authors, sections, and periodicals in the archive.

## 2. Scope

**In Scope:**

- Download three JSON metadata files from marxists.org
- Validate JSON structure
- Cache files locally
- Provide parsed data structures
- Handle network errors gracefully

**Out of Scope:**

- Processing archive content
- Database operations
- Embedding generation

## 3. Technical Requirements

### 3.1 System Requirements

- Python 3.9+
- Internet connection
- Write access to output directory

### 3.2 Dependencies

```python
requests>=2.31.0
```

### 3.3 Performance Requirements

- Complete download in <60 seconds
- Handle connection timeouts (30s max per request)
- Retry logic: 3 attempts with exponential backoff

## 4. Data Contracts

### 4.1 Input Parameters

```python
@dataclass
class FetchConfig:
    output_dir: Path          # Where to save JSON files
    timeout: int = 30         # Request timeout in seconds
    max_retries: int = 3      # Number of retry attempts
    verify_ssl: bool = True   # SSL certificate verification
```

### 4.2 Source URLs

```python
METADATA_URLS = {
    "authors": "https://www.marxists.org/admin/js/data/authors.json",
    "sections": "https://www.marxists.org/admin/js/data/sections.json",
    "periodicals": "https://www.marxists.org/admin/js/data/periodicals.json"
}
```

### 4.3 Output Structure

```
{output_dir}/
├── authors.json       # 850+ author entries with work links
├── sections.json      # Subject/topic taxonomy
├── periodicals.json   # Revolutionary publications catalog
└── metadata_info.json # Fetch metadata (timestamp, sizes, checksums)
```

### 4.4 Authors JSON Schema

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "href": {"type": "string"},
      "description": {"type": "string", "optional": true},
      "birth": {"type": "string", "optional": true},
      "death": {"type": "string", "optional": true}
    }
  }
}
```

### 4.5 Return Value

```python
@dataclass
class MetadataFetchResult:
    success: bool
    files_downloaded: List[str]
    errors: List[str]
    output_dir: Path
    fetch_timestamp: str
    total_authors: int
    total_sections: int
    total_periodicals: int
```

## 5. Functional Specification

### 5.1 Core Function Signature

```python
def fetch_metadata(config: FetchConfig) -> MetadataFetchResult:
    """
    Fetch MIA JSON metadata files.
    
    Args:
        config: Configuration for fetch operation
        
    Returns:
        MetadataFetchResult with status and statistics
        
    Raises:
        NetworkError: If all retries fail
        ValidationError: If JSON is malformed
        IOError: If cannot write to output directory
    """
```

### 5.2 Processing Steps

1. **Validate output directory**
   - Check write permissions
   - Create directory if doesn't exist

2. **For each metadata URL:**
   - Attempt download with retry logic
   - Validate JSON structure
   - Check for minimum expected size
   - Calculate SHA256 checksum
   - Save to output directory

3. **Generate metadata info file**
   - Timestamp
   - File sizes
   - Checksums
   - Record counts

4. **Return result summary**

### 5.3 Retry Logic

```python
def fetch_with_retry(url: str, max_retries: int, timeout: int) -> bytes:
    """
    Exponential backoff: 1s, 2s, 4s delays between retries
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## 6. Error Handling

### 6.1 Error Types

```python
class MetadataFetchError(Exception):
    """Base exception for metadata fetch errors"""
    
class NetworkError(MetadataFetchError):
    """Network-related errors"""
    
class ValidationError(MetadataFetchError):
    """JSON validation errors"""
    
class ChecksumError(MetadataFetchError):
    """Checksum mismatch errors"""
```

### 6.2 Error Scenarios

| Scenario | Handling |
|----------|----------|
| Network timeout | Retry with exponential backoff |
| HTTP 4xx error | Fail immediately (no retry) |
| HTTP 5xx error | Retry up to max_retries |
| Malformed JSON | Log error, continue with other files |
| Empty response | Treat as error, retry |
| Disk full | Fail immediately with clear message |

### 6.3 Partial Success

If 2/3 files download successfully, mark as partial success and log warnings.

## 7. Validation Rules

### 7.1 JSON Validation

```python
def validate_authors_json(data: Any) -> bool:
    """
    Validate authors.json structure:
    - Must be array
    - Length > 800 (expect 850+)
    - Each item has 'name' and 'href' keys
    """

def validate_sections_json(data: Any) -> bool:
    """
    Validate sections.json structure:
    - Must be array
    - Length > 50
    - Each item has required keys
    """

def validate_periodicals_json(data: Any) -> bool:
    """
    Validate periodicals.json structure:
    - Must be array
    - Length > 100
    """
```

### 7.2 Size Validation

- authors.json: Expected 500KB - 2MB
- sections.json: Expected 100KB - 1MB
- periodicals.json: Expected 50KB - 500KB

Warn if outside expected ranges.

## 8. Testing Requirements

### 8.1 Unit Tests

```python
def test_fetch_with_valid_url():
    """Test successful fetch"""
    
def test_fetch_with_network_timeout():
    """Test timeout handling"""
    
def test_fetch_with_retry_logic():
    """Test retry behavior"""
    
def test_json_validation():
    """Test each validation function"""
    
def test_partial_success():
    """Test when some files fail"""
```

### 8.2 Integration Tests

```python
def test_full_fetch_pipeline():
    """Test complete fetch operation"""
    
def test_concurrent_fetch_safety():
    """Test multiple simultaneous fetches"""
```

### 8.3 Mock Testing

Use `responses` library to mock HTTP requests:

```python
@responses.activate
def test_mock_fetch():
    responses.add(
        responses.GET,
        METADATA_URLS["authors"],
        json=[{"name": "Marx", "href": "/marx/"}],
        status=200
    )
```

## 9. Success Criteria

### 9.1 Functional

- [ ] All three JSON files downloaded
- [ ] JSON validated successfully
- [ ] Metadata info file generated
- [ ] Checksums calculated and stored
- [ ] Returns accurate statistics

### 9.2 Non-Functional

- [ ] Completes in <60 seconds on typical connection
- [ ] Handles network interruptions gracefully
- [ ] Clear error messages for all failure modes
- [ ] Idempotent (safe to run multiple times)
- [ ] No data corruption on interruption

## 10. Implementation Notes

### 10.1 File Organization

```
mia_metadata_fetcher.py    # Main implementation
tests/
  test_fetcher.py          # Unit tests
  test_integration.py      # Integration tests
  fixtures/
    sample_authors.json    # Test fixtures
```

### 10.2 CLI Interface (Optional)

```bash
python mia_metadata_fetcher.py \
  --output-dir ~/marxists-metadata/ \
  --timeout 30 \
  --max-retries 3
```

### 10.3 Library Usage

```python
from mia_metadata_fetcher import fetch_metadata, FetchConfig

config = FetchConfig(
    output_dir=Path("~/marxists-metadata/"),
    timeout=30
)

result = fetch_metadata(config)
print(f"Downloaded {len(result.files_downloaded)} files")
```

## 11. Performance Benchmarks

### 11.1 Expected Performance

- Download time: 5-20 seconds (depends on connection)
- Validation time: <1 second
- Total time: <30 seconds typically

### 11.2 Resource Usage

- Memory: <50MB
- Disk: ~2MB total
- Network: ~2MB download

## 12. Security Considerations

### 12.1 Network Security

- Verify SSL certificates by default
- Provide option to disable for debugging
- No credentials required (public API)

### 12.2 File System Security

- Validate output directory path (no path traversal)
- Set appropriate file permissions (644)
- No executable permissions on JSON files

## 13. Future Enhancements

**Phase 2 (Not required now):**

- ETag caching (only download if changed)
- Compression support
- Progress bars for long downloads
- Parallel downloads
- Diff generation between updates

## 14. Dependencies on Other Components

**Upstream:** None (standalone component)  
**Downstream:**

- HTML/PDF processors will read these files
- Metadata extraction can use author info

## 15. Confidence Level

**Implementation Confidence:** 95%

**Risks:**

- URLs may change (5% risk) - mitigated by retry logic
- JSON schema may evolve - mitigated by flexible validation

**Known Unknowns:**

- None - straightforward HTTP + JSON operation

## 16. Example Usage

```python
#!/usr/bin/env python3
from pathlib import Path
from mia_metadata_fetcher import fetch_metadata, FetchConfig

def main():
    config = FetchConfig(
        output_dir=Path("./mia_metadata/"),
        timeout=30,
        max_retries=3
    )
    
    result = fetch_metadata(config)
    
    if result.success:
        print(f"✓ Fetched {len(result.files_downloaded)} files")
        print(f"  Authors: {result.total_authors}")
        print(f"  Sections: {result.total_sections}")
        print(f"  Periodicals: {result.total_periodicals}")
    else:
        print(f"✗ Errors: {result.errors}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## 17. Acceptance Test

Run this command to verify implementation:

```bash
python mia_metadata_fetcher.py --output-dir /tmp/mia_test/ && \
  [ -f /tmp/mia_test/authors.json ] && \
  [ -f /tmp/mia_test/sections.json ] && \
  [ -f /tmp/mia_test/periodicals.json ] && \
  echo "✓ All files present"
```
