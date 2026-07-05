# document-ai

A modular, production-grade platform for intelligent document ingestion, semantic search, and retrieval-augmented generation (RAG).

It enables the transformation of unstructured documents into a queryable knowledge base, supporting natural language search, citation-grounded answers, and fine-grained access control.

The platform is built around clean abstractions and swappable backends — identity providers, storage, databases, task queues, and document sources are all configurable without code changes.

## Architecture

The codebase is organised into the following layers, in dependency order:

- [`common/`](common/COMMON_SPEC.md) — shared domain models
- [`libs/`](libs/LIBS_SPEC.md) — pure domain logic, stateless and injectable
- [`backends/`](backends/BACKENDS_SPEC.md) — abstractions for external systems (storage, task queues, LLM inference, embeddings, observability)
- [`pipelines/`](pipelines/PIPELINES_SPEC.md) — orchestration layer
- [`services/`](services/SERVICES_SPEC.md) — facade layer used by API routes, CLI commands, and workers

[`infrastructure/`](infrastructure/INFRASTRUCTURE_SPEC.md) sits alongside this chain: it holds concrete, technology-specific implementations of the ABCs defined in `backends/`, wired into `services/` at the application entrypoint rather than depended on directly by any of the five layers above.

```
document-ai/
├── common/          # shared domain models
├── libs/            # pure domain logic, stateless and injectable
├── backends/        # abstractions for external systems
├── pipelines/       # orchestration layer
├── services/        # facade layer used by API routes, CLI commands, and workers
├── infrastructure/  # concrete implementations of backend abstractions
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## License

GPL-3.0 — see [LICENSE](LICENSE).