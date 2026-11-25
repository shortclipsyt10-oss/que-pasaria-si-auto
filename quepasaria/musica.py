"""Música de fondo generada por código (sin derechos de autor) y un 'whoosh' en cada cambio de escena."""
import numpy as np

PROGRESIONES = [
    [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]],
    [[62, 65, 69], [58, 62, 65], [60, 64, 67], [57, 60, 64]],
    [[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]],
    [[64, 67, 71], [60, 64, 67], [62, 65, 69], [59, 62, 67]],
    [[55, 59, 62], [52, 55, 59], [60, 64, 67], [62, 66, 69]],
]


def musica(ruta, total, cortes, semilla=0):
    import soundfile as sf
    rng = np.random.default_rng(semilla)
    chords = PROGRESIONES[semilla % len(PROGRESIONES)]
    bpm = [104, 110, 116, 120, 98][semilla % 5]
    sr = 44100; n = int(total * sr); out = np.zeros(n); beat = 60 / bpm

    def note(f): return 440 * 2 ** ((f - 69) / 12)

    def pluck(start, f, dur=0.5, amp=0.3):
        i = int(start * sr); L = int(dur * sr)
        if i >= n: return
        L = min(L, n - i); tt = np.arange(L) / sr
        out[i:i + L] += amp * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt) + 0.15 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7)

    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    b = 0
    while b * beat < total:
        ch = chords[(b // 8) % len(chords)]
        pluck(b * beat, note(ch[0] - 24), 0.9, 0.35)
        pluck(b * beat, note(ch[pat[b % 8]] + 12), 0.4, 0.18)
        pluck(b * beat + beat / 2, note(ch[pat[(b + 3) % 8]] + 12), 0.3, 0.1)
        i = int((b * beat + beat / 2) * sr); L = int(0.04 * sr)
        if i + L < n: out[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 120) * 0.05
        b += 1
    for x in cortes:
        i = int((x - 0.25) * sr); L = int(0.35 * sr)
        if i < 0 or i + L > n: continue
        nz = np.convolve(rng.standard_normal(L), np.ones(12) / 12, 'same')
        out[i:i + L] += nz * np.sin(np.linspace(0, np.pi, L)) ** 2 * 0.6
    out /= np.max(np.abs(out)) * 1.05
    sf.write(ruta, out, sr)
