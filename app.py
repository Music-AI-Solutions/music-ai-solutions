# FastAPI main application
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from certificate import generate_certificate
from database import find_similar, get_track, register_track
from fingerprint import fingerprint

app = FastAPI(title="Music AI Solutions API")


@app.get("/")
def read_root():
    return {"message": "Music AI Solutions API"}


@app.post("/tracks")
async def create_track(
    title: str = Form(...),
    artist: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a track, fingerprint it and register it. Returns the record and
    any already-registered tracks with a similar fingerprint."""
    data = await file.read()
    try:
        fp = fingerprint(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    similar = find_similar(fp)
    record = register_track(title, artist, fp)
    return {"track": record.to_dict(), "similar": similar}


@app.get("/tracks/{track_id}")
def read_track(track_id: str):
    record = get_track(track_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return record.to_dict()


@app.get("/tracks/{track_id}/certificate")
def read_certificate(track_id: str):
    record = get_track(track_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return Response(
        generate_certificate(record),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="certificate-{track_id}.pdf"'},
    )
