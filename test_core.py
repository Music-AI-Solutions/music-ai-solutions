"""Checks for the fingerprint, registry and certificate. Run: python test_core.py"""
import io
import os
import tempfile
import wave

import numpy as np

from certificate import generate_certificate
from database import find_similar, get_track, register_track
from fingerprint import fingerprint, similarity

SR = 22050


def make_wav(freqs, seconds_each=0.4, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(int(SR * seconds_each)) / SR
    # Plucked-style notes: a sharp onset that decays, like real instruments.
    y = np.concatenate([0.5 * np.exp(-6 * t) * np.sin(2 * np.pi * f * t) for f in freqs])
    y = y + noise * rng.standard_normal(len(y))
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


MELODY = [440, 554, 659, 880, 659, 554, 440, 330, 494, 587, 740, 988]
OTHER = [262, 311, 392, 466, 523, 622, 784, 932, 349, 415, 523, 698]


def main():
    a = fingerprint(make_wav(MELODY))
    assert fingerprint(make_wav(MELODY))["fingerprint_id"] == a["fingerprint_id"], "same audio, same id"
    noisy = fingerprint(make_wav(MELODY, noise=0.01, seed=1))
    other = fingerprint(make_wav(OTHER))
    s_noisy = similarity(a["hashes"], noisy["hashes"])
    s_other = similarity(a["hashes"], other["hashes"])
    print(f"noisy copy: {s_noisy:.2f}  different track: {s_other:.2f}")
    assert s_noisy > 0.5 > s_other + 0.2

    with tempfile.TemporaryDirectory() as d:
        db = os.path.join(d, "t.db")
        rec = register_track("Song A", "Artist A", a, path=db)
        assert get_track(rec.id, path=db).fingerprint_id == a["fingerprint_id"]
        hits = find_similar(noisy, path=db)
        assert hits and hits[0]["track"]["id"] == rec.id
        assert not find_similar(other, path=db)
        pdf = generate_certificate(rec)
        assert pdf.startswith(b"%PDF")

    try:
        fingerprint(make_wav([440], seconds_each=0.2))
    except ValueError:
        pass
    else:
        raise AssertionError("short audio should be rejected")
    print("all checks passed")


if __name__ == "__main__":
    main()
