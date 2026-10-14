# soul_composer_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
Kompozytor Duszowy EriAmo v5.9.2
Orkiestracja. Generatory: composer_menuet, composer_genres. Zapis: composer_score.
"""
import datetime
import os
import random

import numpy as np

from amocore_v59 import (
    AXES_LIST,
    compute_curiosity_from_soul,
    get_curiosity_engine,
    get_music_memory,
    interpret_improv_for_composition,
)
from composer_genres import GenreMixin
from composer_menuet import MenuetMixin
from composer_runtime import AUDIO_AVAIL, MUSIC21_AVAIL, PYDUB_AVAIL
from composer_score import ScoreMixin
from genre_definitions import GENRE_DEFINITIONS, list_genres
from instruments import normalize_instrument

if not MUSIC21_AVAIL:
    print("[COMPOSER] Music21 niedostępne - tylko eksport tekstowy")
if not AUDIO_AVAIL:
    print("[COMPOSER] Brak midi2audio - zostaje sam zapis MIDI")
elif not PYDUB_AVAIL:
    print("[COMPOSER] Brak pydub - zostaje WAV, bez OGG/FLAC")


class SoulComposerV59(MenuetMixin, GenreMixin, ScoreMixin):
    OUTPUT_DIR = "compositions"

    CHORD_MAP = {
        "maj": [0, 4, 7],
        "min": [0, 3, 7],
        "7": [0, 4, 7, 10],
        "dim": [0, 3, 6],
        "power": [0, 7, 12],
        "sus4": [0, 5, 7],
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
    }

    TONIC_MAP = {
        "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
        "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
        "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71,
    }

    def __init__(self, core, logger):
        self.core = core
        self.logger = logger
        self._slur_start = None
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        self.AXES_MAP = {axis: i for i, axis in enumerate(AXES_LIST)}

    def _get_soul_metrics(self) -> dict:
        """Metryki duszy, styl z pamięci i aktualna ciekawość."""
        soul = self.core.get_vector_copy()
        improv_value = soul[self.AXES_MAP["improwizacja"]]
        improv_params = interpret_improv_for_composition(improv_value)

        try:
            memory = get_music_memory()
            recent_weight = 0.3 + (improv_value / 100.0) * 0.3
            recent_weight = max(0.0, min(1.0, recent_weight))
            memory_style = memory.get_blended_style(recent_weight)
            memory_status = memory.get_status()
        except Exception:
            memory_style = {}
            memory_status = {}

        curiosity = compute_curiosity_from_soul(self.core)
        return {
            "logika": soul[self.AXES_MAP["logika"]],
            "emocje": soul[self.AXES_MAP["emocje"]],
            "affections": soul[self.AXES_MAP["affections"]],
            "wiedza": soul[self.AXES_MAP["wiedza"]],
            "czas": soul[self.AXES_MAP["czas"]],
            "kreacja": soul[self.AXES_MAP["kreacja"]],
            "przestrzen": soul[self.AXES_MAP["przestrzen"]],
            "improwizacja": improv_value,
            "improv_params": improv_params,
            "byt": soul[self.AXES_MAP["byt"]],
            "memory_style": memory_style,
            "memory_status": memory_status,
            "curiosity": curiosity,
        }

    def _get_rhythm_duration(self, metrics: dict, base_tempo_mod: float = 0.0) -> float:
        time_val = metrics["czas"] + base_tempo_mod
        style = metrics.get("memory_style") or {}
        if style.get("has_data"):
            density = float(style.get("note_density", 0.5))
            if density >= 0.66:
                time_val += 12
            elif density <= 0.34:
                time_val -= 12
        opts_fast = [0.25, 0.5, 0.5, 1.0]
        opts_med = [0.5, 1.0, 1.0, 2.0]
        opts_slow = [1.0, 2.0, 4.0]

        if time_val > 10.0:
            return random.choice(opts_fast)
        elif time_val > 0.0:
            return random.choice(opts_fast) if random.random() < (time_val / 15.0) else random.choice(opts_med)
        elif time_val < -10.0:
            return random.choice(opts_slow)
        return random.choice(opts_med)

    def _build_chord_notes(self, root: int, chord_type: str) -> list:
        intervals = self.CHORD_MAP.get(chord_type, [0, 4, 7])
        return [root + i for i in intervals]

    def _resolve_tonic(self, fallback_midi: int, style: dict):
        """Tonika w oktawie fallbacku i flaga moll. Pusta pamięć zostawia fallback."""
        fallback_midi = int(fallback_midi)
        if not style or not style.get("has_data"):
            return fallback_midi, False
        learned_pc = int(round(float(style.get("key_tonic", 0.0)) * 11)) % 12
        tonic = (fallback_midi // 12) * 12 + learned_pc
        is_minor = float(style.get("key_mode", 1.0)) < 0.5
        return tonic, is_minor

    def _key_shift(self, style: dict, home_pc: int) -> int:
        """Przesunięcie z tonacji domowej do wyuczonej. Pusta pamięć daje 0."""
        if not style or not style.get("has_data"):
            return 0
        learned_pc = int(round(float(style.get("key_tonic", 0.0)) * 11)) % 12
        return (learned_pc - int(home_pc)) % 12

    def _clamp_pitch(self, pitch: int) -> int:
        return max(0, min(127, int(pitch)))

    def _shift_pitch(self, pitch, shift: int):
        if isinstance(pitch, (list, tuple)):
            return [self._clamp_pitch(p + shift) for p in pitch]
        return self._clamp_pitch(int(pitch) + shift)

    def _shift_event(self, event: dict, shift: int) -> dict:
        if not shift or event.get("type") == "rest":
            return event
        copied = dict(event)
        copied["pitch"] = self._shift_pitch(event["pitch"], shift)
        return copied

    def _shift_measures(self, measures, shift: int):
        if not shift:
            return measures
        return [[self._shift_event(ev, shift) for ev in measure] for measure in measures]

    def _syncopate_measure(self, measure):
        """Pauza 0.5 na początku i skrócenie pierwszego dźwięku o tyle samo."""
        index = None
        for i, ev in enumerate(measure):
            if ev.get("type") != "rest" and float(ev.get("duration", 0)) > 0.5:
                index = i
                break
        if index is None:
            return measure
        out = []
        for i, ev in enumerate(measure):
            if i == index:
                out.append({"type": "rest", "duration": 0.5, "dynamic": ev.get("dynamic", "mf")})
                shortened = dict(ev)
                shortened["duration"] = float(ev["duration"]) - 0.5
                out.append(shortened)
            else:
                out.append(ev)
        return out

    def _maybe_syncopate(self, measures, style):
        if not style or not style.get("has_data"):
            return measures
        if float(style.get("syncopation_feel", 0)) < 0.45:
            return measures
        return [self._syncopate_measure(m) for m in measures]

    def _densify_measures(self, measures, style):
        """Gęsty plik dzieli długie nuty, rzadki łączy je parami. Długość taktu zostaje."""
        if not style or not style.get("has_data"):
            return measures
        density = float(style.get("note_density", 0.5))
        if density >= 0.66:
            return [self._split_long_notes(m) for m in measures]
        if density <= 0.34:
            return [self._merge_note_pairs(m) for m in measures]
        return measures

    def _split_long_notes(self, measure):
        out = []
        for ev in measure:
            dur = float(ev.get("duration", 0))
            if ev.get("type") == "note" and dur >= 1.0:
                half = dur / 2.0
                out.append({**ev, "duration": half})
                out.append({**ev, "duration": half})
            else:
                out.append(ev)
        return out

    def _merge_note_pairs(self, measure):
        out = []
        i = 0
        while i < len(measure):
            ev = measure[i]
            nxt = measure[i + 1] if i + 1 < len(measure) else None
            if ev.get("type") == "note" and nxt and nxt.get("type") == "note":
                merged = dict(ev)
                merged["duration"] = float(ev["duration"]) + float(nxt["duration"])
                out.append(merged)
                i += 2
            else:
                out.append(ev)
                i += 1
        return out

    def _recolor_minor(self, measures):
        """W C zamienia tercję wielką i leading tone na odmianę molową."""
        out = []
        for measure in measures:
            bar = []
            for ev in measure:
                copied = dict(ev)
                pitch = copied.get("pitch")
                if isinstance(pitch, int):
                    if pitch % 12 in (4, 11):
                        copied["pitch"] = pitch - 1
                elif isinstance(pitch, list):
                    copied["pitch"] = [p - 1 if p % 12 in (4, 11) else p for p in pitch]
                bar.append(copied)
            out.append(bar)
        return out

    def _apply_learned_key(self, melody, harmony, style, home_pc: int):
        """Synkopa melodii, potem to samo przesunięcie obu głosów."""
        melody = self._maybe_syncopate(melody, style)
        shift = self._key_shift(style, home_pc)
        return self._shift_measures(melody, shift), self._shift_measures(harmony, shift)

    def _apply_intention_vector(self, genre_name: str) -> np.ndarray:
        if genre_name not in GENRE_DEFINITIONS:
            return np.zeros(len(AXES_LIST))
        f_def = GENRE_DEFINITIONS[genre_name]["f_intencja_wektor"]
        f_int = np.zeros(len(AXES_LIST))
        for axis, val in f_def.items():
            if axis in self.AXES_MAP:
                f_int[self.AXES_MAP[axis]] = float(val)
        for i, val in enumerate(f_int):
            if val != 0:
                self.core.shift_axis(AXES_LIST[i], "INCREMENT", val)
        return f_int

    def _normalize_request(self, genre_name: str, instrument_override):
        if genre_name is None or not str(genre_name).strip():
            raise ValueError("Podaj nazwę gatunku.")
        genre_name = str(genre_name).upper().strip()
        if genre_name not in GENRE_DEFINITIONS:
            known = ", ".join(sorted(GENRE_DEFINITIONS))
            raise ValueError(f"Nieznany gatunek: {genre_name}. Dostępne: {known}")
        if instrument_override is not None and str(instrument_override).strip():
            if str(instrument_override).strip().upper() == "AUTO":
                instrument_override = None
            else:
                instrument_override = normalize_instrument(instrument_override)
        else:
            instrument_override = None
        return genre_name, instrument_override

    def compose_new_work(self, genre_name: str, instrument_override: str = None, tonic: str = None) -> dict:
        """
        Komponuje nowy utwór.

        Nieznany gatunek i nieznany instrument kończą się ValueError,
        zanim dusza albo pliki zostaną zmienione.
        """
        genre_name, instrument_override = self._normalize_request(genre_name, instrument_override)

        curiosity_before = compute_curiosity_from_soul(self.core)
        recommendation = curiosity_before.get("recommendation", {})
        if recommendation.get("action") in ("EXPLORE", "REVOLUTIONIZE"):
            suggestion = get_curiosity_engine().suggest_new_genre(genre_name, list_genres())
            self.core.log(
                f"[CIEKAWOŚĆ] {curiosity_before.get('description', '')}. "
                f"{recommendation.get('message', '')} Propozycja: {suggestion}.",
                "YELLOW",
            )

        self.core.apply_time_based_decay()
        f_intencja = self._apply_intention_vector(genre_name)

        if genre_name == "POWER_METAL":
            data = self._generate_power_metal()
        elif genre_name == "HEAVY_METAL":
            data = self._generate_heavy_metal()
        elif genre_name == "BLUES":
            data = self._generate_blues_polyphonic()
        elif genre_name == "ROCK_AND_ROLL":
            data = self._generate_rock_polyphonic()
        elif genre_name == "MENUET":
            tonic_midi = 60
            if tonic:
                tonic_midi = self.TONIC_MAP.get(tonic.upper().strip(), 60)
            if tonic and tonic.upper() == "RIEPEL":
                data = self._generate_menuet_polyphonic(tonic=60)
            else:
                data = self._generate_menuet_mozart_dice(tonic=tonic_midi)
        elif genre_name == "WALC":
            data = self._generate_waltz()
        elif genre_name == "KANON":
            data = self._generate_canon()
        elif genre_name == "LAMENT":
            data = self._generate_lament_polyphonic()
        elif genre_name == "AMBIENT":
            data = self._generate_ambient_polyphonic()
        else:
            data = self._generate_simple_poly(genre_name)

        score = self._create_music21_score(data, genre_name, instrument_override)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tonic_suffix = f"_{tonic}" if tonic and genre_name == "MENUET" else ""
        base = f"{self.OUTPUT_DIR}/{genre_name}{tonic_suffix}_{timestamp}"
        paths = {"midi": None, "xml": None, "txt": None}

        if score:
            paths["midi"] = f"{base}.mid"
            score.write("midi", fp=paths["midi"])
            paths["xml"] = f"{base}.musicxml"
            score.write("musicxml", fp=paths["xml"])
            if AUDIO_AVAIL:
                paths.update(self._render_audio(paths["midi"]))

        paths["txt"] = f"{base}.txt"
        with open(paths["txt"], "w", encoding="utf-8") as handle:
            handle.write(f"Gatunek: {genre_name}\n")
            if tonic and genre_name == "MENUET":
                handle.write(f"Tonacja: {tonic}-dur\n")
            handle.write(f"Instrument: {instrument_override if instrument_override else 'Auto'}\n")
            handle.write(f"Data: {datetime.datetime.now().isoformat()}\n\n")
            if genre_name == "MENUET":
                handle.write("STRUKTURA (Riepel):\n------------------------------\n")
                handle.write("  Część A (Satz):\n")
                handle.write("    t.1-4: Vordersatz → półkadencja (V)\n")
                handle.write("    t.5-8: Nachsatz → pełna kadencja (I)\n")
                handle.write("  Część B (Fortspinnung + Rückgang):\n")
                handle.write("    t.9-12: Fortspinnung (rozwinięcie)\n")
                handle.write("    t.13-16: Rückgang → kadencja końcowa\n")
                handle.write("  Forma: :||: A :||: B :||\n\n")
            elif genre_name == "WALC":
                handle.write("STRUKTURA (8+8):\n------------------------------\n")
                handle.write("  t.1-8: fraza pierwsza, t.8 półkadencja (V)\n")
                handle.write("  t.9-16: fraza druga, t.16 kadencja (I)\n")
                handle.write("  Metrum: 3/4\n\n")
            elif genre_name == "KANON":
                handle.write("STRUKTURA:\n------------------------------\n")
                handle.write("  Kanon w oktawie. Drugi głos wchodzi po 2 taktach.\n\n")
            handle.write("STAN DUSZY:\n------------------------------\n")
            soul = self.core.get_vector_copy()
            for i, axis in enumerate(AXES_LIST):
                handle.write(f"  {axis.capitalize():12}: {soul[i]:+6.2f}\n")
            if paths.get("ogg"):
                handle.write(f"\nAudio: Wygenerowano OGG ({os.path.basename(paths['ogg'])})\n")
            elif paths.get("wav"):
                handle.write(f"\nAudio: Wygenerowano WAV ({os.path.basename(paths['wav'])})\n")

        self.logger.log_state(
            self.core, f_intencja, 1.0, f"Kompozycja {genre_name}", "COMPOSE", "!compose"
        )
        get_curiosity_engine().register_composition(
            genre_name,
            was_novel=bool(recommendation.get("novelty_seeking")),
        )
        return paths
