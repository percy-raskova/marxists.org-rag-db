# Runpod.io Self-Hosted Embeddings Guide

## Overview

Using Runpod.io for GPU rental provides the best cost-performance ratio for embedding generation at 200GB scale.

**Total estimated cost: $40-60** (vs $500-1000 for API-based solutions)

## Recommended Setup

### Optimal Configuration

**GPU**: RTX 4090 (24GB VRAM)
- Cost: ~$0.50/hour
- Throughput: ~25,000 embeddings/hour
- Total time: 80-100 hours
- Total cost: $40-60

**Model**: BAAI/bge-large-en-v1.5
- Dimensions: 1024
- Quality: Excellent (beats OpenAI ada-002 on MTEB)
- Open source: No licensing issues

### Alternative Budget Option

**GPU**: RTX 3090 (24GB VRAM)
- Cost: ~$0.30/hour
- Throughput: ~15,000 embeddings/hour
- Total time: 130-160 hours
- Total cost: $40-50

**Model**: sentence-transformers/all-MiniLM-L12-v2
- Dimensions: 384
- Quality: Good (smaller but faster)

## Implementation

### 1. Runpod Setup Script

```python
# runpod_embeddings.py
import torch
from sentence_transformers import SentenceTransformer
import msgpack
import redis
from pathlib import Path
from typing import List, Iterator
import logging
from tqdm import tqdm
import gc

class RunpodEmbeddingService:
    """
    Optimized embedding service for Runpod GPUs.
    Processes 200GB corpus efficiently.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        batch_size: int = 256,
        device: str = "cuda",
        cache_dir: str = "./embedding_cache"
    ):
        self.device = device
        self.batch_size = batch_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Load model with optimizations
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = 512  # Optimize for most docs

        # Enable mixed precision for 2x speedup
        if device == "cuda":
            self.use_amp = True
            torch.cuda.empty_cache()

        # Redis for job queue and caching
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=False  # Binary for msgpack
        )

        self.processed_count = 0
        self.logger = logging.getLogger(__name__)

    def process_batch(self, texts: List[str]) -> List[List[float]]:
        """Process a batch of texts to embeddings."""
        with torch.cuda.amp.autocast(enabled=self.use_amp):
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # Unit vectors for cosine similarity
            )
        return embeddings.tolist()

    def process_corpus_shard(self, shard_path: Path) -> Iterator[dict]:
        """
        Process a shard of the corpus.
        Yields document + embedding pairs.
        """
        # Load documents from shard
        documents = self.load_shard(shard_path)

        # Process in optimized batches
        batch = []
        batch_ids = []

        for doc in tqdm(documents, desc=f"Processing {shard_path.name}"):
            # Check cache first
            cache_key = f"emb:{doc['content_hash']}"
            cached = self.redis.get(cache_key)

            if cached:
                embedding = msgpack.unpackb(cached)
                yield {**doc, 'embedding': embedding}
                continue

            # Add to batch
            batch.append(doc['content'])
            batch_ids.append(doc)

            # Process when batch is full
            if len(batch) >= self.batch_size:
                embeddings = self.process_batch(batch)

                for doc, embedding in zip(batch_ids, embeddings):
                    # Cache the embedding
                    cache_key = f"emb:{doc['content_hash']}"
                    self.redis.set(
                        cache_key,
                        msgpack.packb(embedding),
                        ex=86400 * 7  # 7 day TTL
                    )

                    yield {**doc, 'embedding': embedding}

                # Clear batch
                batch = []
                batch_ids = []

                # Periodic cleanup
                if self.processed_count % 10000 == 0:
                    gc.collect()
                    torch.cuda.empty_cache()

                self.processed_count += self.batch_size

        # Process remaining
        if batch:
            embeddings = self.process_batch(batch)
            for doc, embedding in zip(batch_ids, embeddings):
                cache_key = f"emb:{doc['content_hash']}"
                self.redis.set(
                    cache_key,
                    msgpack.packb(embedding),
                    ex=86400 * 7
                )
                yield {**doc, 'embedding': embedding}

    def load_shard(self, shard_path: Path) -> List[dict]:
        """Load a shard of processed documents."""
        # Implement based on your storage format
        # This is a placeholder
        import json

        documents = []
        for json_file in shard_path.glob("*.json"):
            with open(json_file) as f:
                doc = json.load(f)
                documents.append(doc)

        return documents

    def get_progress_stats(self) -> dict:
        """Get processing statistics."""
        return {
            'processed': self.processed_count,
            'cache_size': self.redis.dbsize(),
            'gpu_memory': torch.cuda.memory_allocated() / 1024**3,  # GB
            'gpu_memory_cached': torch.cuda.memory_reserved() / 1024**3,
        }
```

