# Instance 6: Monitoring & Testing

**Quick Start Guide for AI Agent Working on Monitoring Module**

## 🎯 Your Role

You are responsible for **observability and integration testing** - ensuring all 5 instances work together correctly and monitoring system health.

**Status**: ✅ Ready for development (can start immediately with test stubs)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/monitoring/       # Metrics, dashboards, alerts
tests/integration/            # Integration tests across instances
tests/performance/            # Performance benchmarks
docs/instances/instance6-monitoring/  # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**: ALL INSTANCES (you observe everyone)
- Instance 1 (storage) - Monitor GCS usage, pipeline progress
- Instance 2 (embeddings) - Track batch progress, Runpod costs
- Instance 3 (weaviate) - Monitor query performance, index health
- Instance 4 (api) - Track endpoint latency, cache hit rates
- Instance 5 (mcp) - Monitor tool usage, error rates

**Who depends on you**: Everyone relies on your integration tests passing!

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class MonitoringInterface(Protocol):
    """Contract that other instances use"""
    def record_metric(self, name: str, value: float, labels: dict) -> None
    def increment_counter(self, name: str, labels: dict) -> None
    def observe_histogram(self, name: str, value: float, buckets: List[float]) -> None

class DashboardInterface(Protocol):
    """Dashboard contract"""
    def create_dashboard(self, config: DashboardConfig) -> Dashboard
    def update_panel(self, panel_id: str, query: str) -> None
```

### Your Deliverables

1. **Metrics Collection** (`src/mia_rag/monitoring/metrics.py`)
   - Prometheus metrics exporter
   - Custom metrics: storage_bytes, embedding_cost, query_latency
   - Metric aggregation and rollups
   - Export to Cloud Monitoring

2. **Integration Tests** (`tests/integration/`)
   - `test_storage_to_embeddings.py` - Instance 1 → 2 data flow
   - `test_embeddings_to_weaviate.py` - Instance 2 → 3 data flow
   - `test_weaviate_to_api.py` - Instance 3 → 4 query flow
   - `test_api_to_mcp.py` - Instance 4 → 5 tool calls
   - `test_end_to_end.py` - Full pipeline test

3. **Dashboards** (`src/mia_rag/monitoring/dashboards/`)
   - System Overview (all instances)
   - Storage & Pipeline (Instance 1)
   - Embeddings & Costs (Instance 2)
   - Weaviate Performance (Instance 3)
   - API Health (Instance 4)
   - MCP Tool Usage (Instance 5)

4. **Alerting** (`src/mia_rag/monitoring/alerts.py`)
   - Storage quota >80% (Instance 1)
   - Runpod cost >$70 (Instance 2)
   - Query latency >500ms p95 (Instance 3)
   - API error rate >5% (Instance 4)
   - MCP tool failures (Instance 5)

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance6           # Run your tests only
mise run quality:instance6        # Lint your code
mise run monitoring:start         # Start Prometheus + Grafana
mise run integration:run          # Run all integration tests

# Run daily integration suite
mise run integration:daily        # Full end-to-end test

# Check your boundaries
python scripts/check_boundaries.py --instance monitoring

# Submit work
git add src/mia_rag/monitoring/ tests/integration/
git commit -m "feat(monitoring): add end-to-end integration test"
git push origin monitoring-dev
```

---

## 📋 Development Checklist

- [ ] Read `docs/instances/instance6-monitoring/README.md` (your detailed guide)
- [ ] Read `PARALLEL-TEST-STRATEGY.md` (testing without cloud resources)
- [ ] Read `specs/06-TESTING.md` (formal specification)
- [ ] Set up local Prometheus + Grafana (Docker Compose)
- [ ] Implement `MonitoringInterface` in `src/mia_rag/monitoring/metrics.py`
- [ ] Write integration tests for each instance boundary
- [ ] Create Grafana dashboards (export JSON configs)
- [ ] Set up alerting rules
- [ ] Document test strategy in work logs

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/monitoring/` or `tests/integration/`
- ❌ Change `MonitoringInterface` without RFC
- ❌ Run integration tests against production (use dev/test envs!)
- ❌ Skip performance benchmarks before deployment
- ❌ Ignore failing integration tests

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Run integration tests daily (automated via GitHub Actions)
- ✅ Track metrics for cost monitoring (Runpod $$)
- ✅ Create dashboards for each instance
- ✅ Alert on SLO violations

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance6-monitoring/README.md` - Your detailed guide
2. `PARALLEL-TEST-STRATEGY.md` - Testing strategy, mocking cloud services
3. `specs/06-TESTING.md` - Formal specification

**Reference**:
- [Prometheus Docs](https://prometheus.io/docs/) - Metrics collection
- [Grafana Docs](https://grafana.com/docs/) - Dashboard creation
- `docs/architecture/infrastructure.md` - Cloud Monitoring setup

**Communication**:
- `work-logs/instance6/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `MonitoringInterface` implemented and documented
- [ ] Integration tests for all 5 boundaries
- [ ] Grafana dashboards created and exported
- [ ] Alert rules configured
- [ ] Daily integration test workflow automated
- [ ] Work log updated

---

## 💡 Pro Tips

**Testing**:
- Use `pytest-mock` for mocking GCS/Runpod/Weaviate
- Test with 1% sample data (1000 docs)
- Run integration tests in parallel (pytest-xdist)
- Expected: <5 minutes for full integration suite

**Metrics**:
- Use histogram for latency (not gauge!)
- Label metrics by instance_id
- Aggregate across instances for system view
- Expected: <50MB Prometheus storage

**Debugging**:
- Check Prometheus: `http://localhost:9090`
- Check Grafana: `http://localhost:3000`
- Query metrics: `promtool query instant 'query_latency_seconds{quantile="0.95"}'`

---

**Need help?** Check `docs/instances/instance6-monitoring/troubleshooting.md`

**Last Updated**: 2025-11-08
