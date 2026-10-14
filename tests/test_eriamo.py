# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Testy bez renderu audio: osie, instrumenty, zanik, gatunki, kosinus."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import amocore_v59
from amocore_v59 import AXES_LIST, EriAmoCore
from authorship_reporter_v59 import cosine_similarity
from genre_definitions import GENRE_DEFINITIONS
from instruments import list_instrument_names, midi_program, normalize_instrument
from session import EriAmoSession
from soundfont import resolve_soundfont


class CatalogTests(unittest.TestCase):
    def test_genre_axes_are_real_axes(self):
        self.assertIn("POWER_METAL", GENRE_DEFINITIONS)
        self.assertIn("HEAVY_METAL", GENRE_DEFINITIONS)
        for name, data in GENRE_DEFINITIONS.items():
            for axis in data["f_intencja_wektor"]:
                self.assertIn(axis, AXES_LIST, f"{name} używa nieistniejącej osi {axis}")
        self.assertNotIn("etyka", AXES_LIST)

    def test_instrument_aliases(self):
        self.assertEqual(midi_program("DIST_GUITAR"), 30)
        self.assertEqual(midi_program("synth"), midi_program("PAD"))
        self.assertEqual(normalize_instrument("distortion"), "DISTORTION")
        self.assertIn("SYNTH", list_instrument_names())
        with self.assertRaises(ValueError):
            normalize_instrument("BANJO")

    def test_cosine_similarity(self):
        same = np.array([1.0, 0.0, 0.0])
        self.assertAlmostEqual(cosine_similarity(same, same), 1.0)
        self.assertAlmostEqual(cosine_similarity(same, np.array([-1.0, 0.0, 0.0])), -1.0)
        self.assertEqual(cosine_similarity(np.zeros(3), same), 0.0)

    def test_soundfont_env_wins(self):
        previous = os.environ.get("ERIAMO_SOUNDFONT")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "bank.sf2")
            with open(path, "wb") as handle:
                handle.write(b"0" * 1200)
            os.environ["ERIAMO_SOUNDFONT"] = path
            try:
                self.assertEqual(resolve_soundfont(), os.path.abspath(path))
            finally:
                if previous is None:
                    os.environ.pop("ERIAMO_SOUNDFONT", None)
                else:
                    os.environ["ERIAMO_SOUNDFONT"] = previous


