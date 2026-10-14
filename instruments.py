# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Wspólna tabela instrumentów dla CLI, GUI i kompozytora."""

INSTRUMENTS = {
    "PIANO": 0,
    "BRIGHT_PIANO": 1,
    "HARPSICHORD": 6,
    "ORGAN": 19,
    "GUITAR": 29,
    "DISTORTION": 30,
    "BASS": 33,
    "STRINGS": 48,
    "SLOW_STRINGS": 49,
    "CHOIR": 52,
    "VOICE": 53,
    "TRUMPET": 56,
    "BRASS": 61,
    "SAX": 65,
    "OBOE": 68,
    "FLUTE": 73,
    "PAD": 89,
    "SCIFI": 96,
    "SITAR": 104,
}

# Nazwy z pomocy CLI i ze starszego GUI.
ALIASES = {
    "DIST_GUITAR": "DISTORTION",
    "DISTORTED_GUITAR": "DISTORTION",
    "SYNTH": "PAD",
    "SYNTHESIZER": "PAD",
    "HARPSI": "HARPSICHORD",
}


def normalize_instrument(name: str) -> str:
    """Zwraca kanoniczną nazwę albo rzuca ValueError."""
    if name is None:
        raise ValueError("Brak nazwy instrumentu.")
    key = str(name).strip().upper().replace("-", "_").replace(" ", "_")
    key = ALIASES.get(key, key)
    if key not in INSTRUMENTS:
        known = ", ".join(sorted(set(INSTRUMENTS) | set(ALIASES)))
        raise ValueError(f"Nieznany instrument: {name}. Dostępne: {known}")
    return key


def midi_program(name: str) -> int:
    """Numer programu General MIDI dla nazwy lub aliasu."""
    return INSTRUMENTS[normalize_instrument(name)]


def list_instrument_names() -> list:
    """Nazwy kanoniczne i aliasy, do pomocy i listy w GUI."""
    return sorted(set(INSTRUMENTS) | set(ALIASES))
