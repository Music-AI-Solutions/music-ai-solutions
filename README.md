# Music AI Solutions

Music AI Solutions is an infrastructure platform designed to help artists, producers, and music companies register audio fingerprints and generate proof-of-authorship certificates for musical works.

The platform aims to provide **cybersecured music ownership verification** in the era of AI-generated content.

## Vision
As artificial intelligence generates more music every day, verifying **who created what and when** becomes critical.

Music AI Solutions creates a system where every track can receive a **unique audio fingerprint and ownership certificate**.

## Core Features
• Audio upload and processing  
• Unique audio fingerprint generation  
• Track registration system  
• Proof-of-authorship certificate generation  
• Future public music registry  

## Platform Pipeline
Upload Track → Generate Audio Fingerprint → Store Track Metadata → Generate Ownership Certificate

## Tech Stack
Frontend: Next.js  
Backend: FastAPI  
Audio Processing: Librosa  
Certificates: ReportLab

## MVP Goal
1. Upload a track
2. Generate a fingerprint
3. Issue a certificate of authorship

## Status
The backend path for the MVP is implemented: upload, fingerprint, register in a SQLite registry, flag similar tracks, and issue a PDF certificate. The Next.js frontend is not built yet.

The fingerprint hashes pairs of spectral peaks (offset-invariant) and compares tracks by hash overlap. WAV files are decoded with the standard library; other formats need librosa. It has been checked on synthetic audio only, so tune it on real music and compressed copies before relying on it.

## Run it
```bash
pip install -r requirements.txt
python test_core.py            # checks fingerprint, registry and certificate
uvicorn app:app --reload       # API on http://127.0.0.1:8000
```

| Endpoint | What it does |
| --- | --- |
| `POST /tracks` | Upload `file`, `title`, `artist`. Returns the record and similar registered tracks |
| `GET /tracks/{id}` | Registry record |
| `GET /tracks/{id}/certificate` | Proof-of-authorship certificate (PDF) |

The registry path can be set with the `MAS_DB` environment variable (default `registry.db`).

## Founder
Santiago Quevedo Jaramillo
Founder – Music AI Solutions
Medellín, Colombia
