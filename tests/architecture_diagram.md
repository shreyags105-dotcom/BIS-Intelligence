# Architecture Diagram

```mermaid
flowchart TD
    U[User] --> F[Frontend\nNext.js App]
    F --> B[Backend\nFastAPI]
    B --> Q[Query Understanding]
    Q --> KB[BIS Knowledge Base]
    KB --> R[Retrieval / RAG]
    R --> L[AI / LLM]
    L --> A[Answer + Recommendation]
    L --> S[Source / Reference]
    A --> U
    S --> U
```

## Summary

- Frontend handles user interaction.
- Backend routes BIS queries and services.
- Query understanding identifies product, service, or certification intent.
- BIS knowledge base stores verified product and service data.
- Retrieval and RAG help select the relevant information.
- AI generates the final answer with source references.
