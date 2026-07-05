# document-ai
A modular, production-grade platform for intelligent document ingestion, semantic search, and retrieval-augmented generation (RAG).

It enables the transformation of unstructured documents into a queryable knowledge base, supporting natural language search, citation-grounded answers, and fine-grained access control.

The platform is built around clean abstractions and swappable backends — identity providers, storage, databases, task queues, and document sources are all configurable without code changes.

## Architecture

The codebase is organised into the following layers:

- common/ — shared domain models
- libs/ — pure domain logic, stateless and injectable
- backends/ — storage abstractions
- pipelines/ — orchestration layer
- infrastructure/ — concrete implementations of backend abstractions (databases, queues, identity providers)
- services/ — entry points exposing the platform (APIs, workers)

```
document-ai/
├── common/          # shared domain models
├── libs/            # pure domain logic, stateless and injectable
├── backends/        # storage abstractions
├── pipelines/       # orchestration layer
├── infrastructure/  # concrete implementations of backend abstractions
├── services/        # entry points exposing the platform (APIs, workers)
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## License

GPL-3.0 — see [LICENSE](LICENSE).
