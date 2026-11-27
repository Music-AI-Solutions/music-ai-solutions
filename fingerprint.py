"""Audio fingerprinting.

Turns a track into a set of landmark hashes: spectral peaks are picked from a
spectrogram and paired with the peaks that follow them. The hashes ignore where
a pair happens in the track, so the same audio gives the same fingerprint, and
two similar tracks share many hashes.

WAV files are read with the standard library. Other formats (mp3, flac, ...)
are decoded with librosa when it is installed.
"""
import hashlib
import io
import wave
from math import gcd

import numpy as np
from scipy.ndimage import maximum_filter
from scipy.signal import resample_poly, spectrogram

TARGET_SR = 11025
PEAK_NEIGHBORHOOD = (20, 20)  # (frequency bins, time frames)
FAN_OUT = 5
MAX_PAIR_FRAMES = 64
PEAK_FLOOR = 0.4  # a peak must reach this fraction of the loudest peak (log scale)


def load_audio(data: bytes):
    """Decode audio bytes to a mono float array at TARGET_SR."""
    try:
        with wave.open(io.BytesIO(data)) as w:
            channels, width, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
            raw = w.readframes(w.getnframes())
        dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(width)
        if dtype is None:
            raise ValueError("unsupported WAV sample width")
        y = np.frombuffer(raw, dtype=dtype).astype(np.float32)
        if width == 1:
            y = y - 128.0
        y /= float(2 ** (8 * width - 1)) if width > 1 else 128.0
        y = y.reshape(-1, channels).mean(axis=1)
    except (wave.Error, EOFError, ValueError):
        try:
            import librosa
        except ImportError as exc:
            raise ValueError("Not a readable WAV file and librosa is not installed") from exc
        y, sr = librosa.load(io.BytesIO(data), sr=None, mono=True)
    if sr != TARGET_SR:
        g = gcd(int(sr), TARGET_SR)
        y = resample_poly(y, TARGET_SR // g, int(sr) // g)
    return np.asarray(y, dtype=np.float32), TARGET_SR


def _peaks(y: np.ndarray, sr: int):
    _, _, s = spectrogram(y, fs=sr, nperseg=1024, noverlap=512)
    s = np.log1p(s)
    # Keep only prominent peaks so background noise does not change the hashes.
    is_peak = (s == maximum_filter(s, size=PEAK_NEIGHBORHOOD)) & (s > PEAK_FLOOR * s.max())
    freq_idx, time_idx = np.nonzero(is_peak)
    order = np.argsort(time_idx, kind="stable")
    return list(zip(time_idx[order].tolist(), freq_idx[order].tolist()))


def fingerprint(data: bytes) -> dict:
    """Return the sha256 of the file, the landmark hashes and a fingerprint id."""
    y, sr = load_audio(data)
    if len(y) < sr:  # under one second
        raise ValueError("Audio is too short to fingerprint")
    peaks = _peaks(y, sr)
    hashes = set()
    for i, (t1, f1) in enumerate(peaks):
        for t2, f2 in peaks[i + 1 : i + 1 + FAN_OUT]:
            dt = t2 - t1
            if 0 < dt <= MAX_PAIR_FRAMES:
                hashes.add(hashlib.sha1(f"{f1}|{f2}|{dt}".encode()).hexdigest()[:12])
    if not hashes:
        raise ValueError("No fingerprint could be extracted from this audio")
    ordered = sorted(hashes)
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "fingerprint_id": hashlib.sha256("\n".join(ordered).encode()).hexdigest(),
        "hashes": ordered,
        "duration_s": round(len(y) / sr, 2),
    }


def similarity(a, b) -> float:
    """Jaccard similarity between two hash collections, from 0 to 1."""
    a, b = set(a), set(b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