### 2. Runpod Deployment Script

```bash
#!/bin/bash
# deploy_to_runpod.sh

# Create Runpod pod with RTX 4090
runpod create pod \
  --name "mia-embeddings" \
  --gpu-type "RTX 4090" \
  --gpu-count 1 \
  --container-image "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime" \
  --container-disk 100 \
  --volume-size 500 \
  --ports "6379:6379,8888:8888" \
  --env "CUDA_VISIBLE_DEVICES=0"

# Wait for pod to be ready
sleep 30

# Get pod ID
POD_ID=$(runpod list pods | grep "mia-embeddings" | awk '{print $1}')

# Copy code to pod
runpod cp runpod_embeddings.py $POD_ID:/workspace/
runpod cp requirements.txt $POD_ID:/workspace/

# Install dependencies
runpod exec $POD_ID "pip install -r /workspace/requirements.txt"

# Start Redis for caching
runpod exec $POD_ID "redis-server --daemonize yes"

# Start Jupyter for monitoring (optional)
runpod exec $POD_ID "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser &"

echo "Pod ready at: $(runpod get pod $POD_ID | grep 'Public IP')"
```

### 3. Distributed Processing Orchestrator

```python
# orchestrate_embeddings.py
import asyncio
from pathlib import Path
from typing import List
import aiohttp
import asyncio
from tqdm.asyncio import tqdm

class EmbeddingOrchestrator:
    """
    Orchestrates embedding generation across multiple Runpod instances.
    """

    def __init__(self, pod_urls: List[str], corpus_path: Path):
        self.pod_urls = pod_urls
        self.corpus_path = corpus_path
        self.shards = self.create_shards()

    def create_shards(self, shard_size_gb: int = 10) -> List[Path]:
        """Split corpus into shards for parallel processing."""
        # Implementation depends on your corpus structure
        # This creates logical shards
        shards = []
        for i in range(0, 200, shard_size_gb):
            shard_path = self.corpus_path / f"shard_{i:03d}_{i+shard_size_gb:03d}"
            if shard_path.exists():
                shards.append(shard_path)
        return shards

    async def process_shard_on_pod(
        self,
        session: aiohttp.ClientSession,
        pod_url: str,
        shard_path: Path
    ):
        """Send shard to pod for processing."""
        async with session.post(
            f"{pod_url}/process",
            json={"shard_path": str(shard_path)}
        ) as response:
            result = await response.json()
            return result

    async def run(self):
        """Orchestrate parallel embedding generation."""
        async with aiohttp.ClientSession() as session:
            # Create tasks for all shards
            tasks = []

            for i, shard in enumerate(self.shards):
                # Round-robin pods
                pod_url = self.pod_urls[i % len(self.pod_urls)]

                task = self.process_shard_on_pod(
                    session, pod_url, shard
                )
                tasks.append(task)

            # Process all shards in parallel
            results = await tqdm.gather(*tasks, desc="Processing shards")

            return results

# Usage
if __name__ == "__main__":
    # If using multiple pods for even faster processing
    orchestrator = EmbeddingOrchestrator(
        pod_urls=[
            "http://pod1.runpod.io:8000",
            "http://pod2.runpod.io:8000",
        ],
        corpus_path=Path("/data/marxists-processed")
    )

    asyncio.run(orchestrator.run())
```

### 4. Optimizations for Maximum Throughput

