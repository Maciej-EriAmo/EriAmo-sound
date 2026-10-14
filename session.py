# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Wspólne polecenia CLI i GUI."""
import os

from amocore_v59 import EriAmoCore, SoulStateLogger, learn_from_score, shutdown_music_memory
from authorship_reporter_v59 import AuthorshipReporter
from data_loader_v59 import ExternalKnowledgeLoader
from music_analyzer_v59 import MusicAnalyzer
from soul_composer_v59 import SoulComposerV59

PITCH_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


class EriAmoSession:
    def __init__(self):
        self.core = EriAmoCore()
        self.logger = SoulStateLogger()
        self.analyzer = MusicAnalyzer(self.core, self.logger)
        self.composer = SoulComposerV59(self.core, self.logger)
        self.loader = ExternalKnowledgeLoader()
        self.reporter = AuthorshipReporter()
        self._visualizer = None

    @property
    def visualizer(self):
        if self._visualizer is None:
            from visualizer_v59 import SoulVisualizerV59
            self._visualizer = SoulVisualizerV59()
        return self._visualizer

    def compose(self, genre: str, instrument: str = None, tonic: str = None) -> dict:
        return self.composer.compose_new_work(genre, instrument_override=instrument, tonic=tonic)

    def teach(self, features: list, title: str, mode: str = "!teach"):
        self.analyzer.analyze_and_shift(features, title, mode=mode)

    def learn_web(self, artist: str, title: str) -> list:
        features = self.loader.get_context_from_web(artist, title)
        if features:
            self.analyzer.analyze_and_shift(features, f"{artist} - {title}", mode="!teach")
        return features

    def learn_file(self, path: str):
        """Cechy ontologiczne oraz zapis wzorca do pamięci snu. Plik czyta raz."""
        if not os.path.isfile(path):
            self.core.log(f"[NUTY] Brak pliku: {path}", "RED")
            return [], False
        score = self.loader.open_score(path)
        if score is None:
            self.core.log(self._learning_line([], {}), "YELLOW")
            return [], False
        features = self.loader.features_from_score(score)
        if features:
            self.analyzer.analyze_and_shift(
                features, f"Plik: {os.path.basename(path)}", mode="!teach"
            )
        note_memory = learn_from_score(score, os.path.basename(path))
        self.core.log(self._learning_line(features, note_memory), "CYAN")
        return features, bool(note_memory)

    def _learning_line(self, features, note_memory) -> str:
        """Jedna linia: co weszło do duszy i co weszło do pamięci nut."""
        soul = ", ".join(features) if features else "brak nowych cech"
        if not note_memory:
            notes = "pominięta"
        else:
            pc = int(round(float(note_memory.get("key_tonic", 0)) * 11)) % 12
            name = PITCH_NAMES[pc]
            name += " moll" if float(note_memory.get("key_mode", 1)) < 0.5 else " dur"
            notes = (
                f"tonika {name}, skoki {float(note_memory.get('leap_ratio', 0)):.2f}, "
                f"gęstość {float(note_memory.get('note_density', 0)):.2f}, "
                f"synkopa {float(note_memory.get('syncopation_feel', 0)):.2f}"
            )
        return f"[NAUKA] Dusza: {soul}. Pamięć nut: {notes}."

    def decay(self, cycles: int = 1):
        """Wygasza osie efemeryczne i dopisuje stan do historii."""
        cycles = int(cycles)
        if cycles < 1:
            raise ValueError("Liczba cykli musi być dodatnia.")
        before = self.core.get_vector_copy()
        self.core.apply_emotion_decay(cycles)
        after = self.core.get_vector_copy()
        delta = after - before
        self.logger.log_state(
            self.core,
            delta,
            1.0,
            "Wygaszenie emocji",
            f"Decay x{cycles}",
            "!decay",
        )
        return before, after

    def shutdown(self):
        shutdown_music_memory()
