# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Testy bez renderu audio: osie, instrumenty, zanik, gatunki, kosinus."""
import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Kompozycje w testach nie renderują WAV. Bank ma 148 MB.
os.environ.setdefault("ERIAMO_SKIP_WAV", "1")

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
        self._old_home = os.environ.get("ERIAMO_HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["ERIAMO_HOME"] = self._tmp.name
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
        if self._old_home is None:
            os.environ.pop("ERIAMO_HOME", None)
        else:
            os.environ["ERIAMO_HOME"] = self._old_home
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

    def test_external_score_teaches_note_memory(self):
        import queue

        from main_gui_v59 import EriAmoBrain

        session = EriAmoSession()
        responses = queue.Queue()
        brain = EriAmoBrain(session, queue.Queue(), responses)
        path = self._write_pitches(self._g_major_line(), "external.mid")
        brain._handle_learn_file({"paths": [path]})
        learned = []
        while not responses.empty():
            learned.append(responses.get_nowait())
        self.assertTrue(any(item["status"] == "LOG" and "G dur" in item["msg"] for item in learned))
        style = amocore_v59.get_music_memory().get_blended_style()
        self.assertEqual(int(round(style["key_tonic"] * 11)) % 12, 7)

        brain._handle_learn_file({"paths": [os.path.join(self._tmp.name, "brak.mid")]})
        missed = []
        while not responses.empty():
            missed.append(responses.get_nowait())
        self.assertTrue(any(item["status"] == "ERROR" for item in missed))

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
            "note_density": 1.0,
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
                "note_density": 1.0,
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
                "note_density": 1.0,
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

    def test_broken_history_keeps_a_backup_and_the_earlier_rows(self):
        session = EriAmoSession()
        session.decay(1)
        path = Path("data/soul_history.csv")
        with path.open("a", encoding="utf-8") as handle:
            handle.write('2020-01-01,"unterminated\n')
        amocore_v59.SoulStateLogger()
        restored = path.read_text(encoding="utf-8")
        self.assertIn("!decay", restored)
        self.assertNotIn("unterminated", restored)
        backups = list(Path("data").glob("soul_history.csv.broken*"))
        self.assertEqual(len(backups), 1)
        self.assertIn("unterminated", backups[0].read_text(encoding="utf-8"))
        reborn = EriAmoCore()
        self.assertTrue(all(np.isfinite(reborn.get_vector_copy())))

    def test_blank_axis_does_not_become_the_soul(self):
        session = EriAmoSession()
        session.core.shift_axis("emocje", "SET", 6.0)
        session.decay(1)
        good = EriAmoCore().get_vector_copy().copy()
        path = Path("data/soul_history.csv")
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        emocje = rows[0].index("S_emocje")
        broken = list(rows[-1])
        broken[emocje] = ""
        with path.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(broken)
        reborn = EriAmoCore()
        np.testing.assert_allclose(reborn.get_vector_copy(), good)

    def test_incomplete_dump_does_not_replace_the_soul(self):
        core = EriAmoCore()
        core.shift_axis("emocje", "SET", 0.0)
        before = core.get_vector_copy().copy()
        path = os.path.join(self._tmp.name, "bad.soul")
        Path(path).write_text(json.dumps({"soul_vector": {"emocje": 12.5}, "meta": {}}), encoding="utf-8")
        self.assertFalse(core.load_memory_dump(path))
        np.testing.assert_allclose(core.get_vector_copy(), before)

    def test_sleep_does_not_reinforce_the_same_experience_twice(self):
        memory = amocore_v59.get_music_memory()
        memory.H_log = [{
            "features": {
                "repetition_density": 0.1,
                "leap_ratio": 0.1,
                "rhythmic_regularity": 0.8,
                "syncopation_feel": 0.0,
                "key_tonic": 0.0,
                "key_mode": 1.0,
            },
            "source": "t",
        }]
        memory.D_Map = {}
        memory._consolidated_index = 0
        memory.is_sleeping = False
        memory._consolidate_locked()
        weight = next(iter(memory.D_Map.values()))["weight"]
        memory._consolidate_locked()
        self.assertEqual(next(iter(memory.D_Map.values()))["weight"], weight)
        self.assertFalse(memory.is_sleeping)

    def test_dedup_keeps_weight_from_the_third_pattern(self):
        memory = amocore_v59.get_music_memory()
        memory.D_Map = {
            "rep:L|lea:L|rhy:L|syn:L|ton:0M": {"weight": 1.0, "features": {}},
            "rep:L|lea:M|rhy:L|syn:L|ton:0M": {"weight": 5.0, "features": {}},
            "rep:L|lea:H|rhy:L|syn:L|ton:0M": {"weight": 1.0, "features": {}},
        }
        memory._deduplicate_patterns()
        self.assertEqual(len(memory.D_Map), 1)
        self.assertAlmostEqual(next(iter(memory.D_Map.values()))["weight"], 6.0)

    def test_missing_reinforced_count_does_not_stick_the_sleep_flag(self):
        memory = amocore_v59.get_music_memory()
        experience = {
            "features": {
                "repetition_density": 1.0,
                "leap_ratio": 0.0,
                "rhythmic_regularity": 1.0,
                "syncopation_feel": 0.0,
                "key_tonic": 0.0,
                "key_mode": 1.0,
            },
            "source": "t",
        }
        key = memory._extract_pattern_key(experience)
        memory.D_Map = {key: {"weight": 1.0, "features": experience["features"]}}
        memory.H_log = [experience]
        memory._consolidated_index = 0
        memory.is_sleeping = False
        memory._consolidate_locked()
        self.assertFalse(memory.is_sleeping)
        self.assertEqual(memory.D_Map[key]["reinforced_count"], 1)

    def test_fuga_does_not_move_the_soul(self):
        session = EriAmoSession()
        original = session.core.get_vector_copy().copy()
        with self.assertRaises(ValueError):
            session.compose("FUGA")
        np.testing.assert_allclose(session.core.get_vector_copy(), original)
        history = Path("data/soul_history.csv").read_text(encoding="utf-8")
        self.assertNotIn("FUGA", history)

    def test_report_escapes_text_from_the_history(self):
        session = EriAmoSession()
        session.logger.log_state(
            session.core,
            session.core.get_vector_copy(),
            0.2,
            "raw &",
            "<b>xss</b>",
            "!teach",
        )
        path = session.visualizer.create_basic_report()
        page = Path(path).read_text(encoding="utf-8")
        self.assertIn("&lt;b&gt;xss&lt;/b&gt;", page)
        self.assertNotIn("<b>xss</b>", page)
        self.assertIn("raw &amp;", page)

    def test_data_stays_in_eriamo_home_when_cwd_changes(self):
        session = EriAmoSession()
        session.decay(1)
        elsewhere = tempfile.TemporaryDirectory()
        os.chdir(elsewhere.name)
        try:
            reborn = EriAmoCore()
            self.assertTrue(np.any(reborn.get_vector_copy() != 0) or Path(self._tmp.name, "data", "soul_history.csv").is_file())
            self.assertTrue(Path(self._tmp.name, "data", "soul_history.csv").is_file())
            self.assertFalse(Path(elsewhere.name, "data", "soul_history.csv").exists())
        finally:
            os.chdir(self._tmp.name)
            elsewhere.cleanup()


class LearningTests(unittest.TestCase):
    def test_windows_score_path_survives_the_command_split(self):
        from main_v59 import command_path, split_command

        parts = split_command(r"!file C:\Users\eriamo\score.mid")
        self.assertEqual(command_path(parts), r"C:\Users\eriamo\score.mid")
        spaced = split_command(r"!file C:\My Music\sonata.mid")
        self.assertEqual(command_path(spaced), r"C:\My Music\sonata.mid")
        quoted = split_command(r'!teach "Sonata C" MENUET KLASYCYZM')
        self.assertEqual(quoted, ["!teach", "Sonata C", "MENUET", "KLASYCYZM"])
        with self.assertRaises(ValueError):
            split_command('!teach "otwarte')

    def test_style_words_match_whole_words(self):
        from data_loader_v59 import ExternalKnowledgeLoader
        loader = ExternalKnowledgeLoader()
        self.assertNotIn("AMBIENT", loader._analyze_text_heuristics("Venom Black Metal"))
        self.assertNotIn("AMBIENT", loader._analyze_text_heuristics("tenor sax"))
        self.assertIn("AMBIENT", loader._analyze_text_heuristics("Brian Eno"))
        self.assertNotIn("PROG_ROCK", loader._analyze_text_heuristics("Yesterday"))
        self.assertIn("PROG_ROCK", loader._analyze_text_heuristics("Yes"))
        self.assertNotIn("RADOSC", loader._analyze_text_heuristics("Duran Duran"))
        self.assertIn("RADOSC", loader._analyze_text_heuristics("Sonata in C dur"))
        self.assertNotIn("HEAVY_METAL", loader._analyze_text_heuristics("acceptable"))
        self.assertIn("HEAVY_METAL", loader._analyze_text_heuristics("Accept"))

    def test_new_soul_has_no_discovery_penalty(self):
        engine = amocore_v59.CuriosityEngine()
        self.assertIsNone(engine.discovery_cooldown)
        self.assertEqual(engine._compute_discovery_penalty(), 0.0)
        engine.register_discovery()
        self.assertEqual(engine.discovery_cooldown, 0)
        self.assertEqual(engine._compute_discovery_penalty(), 20.0)

    def test_chords_are_not_melodic_leaps_and_quarters_are_not_presto(self):
        from music21 import chord, note, stream

        score = stream.Stream()
        for index, pitch in enumerate([60, 62, 64, 65, 67, 65, 64, 62]):
            score.insert(float(index), note.Note(pitch, quarterLength=1))
            score.insert(float(index), chord.Chord([48, 52, 55], quarterLength=1))
        features = amocore_v59._learning_features_from_score(score)
        self.assertLess(features["leap_ratio"], 0.25)
        self.assertAlmostEqual(features["note_density"], 1.0, places=2)

        eighths = stream.Stream()
        for _ in range(8):
            eighths.append(note.Note(60, quarterLength=0.5))
        dense = amocore_v59._learning_features_from_score(eighths)
        self.assertAlmostEqual(dense["note_density"], 2.0, places=2)

    @unittest.skipUnless(sys.platform == "win32", "syntezator Windows")
    def test_windows_sequencer_reads_music21_midi_and_play_is_detached(self):
        from music21 import note, stream

        import midi_windows

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        score = stream.Score()
        part = stream.Part()
        part.append(note.Note(60, quarterLength=1))
        score.append(part)
        path = os.path.join(folder.name, "one.mid")
        score.write("midi", fp=path)

        self.assertGreater(midi_windows.probe_midi(path), 0)
        midi_windows.stop_midi()
        with mock.patch.object(midi_windows.subprocess, "Popen", return_value=mock.Mock(poll=lambda: None)) as popen:
            played = midi_windows.play_midi(path)
        self.assertEqual(played, os.path.abspath(path))
        command = popen.call_args.args[0]
        self.assertEqual(command, midi_windows.play_command(os.path.abspath(path)))
        self.assertEqual(os.path.abspath(command[-1]), os.path.abspath(path))
        self.assertNotEqual(popen.call_args.kwargs.get("creationflags", 0), 0)
        self.assertIsNone(midi_windows.play_composed_midi({"midi": path, "wav": path + ".wav"}))

    @unittest.skipUnless(sys.platform == "win32", "syntezator Windows")
    def test_play_uses_eriamo_midi_when_player_and_soundfont_exist(self):
        from music21 import note, stream

        import midi_windows

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        score = stream.Score()
        part = stream.Part()
        part.append(note.Note(60, quarterLength=1))
        score.append(part)
        path = os.path.join(folder.name, "one.mid")
        score.write("midi", fp=path)
        player = os.path.join(folder.name, "eriamo-midi.exe")
        soundfont = os.path.join(folder.name, "bank.sf2")

        with mock.patch.object(midi_windows, "rust_player_path", return_value=player), \
             mock.patch.object(midi_windows, "resolved_soundfont", return_value=soundfont), \
             mock.patch.object(midi_windows.subprocess, "Popen", return_value=mock.Mock(poll=lambda: None)) as popen:
            played = midi_windows.play_midi(path)

        self.assertEqual(played, os.path.abspath(path))
        command = popen.call_args.args[0]
        self.assertEqual(command, [player, "play", "--soundfont", soundfont, os.path.abspath(path)])

    @unittest.skipUnless(sys.platform == "win32", "syntezator Windows")
    def test_play_uses_eriamo_midi_without_soundfont(self):
        from music21 import note, stream

        import midi_windows

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        score = stream.Score()
        part = stream.Part()
        part.append(note.Note(60, quarterLength=1))
        score.append(part)
        path = os.path.join(folder.name, "one.mid")
        score.write("midi", fp=path)
        player = os.path.join(folder.name, "eriamo-midi.exe")

        with mock.patch.object(midi_windows, "rust_player_path", return_value=player), \
             mock.patch.object(midi_windows, "resolved_soundfont", return_value=None), \
             mock.patch.object(midi_windows.subprocess, "Popen", return_value=mock.Mock(poll=lambda: None)) as popen:
            midi_windows.play_midi(path)

        command = popen.call_args.args[0]
        self.assertEqual(command, [player, "play", os.path.abspath(path)])

    def test_render_uses_eriamo_midi_instead_of_missing_fluidsynth(self):
        import composer_score
        import midi_windows

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        midi_path = os.path.join(folder.name, "one.mid")
        wav_path = os.path.join(folder.name, "one.wav")
        with open(midi_path, "wb") as handle:
            handle.write(b"MThd")

        def write_wav(command, **_kwargs):
            self.assertEqual(command[1], "render")
            self.assertEqual(command[-2], midi_path)
            self.assertEqual(command[-1], wav_path)
            with open(wav_path, "wb") as handle:
                handle.write(b"RIFF")
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.dict(os.environ, {"ERIAMO_SKIP_WAV": ""}), \
             mock.patch.object(composer_score, "resolve_soundfont", return_value="bank.sf2"), \
             mock.patch.object(midi_windows, "rust_player_path", return_value="eriamo-midi.exe"), \
             mock.patch.object(midi_windows, "resolved_soundfont", return_value="bank.sf2"), \
             mock.patch.object(midi_windows.subprocess, "run", side_effect=write_wav), \
             mock.patch.object(composer_score, "AudioSegment", None), \
             mock.patch.object(composer_score.shutil, "which", return_value=None):
            paths = composer_score.ScoreMixin._render_audio(object(), midi_path)

        self.assertEqual(paths.get("wav"), wav_path)

    def test_composed_wav_plays_without_starting_midi(self):
        import midi_windows

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        wav_path = os.path.join(folder.name, "one.wav")
        with open(wav_path, "wb") as handle:
            handle.write(b"RIFF")
        with mock.patch("winsound.PlaySound") as play:
            message = midi_windows.play_composed_midi({"midi": wav_path + ".mid", "wav": wav_path})
        play.assert_called_once()
        self.assertIn(os.path.abspath(wav_path), message or "")

    def test_rock_line_is_a_stepwise_sequence(self):
        import random

        random.seed(1)
        data = EriAmoSession().composer._generate_rock_polyphonic()
        melody = data["melody"]
        self.assertGreaterEqual(len(melody), 8)

        def pitches(bar):
            return [ev["pitch"] for ev in bar if ev.get("type") == "note"]

        stream = []
        for bar in melody:
            self.assertAlmostEqual(sum(float(ev["duration"]) for ev in bar), 4.0, places=3)
            got = pitches(bar)
            self.assertGreater(len(got), 0)
            stream.extend(got)
        intervals = [abs(b - a) for a, b in zip(stream, stream[1:])]
        self.assertGreater(len(intervals), 0)
        small = sum(1 for gap in intervals if gap <= 5)
        self.assertGreater(small / len(intervals), 0.75)
        first = pitches(melody[0])
        second = pitches(melody[1])
        answer = pitches(melody[4])
        rock = [57, 60, 61, 62, 64, 67, 69]
        tones = sorted(set(rock + [pitch + 12 for pitch in rock]))
        self.assertEqual(
            [tones.index(pitch) for pitch in second],
            [tones.index(pitch) + 1 for pitch in first],
        )
        self.assertNotEqual(first, answer)

    def test_lament_sequence_steps_down(self):
        import random

        random.seed(1)
        melody = EriAmoSession().composer._generate_lament_polyphonic()["melody"]
        opening = [ev["pitch"] for ev in melody[0] if ev.get("type") == "note"]
        answer = [ev["pitch"] for ev in melody[1] if ev.get("type") == "note"]
        self.assertGreater(len(opening), 0)
        self.assertLess(answer[0], opening[0])
        self.assertAlmostEqual(sum(float(ev["duration"]) for ev in melody[0]), 4.0, places=3)

    def test_menuet_dice_uses_the_176_written_bars(self):
        import random

        from composer_menuet import MenuetMixin
        from dice_measures import DICE_MEASURES, events_from_measure

        self.assertEqual(sorted(DICE_MEASURES), list(range(1, 177)))
        for measure_id, (right, left) in DICE_MEASURES.items():
            for voice in (right, left):
                total = sum(float(duration) for _pitches, duration in voice)
                self.assertAlmostEqual(total, 3.0, places=6, msg=measure_id)
            for pitches, _duration in right + left:
                if pitches is None:
                    continue
                for pitch in pitches:
                    self.assertGreaterEqual(pitch, 0)
                    self.assertLessEqual(pitch, 127)
        self.assertEqual(
            DICE_MEASURES[1],
            (
                (((77,), 1.0), ((74,), 1.0), ((79,), 1.0)),
                (((53,), 1.0), ((50,), 1.0), ((55,), 1.0)),
            ),
        )
        self.assertEqual(
            DICE_MEASURES[2],
            (
                (((69,), 0.5), ((66,), 0.5), ((67,), 0.5), ((71,), 0.5), ((79,), 1.0)),
                (((47, 55), 2.0), (None, 1.0)),
            ),
        )
        self.assertEqual(DICE_MEASURES[5][0][0], ((67, 71, 74, 79), 2.0))
        self.assertEqual(
            DICE_MEASURES[15],
            (
                (((76,), 1.0), ((79,), 0.5), ((76,), 0.5), ((72,), 1.0)),
                (((48, 55), 2.0), ((48, 52), 1.0)),
            ),
        )

        tables = MenuetMixin.MENUET_MASTERS["MOZART_DICE"]
        numbered = []
        for table in (tables["dice_table_A"], tables["dice_table_B"]):
            for row in table:
                numbered.extend(row)
        self.assertEqual(sorted(numbered), list(range(1, 177)))

        previous_home = os.environ.get("ERIAMO_HOME")
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        amocore_v59.shutdown_music_memory()
        amocore_v59._music_memory = None
        os.environ["ERIAMO_HOME"] = folder.name

        def restore_home():
            amocore_v59.shutdown_music_memory()
            amocore_v59._music_memory = None
            if previous_home is None:
                os.environ.pop("ERIAMO_HOME", None)
            else:
                os.environ["ERIAMO_HOME"] = previous_home

        self.addCleanup(restore_home)
        session = EriAmoSession()
        random.seed(2)
        plain = session.composer._generate_menuet_mozart_dice()
        random.seed(2)
        shifted = session.composer._generate_menuet_mozart_dice(67)

        self.assertFalse(plain["structure"]["is_minor"])
        self.assertFalse(shifted["structure"]["is_minor"])
        self.assertEqual(shifted["structure"]["tonic"], 67)
        self.assertEqual(shifted["structure"]["measure_ids"], plain["structure"]["measure_ids"])
        rolls = plain["structure"]["dice_results"]
        measure_ids = plain["structure"]["measure_ids"]
        self.assertEqual(len(plain["melody"]), 16)
        self.assertEqual(len(rolls), 16)
        for index, (roll, measure_id) in enumerate(zip(rolls, measure_ids)):
            table = tables["dice_table_A"] if index < 8 else tables["dice_table_B"]
            self.assertEqual(measure_id, table[roll - 2][index % 8])
            right, left = events_from_measure(measure_id, 0)
            self.assertEqual(plain["melody"][index], right)
            self.assertEqual(plain["harmony"][index], left)
            shifted_right, shifted_left = events_from_measure(measure_id, 7)
            self.assertEqual(shifted["melody"][index], shifted_right)
            self.assertEqual(shifted["harmony"][index], shifted_left)
            for voice in (right, left):
                self.assertAlmostEqual(
                    sum(float(event["duration"]) for event in voice), 3.0, places=3,
                )

    def test_rock_and_roll_tempo_is_allegro_moderato(self):
        from composer_score import ScoreMixin

        data = {
            "melody": [[{"type": "note", "pitch": 60, "duration": 1.0, "dynamic": "f"}]],
            "harmony": [[{"type": "chord", "pitch": [48, 55], "duration": 1.0, "dynamic": "mf"}]],
        }
        score = ScoreMixin._create_music21_score(ScoreMixin(), data, "ROCK_AND_ROLL")
        marks = list(score.recurse().getElementsByClass("MetronomeMark"))
        self.assertEqual(marks[0].number, 120)

    def test_quoted_midi_path_is_rejected(self):
        import midi_windows

        with self.assertRaises(ValueError):
            midi_windows.play_midi(r'C:\eriamo\bad"name.mid')

    def test_report_uri_uses_three_slashes_on_windows_drive(self):
        uri = Path("C:/Users/eriamo/report basic.html").resolve().as_uri()
        self.assertTrue(uri.startswith("file:///"))
        self.assertNotIn("\\", uri)
        self.assertIn("report%20basic.html", uri)


if __name__ == "__main__":
    unittest.main()
