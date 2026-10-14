# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Szukanie banku FluidR3_GM.sf2 niezależnie od systemu."""
import os


def project_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def assets_soundfont_path() -> str:
    return os.path.join(project_dir(), "assets", "FluidR3_GM.sf2")


def soundfont_missing_message() -> str:
    return (
        "[AUDIO] Brak SoundFontu FluidR3_GM.sf2. "
        "Uruchom: python download_soundfont.py "
        "albo ustaw zmienną ERIAMO_SOUNDFONT na pełną ścieżkę pliku .sf2. "
        "Audio (WAV/OGG/FLAC) pominięte. MIDI zostanie zapisane."
    )


def resolve_soundfont() -> str | None:
    """
    Kolejność: ERIAMO_SOUNDFONT, assets obok kodu, assets w katalogu roboczym,
    potem typowe ścieżki systemowe. Plik krótszy niż 1 KB jest traktowany jako uszkodzony.
    """
    candidates = []
    env_path = os.environ.get("ERIAMO_SOUNDFONT")
    if env_path:
        candidates.append(env_path)
    candidates.append(assets_soundfont_path())
    candidates.append(os.path.join("assets", "FluidR3_GM.sf2"))
    candidates.extend([
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/share/soundfonts/FluidR3_GM.sf2",
        os.path.expanduser("~/Library/Audio/Sounds/Banks/FluidR3_GM.sf2"),
    ])

    seen = set()
    for path in candidates:
        if not path:
            continue
        norm = os.path.abspath(path)
        if norm in seen:
            continue
        seen.add(norm)
        if os.path.isfile(norm) and os.path.getsize(norm) > 1000:
            return norm
    return None
