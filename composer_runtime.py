# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Opcjonalne biblioteki nut i audio, współdzielone przez moduły kompozytora."""

try:
    import music21
    MUSIC21_AVAIL = True
except ImportError:
    music21 = None
    MUSIC21_AVAIL = False

try:
    from midi2audio import FluidSynth
except ImportError:
    FluidSynth = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

AUDIO_AVAIL = FluidSynth is not None
PYDUB_AVAIL = AudioSegment is not None
