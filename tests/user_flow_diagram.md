# User Flow Diagram

```mermaid
flowchart LR
    A[Select User Type\nIndustry / Consumer] --> B[Ask Query]
    B --> C[AI Query Analysis]
    C --> D[Search BIS Knowledge]
    D --> E[Retrieve Relevant Info]
    E --> F[Generate Answer]
    F --> G{Need Standard?}
    G -->|Yes| H[Show Applicable Standard]
    G -->|No| I[Show Guidance / Service Info]
    H --> J[Requirements + Testing + Certification]
    I --> K[Source / Reference]
    J --> K
    K --> L[Next Step / Feedback]
```

## Example flows

### Industry

- Ask about a manufactured product
- Receive standard recommendation
- View requirements, tests, and certification guidance

### Consumer

- Ask about BIS mark or consumer guidance
- Receive simplified explanation and official references
