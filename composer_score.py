# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Zapis partytury Music21 i render audio."""
import os

from composer_runtime import AUDIO_AVAIL, MUSIC21_AVAIL, music21, FluidSynth, AudioSegment
from instruments import midi_program
from soundfont import resolve_soundfont, soundfont_missing_message


class ScoreMixin:
    def _render_audio(self, midi_path: str) -> dict:
        """Konwertuje MIDI na WAV. OGG i FLAC powstają, gdy jest pydub."""
        if not AUDIO_AVAIL or FluidSynth is None:
            return {}
        soundfont = resolve_soundfont()
        if not soundfont:
            print(soundfont_missing_message())
            return {}

        base_path = os.path.splitext(midi_path)[0]
        wav_path = f"{base_path}.wav"
        ogg_path = f"{base_path}.ogg"
        flac_path = f"{base_path}.flac"

        paths = {}
        try:
            fs = FluidSynth(soundfont)
            fs.midi_to_audio(midi_path, wav_path)
            if not os.path.exists(wav_path):
                return paths
            if AudioSegment is None:
                print("[AUDIO] Zostawiam WAV. OGG i FLAC wymagają pydub.")
                paths["wav"] = wav_path
                return paths
            audio = AudioSegment.from_wav(wav_path)
            audio.export(ogg_path, format="ogg")
            paths["ogg"] = ogg_path
            audio.export(flac_path, format="flac")
            paths["flac"] = flac_path
            os.remove(wav_path)
        except Exception as e:
            print(f"[AUDIO ERROR] Błąd renderowania: {e}")

        return paths

    def _create_music21_score(self, data: dict, genre_name: str, instrument_override: str = None):
        """Tworzy partyturę Music21 z danych polifonicznych."""
        if not MUSIC21_AVAIL:
            return None

        score = music21.stream.Score()

        # Metadane
        md = music21.metadata.Metadata()
        md.title = f"{genre_name} by EriAmo"
        md.composer = "EriAmo AI v5.9"
        score.insert(0, md)

        # Instrument i Tempo
        # 
        # WYBÓR INSTRUMENTU DLA MENUETU:
        # Program 6 = Harpsichord (klawesyn) - historycznie poprawny dla XVIII w.
        # 
        # Menuety w stylu Riepela (1709-1782) były komponowane na:
        # - Klawesyn (clavecin) - najpopularniejszy w epoce baroku/galant
        # - Fortepian wczesny (Hammerklavier) - od ok. 1770
        # - Zespół kameralny (smyczki + continuo)
        #
        # Alternatywy (można użyć instrument_override):
        # - 'piano' (0) - fortepian współczesny
        # - 'bright_piano' (1) - jasny fortepian  
        # - 'organ' (19) - organy pozytywne
        # - 'strings' (48) - smyczki
        #
        midi_prog = 0
        if instrument_override:
            midi_prog = midi_program(instrument_override)
        elif genre_name == "POWER_METAL":
            midi_prog = 30  # Distortion Guitar
        elif genre_name == "HEAVY_METAL":
            midi_prog = 30
        elif genre_name == "ROCK_AND_ROLL":
            midi_prog = 29  # Electric Guitar
        elif genre_name == "AMBIENT":
            midi_prog = 96  # SFX/Pad
        elif genre_name == "MENUET":
            midi_prog = 6   # Harpsichord (klawesyn) - autentyczny dla epoki

        bpm_map = {
            "POWER_METAL": 170, "HEAVY_METAL": 110, "ROCK_AND_ROLL": 160, "BLUES": 90,
            "MENUET": 116, "WALC": 168, "LAMENT": 50, "AMBIENT": 60
        }
        bpm = bpm_map.get(genre_name, 120)

        # Interpretacja (Tempo Text)
        tempo_text = {
            "POWER_METAL": "Presto con fuoco",
            "MENUET": "Tempo di Menuetto",
            "WALC": "Tempo di Valse",
            "LAMENT": "Adagio lamentoso",
            "ROCK_AND_ROLL": "Allegro energico"
        }.get(genre_name, "Moderato")

        # Sprawdź czy mamy strukturę z powtórzeniami (menuet Riepela)
        structure = data.get('structure', None)
        has_repeats = structure is not None and genre_name == "MENUET"

        # --- PART 1: MELODIA (RH) ---
        p1 = music21.stream.Part()
        p1.id = 'RightHand'
        p1.insert(0, music21.tempo.MetronomeMark(number=bpm))
        p1.insert(0, music21.expressions.TextExpression(tempo_text))

        inst = music21.instrument.Instrument()
        inst.midiProgram = midi_prog
        p1.insert(0, inst)
        meter = "3/4" if genre_name in ("MENUET", "WALC") else "4/4"
        p1.insert(0, music21.meter.TimeSignature(meter))

        # Budowanie taktów z numeracją
        measure_num = 1
        total_measures = len(data['melody'])
        
        for m_data in data['melody']:
            m = music21.stream.Measure()
            m.number = measure_num

            # === ZNAKI POWTÓRZENIA DLA MENUETU ===
            if has_repeats:
                # Część A: takty 1-8
                if measure_num == 1:
                    # Początek z powtórzeniem
                    m.leftBarline = music21.bar.Barline(style='heavy-light')
                elif measure_num == 8:
                    # Koniec części A - znak powtórzenia
                    m.rightBarline = music21.bar.Repeat(direction='end')
                elif measure_num == 9:
                    # Początek części B
                    m.leftBarline = music21.bar.Repeat(direction='start')
                elif measure_num == 16:
                    # Koniec części B - znak powtórzenia
                    m.rightBarline = music21.bar.Repeat(direction='end')

            # Dodaj nuty
            notes_in_measure = []
            for ev in m_data:
                if ev.get('type') == 'rest':
                    # Pauza
                    r = music21.note.Rest()
                    r.quarterLength = ev['duration']
                    m.append(r)
                else:
                    n = music21.note.Note(ev['pitch'])
                    n.quarterLength = ev['duration']

                    # Dynamika
                    vel = {'ppp': 30, 'pp': 40, 'p': 50, 'mp': 64, 'mf': 80, 'f': 96, 'ff': 112}.get(ev.get('dynamic', 'mf'), 80)
                    n.volume.velocity = vel

                    # Fermata
                    if ev.get('fermata', False):
                        n.expressions.append(music21.expressions.Fermata())

                    # Artykulacja (Staccato dla krótkich w Menuecie)
                    if genre_name == "MENUET" and n.quarterLength <= 0.5:
                        n.articulations.append(music21.articulations.Staccato())

                    m.append(n)
                    notes_in_measure.append(n)

            # Frazy (Slur) - Riepel: frazy 4-taktowe
            if genre_name == "MENUET" and notes_in_measure:
                # Vordersatz: t.1-4, Nachsatz: t.5-8, Fortspinnung: t.9-12, Rückgang: t.13-16
                phrase_boundaries = [1, 5, 9, 13]
                phrase_ends = [4, 8, 12, 16]
                
                if measure_num in phrase_boundaries:
                    self._slur_start = notes_in_measure[0]
                if measure_num in phrase_ends and self._slur_start is not None:
                    slur = music21.spanner.Slur(self._slur_start, notes_in_measure[-1])
                    p1.insert(0, slur)
                    self._slur_start = None

            p1.append(m)
            measure_num += 1

        # --- PART 2: HARMONIA (LH) ---
        p2 = music21.stream.Part()
        p2.id = 'LeftHand'

        inst2 = music21.instrument.Instrument()
        if instrument_override:
            inst2.midiProgram = midi_prog
        elif genre_name in ["POWER_METAL", "ROCK_AND_ROLL", "HEAVY_METAL"]:
            inst2.midiProgram = 33  # Bass
        elif genre_name == "MENUET":
            inst2.midiProgram = 6  # Harpsichord
        else:
            inst2.midiProgram = midi_prog
        p2.insert(0, inst2)
        p2.insert(0, music21.meter.TimeSignature(meter))

        measure_num = 1
        for m_data in data['harmony']:
            m = music21.stream.Measure()
            m.number = measure_num

            # Znaki powtórzenia (LH musi mieć takie same jak RH)
            if has_repeats:
                if measure_num == 1:
                    m.leftBarline = music21.bar.Barline(style='heavy-light')
                elif measure_num == 8:
                    m.rightBarline = music21.bar.Repeat(direction='end')
                elif measure_num == 9:
                    m.leftBarline = music21.bar.Repeat(direction='start')
                elif measure_num == 16:
                    m.rightBarline = music21.bar.Repeat(direction='end')

            for ev in m_data:
                vel = {'ppp': 30, 'pp': 40, 'p': 50, 'mp': 64, 'mf': 80, 'f': 96, 'ff': 112}.get(ev.get('dynamic', 'mf'), 80)
                
                if ev.get('type') == 'rest':
                    r = music21.note.Rest()
                    r.quarterLength = ev['duration']
                    m.append(r)
                elif ev['type'] == 'chord':
                    c = music21.chord.Chord(ev['pitch'])
                    c.quarterLength = ev['duration']
                    c.volume.velocity = vel
                    m.append(c)
                elif ev['type'] == 'note':
                    n = music21.note.Note(ev['pitch'])
                    n.quarterLength = ev['duration']
                    n.volume.velocity = vel
                    # Tenuto dla basu w menuecie (cięższy, nie staccato)
                    if genre_name == "MENUET" and n.quarterLength >= 1.0:
                        n.articulations.append(music21.articulations.Tenuto())
                    m.append(n)
            p2.append(m)
            measure_num += 1

        # Końcowa kreska taktowa (tylko jeśli nie ma powtórzeń)
        if not has_repeats:
            final_bar = music21.bar.Barline(style='light-heavy', location='right')
            if p1.measure(measure_num - 1):
                p1.measure(measure_num - 1).rightBarline = final_bar
            if p2.measure(measure_num - 1):
                p2.measure(measure_num - 1).rightBarline = final_bar

        score.insert(0, p1)
        score.insert(0, p2)
        return score
