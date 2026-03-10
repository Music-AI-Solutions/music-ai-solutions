# System Architecture

```mermaid
flowchart TD
A[Artist Uploads Track] --> B[Frontend - Next.js]
B --> C[Backend API - FastAPI]
C --> D[Audio Fingerprint Engine]
C --> E[Track Metadata Storage]
C --> F[Certificate Generator]
D --> G[Fingerprint Hash]
E --> H[Track Registry]
F --> I[Ownership Certificate]
G --> H
H --> I
```