class DiskTests(unittest.TestCase):
    def setUp(self):
        self._old = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)
        amocore_v59.shutdown_music_memory()
        amocore_v59._music_memory = None
        amocore_v59._curiosity_engine = None

    def tearDown(self):
        amocore_v59.shutdown_music_memory()
        if amocore_v59._music_memory is not None:
            amocore_v59._music_memory.running = False
        amocore_v59._music_memory = None
        amocore_v59._curiosity_engine = None
        os.chdir(self._old)
        self._tmp.cleanup()

    def test_decay_is_reloaded_from_history(self):
        session = EriAmoSession()
        session.core.shift_axis("emocje", "SET", 20.0)
        session.core.shift_axis("czas", "SET", -8.0)
        _before, after = session.decay(4)
        emocje = AXES_LIST.index("emocje")
        czas = AXES_LIST.index("czas")
        self.assertLess(abs(after[emocje]), 20.0)
        self.assertLess(abs(after[czas]), 8.0)
        reborn = EriAmoCore()
        np.testing.assert_allclose(reborn.get_vector_copy(), after)
        history = Path("data/soul_history.csv").read_text(encoding="utf-8")
        self.assertIn("!decay", history)

    def test_unknown_genre_and_instrument_do_not_move_the_soul(self):
        session = EriAmoSession()
        original = session.core.get_vector_copy().copy()
        with self.assertRaises(ValueError):
            session.compose("NIE_MA_TAKIEGO")
        np.testing.assert_allclose(session.core.get_vector_copy(), original)
        with self.assertRaises(ValueError):
            session.compose("BLUES", instrument="BANJO")
        np.testing.assert_allclose(session.core.get_vector_copy(), original)

    def test_alias_compose_and_curiosity_registration(self):
        session = EriAmoSession()
        paths = session.compose("blues", instrument="DIST_GUITAR")
        text = Path(paths["txt"]).read_text(encoding="utf-8")
        self.assertIn("DISTORTION", text)
        self.assertIn("BLUES", text)
        engine = amocore_v59.get_curiosity_engine()
        self.assertEqual(engine.boredom_counter.get("BLUES"), 1)
        self.assertTrue(Path(paths["txt"]).is_file())

    def test_metal_generators_write_a_score(self):
        session = EriAmoSession()
        for genre in ("POWER_METAL", "HEAVY_METAL", "MENUET"):
            paths = session.compose(genre)
            self.assertTrue(Path(paths["txt"]).is_file(), genre)
            if paths.get("midi"):
                self.assertGreater(Path(paths["midi"]).stat().st_size, 0, genre)

    def test_file_learning_reaches_sleep_memory(self):
        from music21 import note, stream

        score = stream.Stream()
        for pitch in (60, 62, 64, 65, 67, 69, 71, 72, 71, 69):
            score.append(note.Note(pitch, quarterLength=1.0))
        midi_path = os.path.join(self._tmp.name, "tiny.mid")
        score.write("midi", fp=midi_path)

        session = EriAmoSession()
        _features, learned = session.learn_file(midi_path)
        self.assertTrue(learned)
        memory = amocore_v59.get_music_memory()
        self.assertGreaterEqual(len(memory.H_log), 1)

    def test_waltz_meter_and_menuet_form(self):
        import music21

        session = EriAmoSession()
        waltz = session.compose("WALC")
        score = music21.converter.parse(waltz["xml"])
        signatures = list(score.parts[0].recurse().getElementsByClass(music21.meter.TimeSignature))
        self.assertEqual(signatures[0].ratioString, "3/4")
        rh = list(score.parts[0].getElementsByClass(music21.stream.Measure))
        lh = list(score.parts[1].getElementsByClass(music21.stream.Measure))
        self.assertEqual(len(rh), 16)
        self.assertEqual(len(lh), 16)
        for part_measures in (rh, lh):
            for measure in part_measures:
                total = sum(float(el.quarterLength) for el in measure.notesAndRests)
                self.assertAlmostEqual(total, 3.0, places=2)
        self.assertEqual(self._first_note(lh[7]), 43)
        self.assertEqual(self._last_note(rh[7]), 67)
        self.assertEqual(self._first_note(lh[15]), 36)
        self.assertEqual(self._last_note(rh[15]), 60)
        waltz_text = Path(waltz["txt"]).read_text(encoding="utf-8")
        self.assertIn("półkadencja", waltz_text)

        menuet = session.compose("MENUET")
        written = music21.converter.parse(menuet["xml"])
        measures = list(written.parts[0].getElementsByClass(music21.stream.Measure))
        self.assertEqual(len(measures), 16)
        self.assertEqual(measures[7].rightBarline.direction, "end")
        self.assertEqual(measures[15].rightBarline.direction, "end")
        sounding = music21.converter.parse(menuet["midi"])
        self.assertEqual(len(list(sounding.parts[0].getElementsByClass(music21.stream.Measure))), 32)

    def _first_note(self, measure):
        for element in measure.notesAndRests:
            if element.isNote:
                return element.pitch.midi
        self.fail("brak nuty")

    def _last_note(self, measure):
        last = None
        for element in measure.notesAndRests:
            if element.isNote:
                last = element.pitch.midi
        self.assertIsNotNone(last)
        return last

    def _write_pitches(self, pitches, name):
        from music21 import note, stream, tempo

        score = stream.Stream()
        score.append(tempo.MetronomeMark(number=120))
        for pitch in pitches:
            score.append(note.Note(pitch, quarterLength=1.0))
        path = os.path.join(self._tmp.name, name)
        score.write("midi", fp=path)
        return path

    def _g_major_line(self):
        phrase = [67, 69, 71, 74, 72, 71, 69, 67]
        return phrase * 8

    def test_learning_changes_tonic_leaps_and_soul(self):
        session = EriAmoSession()
        composer = session.composer
        empty = amocore_v59.get_music_memory().get_blended_style()
        self.assertFalse(empty.get("has_data"))
        self.assertNotIn("key_tonic", empty)
        self.assertEqual(composer._resolve_tonic(60, empty), (60, False))
        self.assertEqual(composer._key_shift({"has_data": False, "key_tonic": 0.5}, 0), 0)
        learned_c = {"has_data": True, "key_tonic": 0.0, "key_mode": 1.0}
        self.assertEqual(composer._resolve_tonic(60, learned_c), (60, False))

        g_path = self._write_pitches(self._g_major_line(), "gmaj.mid")
        _features, learned = session.learn_file(g_path)
        self.assertTrue(learned)
        style = amocore_v59.get_music_memory().get_blended_style()
        self.assertEqual(int(round(style["key_tonic"] * 11)) % 12, 7)
        self.assertGreaterEqual(style["key_mode"], 0.5)
        self.assertLess(style["leap_ratio"], 0.25)
        tonic, is_minor = composer._resolve_tonic(60, style)
        self.assertEqual(tonic % 12, 7)
        self.assertFalse(is_minor)
        history = Path("data/soul_history.csv").read_text(encoding="utf-8")
        self.assertIn("gmaj.mid", history)

        old_memory = amocore_v59._music_memory
        if old_memory is not None:
            old_memory.running = False
        amocore_v59._music_memory = None
        for name in ("data/music_experience.json", "data/music_patterns.json"):
            if os.path.exists(name):
                os.remove(name)
        leap_path = self._write_pitches([60, 72] * 8, "leaps.mid")
        session.learn_file(leap_path)
        leaps = amocore_v59.get_music_memory().get_blended_style()
        self.assertGreater(leaps["leap_ratio"], 0.7)

    def test_shutdown_consolidates_tonal_pattern(self):
        session = EriAmoSession()
        session.learn_file(self._write_pitches(self._g_major_line(), "gmaj.mid"))
        memory = amocore_v59.get_music_memory()
        self.assertEqual(len(memory.D_Map), 0)
        self.assertGreater(memory.experiences_since_sleep, 0)
        memory.shutdown()
        self.assertGreater(len(memory.D_Map), 0)
        self.assertTrue(any("ton:7M" in key for key in memory.D_Map))

    def test_event_ids_continue_without_rereading(self):
        session = EriAmoSession()
        session.decay(1)
        session.decay(1)
        other = amocore_v59.SoulStateLogger()
        self.assertEqual(other.event_counter, session.logger.event_counter)
        self.assertGreaterEqual(other.event_counter, 2)

    def test_canon_imitates_at_the_octave(self):
        import music21

        session = EriAmoSession()
        paths = session.compose("KANON")
        score = music21.converter.parse(paths["xml"])
        signatures = list(score.parts[0].recurse().getElementsByClass(music21.meter.TimeSignature))
        self.assertEqual(signatures[0].ratioString, "4/4")
        rh = list(score.parts[0].getElementsByClass(music21.stream.Measure))
        lh = list(score.parts[1].getElementsByClass(music21.stream.Measure))
        self.assertEqual(len(rh), 10)
        self.assertEqual(len(lh), 10)
        for measure in rh + lh:
            total = sum(float(el.quarterLength) for el in measure.notesAndRests)
            self.assertAlmostEqual(total, 4.0, places=2)
        for index in (0, 1):
            self.assertTrue(all(el.isRest for el in lh[index].notesAndRests))
        for index in range(8):
            leader = [el for el in rh[index].notes if el.isNote]
            follower = [el for el in lh[index + 2].notes if el.isNote]
            self.assertEqual(len(leader), len(follower))
            self.assertGreater(len(leader), 0)
            for left, right in zip(leader, follower):
                self.assertEqual(right.pitch.midi, left.pitch.midi - 12)
                self.assertAlmostEqual(float(right.quarterLength), float(left.quarterLength))
        text = Path(paths["txt"]).read_text(encoding="utf-8")
        self.assertIn("oktawie", text)

    def _event_rows(self, data):
        rows = []
        for voice in ("melody", "harmony"):
            for measure in data[voice]:
                for ev in measure:
                    pitch = ev.get("pitch")
                    if isinstance(pitch, list):
                        pitch = tuple(pitch)
                    rows.append((ev.get("type"), pitch, float(ev.get("duration", 0))))
        return rows

    def test_learned_key_transposes_blues_metal_waltz_and_canon(self):
        import random

        session = EriAmoSession()
        composer = session.composer
        plain_style = {"has_data": False}
        learned = {
            "has_data": True,
            "key_tonic": 7 / 11.0,
            "key_mode": 1.0,
            "note_density": 0.5,
            "syncopation_feel": 0.0,
        }
        homes = {
            "_generate_blues_polyphonic": 0,
            "_generate_power_metal": 4,
            "_generate_heavy_metal": 4,
            "_generate_waltz": 0,
            "_generate_canon": 0,
        }
        original = composer._get_soul_metrics
        base = original()

        def using(style, base=base):
            metrics = dict(base)
            metrics["memory_style"] = dict(style)
            return metrics

        try:
            for name, home in homes.items():
                shift = (7 - home) % 12
                random.seed(3)
                composer._get_soul_metrics = lambda style=plain_style: using(style)
                plain = getattr(composer, name)()
                random.seed(3)
                composer._get_soul_metrics = lambda style=learned: using(style)
                moved = getattr(composer, name)()
                left = self._event_rows(plain)
                right = self._event_rows(moved)
                self.assertEqual(len(left), len(right), name)
                for before, after in zip(left, right):
                    self.assertEqual(before[0], after[0], name)
                    self.assertAlmostEqual(before[2], after[2], places=5, msg=name)
                    if before[1] is None or before[0] == "rest":
                        self.assertEqual(before[1], after[1], name)
                    elif isinstance(before[1], tuple):
                        self.assertEqual(after[1], tuple(p + shift for p in before[1]), name)
                    else:
                        self.assertEqual(after[1], before[1] + shift, name)
            minor = {
                "has_data": True,
                "key_tonic": 0.0,
                "key_mode": 0.0,
                "note_density": 0.5,
                "syncopation_feel": 0.0,
            }
            composer._get_soul_metrics = lambda: using(minor)
            waltz = composer._generate_waltz()
            self.assertEqual(waltz["harmony"][0][1]["pitch"], [48, 51, 55])
            self.assertEqual(waltz["harmony"][1][1]["pitch"], [53, 56, 60])
            self.assertEqual(waltz["harmony"][3][1]["pitch"], [55, 59, 62])

            syncopated = {
                "has_data": True,
                "key_tonic": 0.0,
                "key_mode": 1.0,
                "note_density": 0.5,
                "syncopation_feel": 0.9,
            }
            composer._get_soul_metrics = lambda: using(syncopated)
            waltz = composer._generate_waltz()
            self.assertEqual(waltz["melody"][7][0]["type"], "rest")
            self.assertAlmostEqual(waltz["melody"][7][0]["duration"], 0.5)
            self.assertEqual(waltz["melody"][7][-1]["pitch"], 67)
            self.assertAlmostEqual(sum(ev["duration"] for ev in waltz["melody"][7]), 3.0)
        finally:
            composer._get_soul_metrics = original

    def test_memory_dump_returns(self):
        core = EriAmoCore()
        path = core.create_memory_dump("test.soul")
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(core.load_memory_dump(path))


if __name__ == "__main__":
    unittest.main()