```python
# optimization_config.py

OPTIMIZATIONS = {
    # Model optimizations
    "use_fp16": True,  # Half precision for 2x speed
    "compile_model": True,  # Torch 2.0 compilation
    "use_flash_attention": True,  # If available

    # Batching optimizations
    "dynamic_batching": True,
    "max_batch_size": 512,  # For 24GB VRAM
    "sequence_bucketing": True,  # Group similar lengths

    # Caching
    "enable_redis_cache": True,
    "cache_ttl_days": 7,

    # Memory management
    "gradient_checkpointing": False,  # Not needed for inference
    "empty_cache_interval": 10000,

    # Parallelization
    "num_workers": 4,  # DataLoader workers
    "prefetch_factor": 2,
}

# Apply optimizations
def optimize_model(model):
    """Apply all optimizations to the model."""
    if OPTIMIZATIONS["use_fp16"]:
        model = model.half()

    if OPTIMIZATIONS["compile_model"]:
        import torch._dynamo
        model = torch.compile(model, mode="reduce-overhead")

    return model
```

## Monitoring & Management

### Progress Tracking Dashboard

```python
# monitor.py
import streamlit as st
import redis
import pandas as pd
from datetime import datetime

st.title("MIA Embeddings Progress")

# Connect to Redis
r = redis.Redis(host='your-runpod-ip', port=6379)

# Get stats
total_docs = 5_000_000  # Estimated
processed = r.get('processed_count') or 0
rate = r.get('processing_rate') or 0

# Display metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Progress", f"{processed / total_docs * 100:.1f}%")

with col2:
    st.metric("Documents/hour", f"{rate:,}")

with col3:
    hours_remaining = (total_docs - processed) / rate if rate > 0 else 0
    st.metric("Time remaining", f"{hours_remaining:.1f} hours")

# Cost tracking
hours_used = processed / rate if rate > 0 else 0
cost = hours_used * 0.50  # RTX 4090 rate
st.metric("Current cost", f"${cost:.2f}")

# Progress chart
progress_data = pd.DataFrame({
    'Time': pd.date_range(start='2024-01-01', periods=100, freq='H'),
    'Documents': range(0, processed, processed//100)
})
st.line_chart(progress_data.set_index('Time'))
```

## Cost Comparison

| Method | Total Cost | Time | Control | Quality |
|--------|------------|------|---------|---------|
| **Runpod RTX 4090** | **$40-60** | 80-100h | Full | Excellent |
| VertexAI API | $500-1000 | 24-48h | Limited | Excellent |
| OpenAI Batch | $400-800 | 48-72h | None | Good |
| Buy A100 | $15,000+ | 40-50h | Full | Excellent |

## Advantages of Runpod Approach

✅ **10-20x cheaper** than API solutions
✅ **Full control** over the process
✅ **No rate limits** - process as fast as GPU allows
✅ **Privacy** - data never leaves your control
✅ **Flexibility** - choose any embedding model
✅ **Pause/resume** - pay only for actual usage
✅ **Scale horizontally** - rent multiple GPUs if needed

## Quick Start

1. **Sign up for Runpod**: https://runpod.io
2. **Add credits**: $100 should be more than enough
3. **Deploy the pod**: Run `deploy_to_runpod.sh`
4. **Start processing**: Run `python runpod_embeddings.py`
5. **Monitor progress**: Check dashboard or logs
6. **Terminate when done**: Don't forget to stop the pod!

## Estimated Timeline

With single RTX 4090:
- Day 1-2: Setup and testing on small sample
- Day 3-6: Main corpus processing (running 24/7)
- Day 7: Verification and cleanup
- **Total: ~1 week of rental = $60-80 maximum**

With 4x RTX 4090 pods (parallel):
- Day 1: Setup all pods
- Day 2-3: Complete processing
- **Total: ~48 hours = $100 total** (but done in 2 days!)

## Tips for Success

1. **Test on 1GB sample first** - Verify everything works
2. **Use Redis caching** - Resume from failures instantly
3. **Monitor GPU memory** - Adjust batch size if OOM
4. **Set up alerts** - Get notified if processing stops
5. **Use spot instances** - Even cheaper if available
6. **Pre-download model** - Don't waste GPU time downloading
7. **Checkpoint frequently** - Every 1000 docs or so

---

This approach gives you the best of both worlds: API-level simplicity with self-hosted cost savings!