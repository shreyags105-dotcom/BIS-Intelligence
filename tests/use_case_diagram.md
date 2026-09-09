# Use-Case Diagram

```mermaid
flowchart TD
    U[User] --> UC1[Ask BIS question]
    U --> UC2[Find applicable standard]
    U --> UC3[Check certification process]
    U --> UC4[Understand testing requirements]
    U --> UC5[Check BIS hallmarking]
    U --> UC6[Find relevant lab]
    U --> UC7[Ask unsupported question]

    UC1 --> S[System]
    UC2 --> S
    UC3 --> S
    UC4 --> S
    UC5 --> S
    UC6 --> S
    UC7 --> S

    S --> R1[Return BIS answer]
    S --> R2[Return source/reference]
    S --> R3[Return safe fallback]
```

## Actors

- Industry user
- Consumer user
- BIS assistant system

## Features covered

- Product recommendation
- Certification guidance
- Testing information
- Hallmarking guidance
- Lab discovery
- Safe unsupported-query behavior
