# System Diagram

User
  │
  ▼
Frontend (Next.js)
  │
  ▼
Backend API (FastAPI)
  │
  ├── Audio Fingerprint Engine (Librosa)
  ├── Track Metadata Storage
  └── Certificate Generator (ReportLab)
  │
  ▼
Certificates + Registry
