# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Generatory gatunków popularnych i form prostych."""
import random


class GenreMixin:
    def _tone_ladder(self, scale, octave: int = 0) -> list:
        """Dwie oktawy skali, żeby linia miała gdzie wejść i zejść."""
        tones = []
        for shift in (0, 12):
            tones.extend(int(pitch) + octave + shift for pitch in scale)
        return sorted(set(tones))

    def _fill_durations(self, beats, metrics, rhythm_bias, min_duration) -> list:
        durations = []
        remaining = float(beats)
        guard = 0
        while remaining > 1e-6 and guard < 64:
            guard += 1
            dur = self._get_rhythm_duration(metrics, rhythm_bias)
            if dur < min_duration:
                dur = min_duration
            if dur <= 0:
                dur = 1.0
            if dur > remaining:
                dur = remaining
            if dur <= 1e-9:
                break
            durations.append(float(dur))
            remaining -= dur
        if not durations:
            return [float(beats)]
        durations[-1] = float(beats) - sum(durations[:-1])
        if durations[-1] <= 1e-9:
            durations.pop()
            if not durations:
                return [float(beats)]
            durations[-1] = float(beats) - sum(durations[:-1])
        return durations

    def _nearest_chord_index(self, tones, index, chord_pcs) -> int:
        found = [i for i, pitch in enumerate(tones) if pitch % 12 in chord_pcs]
        if not found:
            return index
        return min(found, key=lambda i: (abs(i - index), i))

    def _nearest_pitch_index(self, tones, index, pitch) -> int:
        found = [i for i, tone in enumerate(tones) if tone % 12 == int(pitch) % 12]
        if not found:
            return index
        return min(found, key=lambda i: (abs(i - index), i))

    def _motif_from(self, tones, start, durations, steps, upward, dynamic):
        """Krótki kształt: kroki z `steps`, pierwszy dźwięk na `start`."""
        start = max(0, min(len(tones) - 1, int(start)))
        offsets = [0]
        pos = 0
        sign = 1 if upward else -1
        for i in range(1, len(durations)):
            pos += sign * int(steps[(i - 1) % len(steps)])
            offsets.append(pos)
        events = []
        last = start
        for offset, dur in zip(offsets, durations):
            last = max(0, min(len(tones) - 1, start + offset))
            events.append({"type": "note", "pitch": tones[last], "duration": dur, "dynamic": dynamic})
        motif = {"start": start, "offsets": offsets, "durations": list(durations)}
        return events, last, motif

    def _replay_motif(self, tones, start, motif, dynamic, invert=False):
        sign = -1 if invert else 1
        events = []
        last = max(0, min(len(tones) - 1, int(start)))
        for offset, dur in zip(motif["offsets"], motif["durations"]):
            last = max(0, min(len(tones) - 1, start + sign * offset))
            events.append({"type": "note", "pitch": tones[last], "duration": dur, "dynamic": dynamic})
        return events, last

    def _walk_to(self, tones, index, target, durations, dynamic):
        """Idzie po stopniach. Ostatnia nuta siada na celu, żeby fraza miała koniec."""
        target = max(0, min(len(tones) - 1, int(target)))
        events = []
        for note_index, dur in enumerate(durations):
            if note_index == len(durations) - 1:
                index = target
            elif index < target:
                index += 1
            elif index > target:
                index -= 1
            index = max(0, min(len(tones) - 1, index))
            events.append({"type": "note", "pitch": tones[index], "duration": dur, "dynamic": dynamic})
        return events, index

    def _avoid_copy(self, tones, events, previous, upward):
        signature = tuple(ev["pitch"] for ev in events if ev.get("type") == "note")
        if previous and signature == previous:
            shift = 1 if upward else -1
            for ev in events:
                if ev.get("type") != "note":
                    continue
                moved = tones.index(ev["pitch"]) + shift
                ev["pitch"] = tones[max(0, min(len(tones) - 1, moved))]
            signature = tuple(ev["pitch"] for ev in events if ev.get("type") == "note")
        return signature

    def _emit_phrase_bar(self, role, tones, index, motif, steps, upward, beats, metrics, rhythm_bias, dynamic, min_duration, chord_pcs):
        if role == "motif" or motif is None or role not in ("sequence", "invert", "cadence"):
            durations = self._fill_durations(beats, metrics, rhythm_bias, min_duration)
            return self._motif_from(tones, index, durations, steps, upward, dynamic)
        if role == "sequence":
            delta = 1 if upward else -1
            start = max(0, min(len(tones) - 1, motif["start"] + delta))
            events, index = self._replay_motif(tones, start, motif, dynamic, invert=False)
            return events, index, motif
        if role == "invert":
            events, index = self._replay_motif(tones, index, motif, dynamic, invert=True)
            return events, index, motif
        durations = self._fill_durations(beats, metrics, rhythm_bias, min_duration)
        target = self._nearest_chord_index(tones, index, chord_pcs)
        events, index = self._walk_to(tones, index, target, durations, dynamic)
        return events, index, motif

    def _line_over(self, progression, scale, beats, metrics, rhythm_bias, octave, dynamic, min_duration=0.0, cell=(1, 1, -1, 2, -1), prefer_down=False):
        """Motyw, powtórka o stopień, odwrócenie, dojście do akordu. Co cztery takty odpowiedź z innej nuty."""
        tones = self._tone_ladder(scale, octave)
        index = min(2, len(tones) - 1)
        motif = None
        previous = None
        melody = []
        phrase = 4 if len(progression) >= 4 else max(1, len(progression))
        roles = ["motif", "sequence", "invert", "cadence"][:phrase]
        if phrase > 1:
            roles[-1] = "cadence"
        upward = True
        for bar_index, (root, ctype) in enumerate(progression):
            local = bar_index % phrase
            answer = (bar_index // phrase) % 2 == 1
            if local == 0:
                upward = False if prefer_down else not answer
                if answer:
                    bump = 3 if prefer_down else 2
                    index = max(0, min(len(tones) - 1, index + bump))
            chord_pcs = {note % 12 for note in self._build_chord_notes(root, ctype)}
            events, index, motif = self._emit_phrase_bar(
                roles[local], tones, index, motif, cell, upward, beats, metrics,
                rhythm_bias, dynamic, min_duration, chord_pcs,
            )
            previous = self._avoid_copy(tones, events, previous, upward)
            if events and events[-1].get("type") == "note":
                index = tones.index(events[-1]["pitch"])
            melody.append(events)
        return melody

    # ============= LAMENT (SAD & DEEP) =============

    def _generate_lament_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(57, 'min'), (56, 'dim'), (55, 'maj'), (54, 'dim'),
                       (53, 'maj'), (52, 'maj'), (57, 'min'), (57, 'min')] * 2
        harmony = []
        for root, ctype in progression:
            harmony.append([{'type': 'chord', 'pitch': self._build_chord_notes(root, ctype), 'duration': 4.0, 'dynamic': 'p'}])
        melody = self._line_over(
            progression, [57, 59, 60, 62, 64, 65, 67, 69], 4.0, metrics, -8.0, 0, "mp",
            cell=(1, 1, -1, 1), prefer_down=True,
        )
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 9)
        return {'melody': melody, 'harmony': harmony}

    def _generate_ambient_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(48, 'maj7'), (53, 'maj7'), (55, 'sus4'), (48, 'maj7')] * 3
        harmony = []
        for root, ctype in progression:
            cn = self._build_chord_notes(root, ctype)
            harmony.append([{'type': 'chord', 'pitch': [cn[0] - 12, cn[1], cn[2] + 12], 'duration': 4.0, 'dynamic': 'pp'}])
        tunes = (
            (
                ((60, 2.0), (64, 2.0)),
                ((65, 2.0), (69, 2.0)),
                ((67, 2.0), (62, 2.0)),
                None,
                ((64, 2.0), (67, 2.0)),
                ((69, 2.0), (65, 2.0)),
                ((62, 2.0), (60, 2.0)),
                None,
                ((60, 2.0), (67, 2.0)),
                ((69, 2.0), (65, 2.0)),
                ((62, 2.0), (67, 2.0)),
                ((60, 4.0),),
            ),
            (
                ((64, 2.0), (67, 2.0)),
                ((69, 2.0), (72, 2.0)),
                ((74, 2.0), (72, 2.0)),
                None,
                ((67, 2.0), (64, 2.0)),
                ((65, 2.0), (69, 2.0)),
                ((67, 4.0),),
                None,
                ((72, 2.0), (69, 2.0)),
                ((65, 2.0), (64, 2.0)),
                ((62, 2.0), (67, 2.0)),
                ((60, 4.0),),
            ),
        )
        melody = []
        for bar in random.choice(tunes):
            if bar is None:
                melody.append([{'type': 'rest', 'duration': 4.0, 'dynamic': 'pp'}])
                continue
            melody.append([
                {'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': 'pp' if i == 0 else 'ppp'}
                for i, (pitch, dur) in enumerate(bar)
            ])
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 0)
        return {'melody': melody, 'harmony': harmony}

    def _generate_power_metal(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(40, 'power'), (40, 'power'), (36, 'power'), (38, 'power'),
                       (40, 'power'), (43, 'power'), (38, 'power'), (40, 'power')] * 2
        scale_e = [40, 42, 43, 45, 47, 48, 50, 52]
        harmony = []

        if metrics['logika'] > 20.0:
            style = 'straight'
        elif metrics['emocje'] > 20.0:
            style = 'gallop'
        else:
            style = 'sustain'

        for root, ctype in progression:
            cn = self._build_chord_notes(root, ctype)
            lh = []
            if style == 'sustain':
                lh.append({'type': 'chord', 'pitch': cn, 'duration': 4.0, 'dynamic': 'ff'})
            elif style == 'gallop':
                for _ in range(4):
                    lh.extend([
                        {'type': 'chord', 'pitch': cn, 'duration': 0.5, 'dynamic': 'mf'},
                        {'type': 'chord', 'pitch': cn, 'duration': 0.25, 'dynamic': 'mp'},
                        {'type': 'chord', 'pitch': cn, 'duration': 0.25, 'dynamic': 'mp'}
                    ])
            else:  # straight
                accent = 'ff' if metrics['byt'] > 0 else 'mf'
                for i in range(8):
                    lh.append({'type': 'chord', 'pitch': cn, 'duration': 0.5, 'dynamic': accent if i == 0 else 'mf'})
            harmony.append(lh)

        melody = self._line_over(
            progression, scale_e, 4.0, metrics, 10.0, 24, "f",
            cell=(1, 1, -1, 1, 2, -1, 1, -1),
        )
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 4)
        return {'melody': melody, 'harmony': harmony}

    def _generate_rock_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(57, 'maj')] * 4 + [(62, 'maj')] * 2 + [(57, 'maj')] * 2 + [(64, 'maj'), (62, 'maj'), (57, 'maj'), (64, 'maj')]
        progression *= 2
        rock_scale = [57, 60, 61, 62, 64, 67, 69]
        harmony = []

        # Używam '_' bo Rock ma Boogie-bass, nie pełne akordy
        for root, _ in progression:
            lh, base = [], root - 12
            if metrics['czas'] > 10.0:
                for _ in range(4):
                    lh.append({'type': 'chord', 'pitch': [base, base + 7], 'duration': 0.5, 'dynamic': 'mf'})
                    lh.append({'type': 'chord', 'pitch': [base, base + 9], 'duration': 0.5, 'dynamic': 'mf'})
            else:
                lh = [
                    {'type': 'chord', 'pitch': [base, base + 7], 'duration': 1.0, 'dynamic': 'mf'},
                    {'type': 'chord', 'pitch': [base, base + 9], 'duration': 1.0, 'dynamic': 'mf'}
                ] * 2
            harmony.append(lh)

        melody = self._line_over(
            progression, rock_scale, 4.0, metrics, 0.0, 0, "f",
            cell=(1, 0, 1, -1, 2, -1),
        )
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 9)
        return {'melody': melody, 'harmony': harmony}

    def _generate_blues_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        
        # Progresja 12-taktowa (Standard Blues)
        # Takt 1-4: I (C7)
        # Takt 5-6: IV (F7)
        # Takt 7-8: I (C7)
        # Takt 9: V (G7), Takt 10: IV (F7), Takt 11: I (C7), Takt 12: V (G7) - Turnaround
        progression = [(48, '7')] * 4 + [(53, '7')] * 2 + [(48, '7')] * 2 + [(55, '7'), (53, '7'), (48, '7'), (55, '7')]
        
        # Skala bluesowa C: C, Eb, F, F#, G, Bb, C
        blue_scale = [60, 63, 65, 66, 67, 70, 72]
        
        harmony = []

        for root, c_type in progression:
            # === LEWA RĘKA: BOOGIE WOOGIE PATTERN ===
            # Zamiast statycznych akordów, gramy interwały.
            # Dzięki temu słychać zmianę harmonii.
            
            lh_measure = []
            base = root - 12  #  niżej dla basu
            
            # Wzorzec Boogie: 1-5, 1-6, 1-7, 1-6 (po ćwierćnutach)
            # interwały od 'base': 0 (root), 7 (kwinta), 9 (seksta), 10 (septyma mała)
            boogie_intervals = [7, 9, 10, 9] 
            
            for interval in boogie_intervals:
                # Tworzymy dwudźwięk: Root + interwał (np. C + G, potem C + A...)
                pitch_pair = [base, base + interval]
                lh_measure.append({'type': 'chord', 'pitch': pitch_pair, 'duration': 1.0, 'dynamic': 'mf'})
                
            harmony.append(lh_measure)

        melody = self._line_over(
            progression, blue_scale, 4.0, metrics, -2.0, 0, "mf",
            cell=(1, -1, 2, -1, 1, -2),
        )

        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 0)
        return {'melody': melody, 'harmony': harmony}

    def _generate_heavy_metal(self) -> dict:
        """Wolniejsze, niższe riffy niż power metal. Tonacja E."""
        metrics = self._get_soul_metrics()
        progression = [(40, "power"), (40, "power"), (35, "power"), (38, "power")] * 2
        scale_e = [40, 43, 45, 46, 47, 50, 52]
        harmony = []
        for root, ctype in progression:
            cn = self._build_chord_notes(root, ctype)
            harmony.append([
                {"type": "chord", "pitch": cn, "duration": 2.0, "dynamic": "ff"},
                {"type": "chord", "pitch": cn, "duration": 1.0, "dynamic": "f"},
                {"type": "chord", "pitch": cn, "duration": 1.0, "dynamic": "mf"},
            ])
        melody = self._line_over(
            progression, scale_e, 4.0, metrics, -4.0, 12, "ff", min_duration=0.5,
            cell=(1, 0, 1, -1, 2, -1),
        )
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 4)
        return {"melody": melody, "harmony": harmony}

    def _generate_waltz(self) -> dict:
        """Walc 8+8 w 3/4. Takt 8 kończy się na kwincie, takt 16 na tonice."""
        metrics = self._get_soul_metrics()
        style = metrics.get("memory_style") or {}
        is_minor = bool(style.get("has_data")) and float(style.get("key_mode", 1.0)) < 0.5
        degrees = [0, 5, 0, 7, 0, 5, 7, 7, 7, 7, 0, 5, 0, 5, 7, 0]
        intervals = [0, 2, 3, 5, 7, 8, 10, 12] if is_minor else [0, 2, 4, 5, 7, 9, 11, 12]
        tones = self._tone_ladder([60 + step for step in intervals])
        index = min(2, len(tones) - 1)
        motif = None
        upward = True
        cell = (1, -1, 2, 1, -1)
        melody, harmony = [], []
        for bar_index, degree in enumerate(degrees):
            root = 48 + degree
            ctype = "min" if is_minor and degree in (0, 5) else "maj"
            chord_notes = self._build_chord_notes(root, ctype)
            harmony.append([
                {"type": "note", "pitch": root - 12, "duration": 1.0, "dynamic": "mf"},
                {"type": "chord", "pitch": chord_notes, "duration": 1.0, "dynamic": "mp"},
                {"type": "chord", "pitch": chord_notes, "duration": 1.0, "dynamic": "mp"},
            ])
            if bar_index == 7:
                melody.append(self._quarter_bar(65, 65, 67))
                continue
            if bar_index == 15:
                third = 63 if is_minor else 64
                melody.append(self._quarter_bar(third, 62, 60))
                continue
            local = bar_index % 8
            if local == 0:
                upward = bar_index == 0
                role = "motif"
            elif local == 3:
                upward = not upward
                role = "motif"
            elif local in (1, 4):
                role = "sequence"
            elif local in (2, 5):
                role = "invert"
            else:
                role = "cadence"
            if role == "cadence":
                target_pitch = 64 if bar_index == 6 else 62
                target = self._nearest_pitch_index(tones, index, target_pitch)
                durations = self._fill_durations(3.0, metrics, -2.0, 0.0)
                events, index = self._walk_to(tones, index, target, durations, "mf")
            else:
                events, index, motif = self._emit_phrase_bar(
                    role, tones, index, motif, cell, upward, 3.0, metrics,
                    -2.0, "mf", 0.0, {note % 12 for note in chord_notes},
                )
            melody.append(events)
        melody, harmony = self._apply_learned_key(melody, harmony, style, 0)
        return {"melody": melody, "harmony": harmony}

    def _quarter_bar(self, a: int, b: int, c: int) -> list:
        return [
            {"type": "note", "pitch": a, "duration": 1.0, "dynamic": "mf"},
            {"type": "note", "pitch": b, "duration": 1.0, "dynamic": "mf"},
            {"type": "note", "pitch": c, "duration": 1.0, "dynamic": "f"},
        ]

    # Temat kanonu w C-dur: osiem taktów ćwierćnut, potem dwa takty toniki.
    CANON_SUBJECT = [
        [60, 62, 64, 65],
        [67, 65, 64, 62],
        [64, 65, 67, 69],
        [67, 64, 62, 60],
        [69, 67, 65, 64],
        [62, 64, 65, 67],
        [64, 62, 60, 62],
        [64, 67, 65, 64],
    ]
    CANON_TAIL = [
        [60, 64, 67, 64],
        [67, 65, 62, 60],
    ]

    def _generate_canon(self) -> dict:
        """Dwa głosy. Drugi wchodzi po dwóch taktach, oktawę niżej."""
        metrics = self._get_soul_metrics()
        style = metrics.get("memory_style") or {}
        subject = [self._quarter_pitches(pitches) for pitches in self.CANON_SUBJECT]
        tail = [self._quarter_pitches(pitches) for pitches in self.CANON_TAIL]
        if style.get("has_data") and float(style.get("key_mode", 1.0)) < 0.5:
            subject = self._recolor_minor(subject)
            tail = self._recolor_minor(tail)
        subject = self._densify_measures(subject, style)
        tail = self._densify_measures(tail, style)
        subject = self._maybe_syncopate(subject, style)
        tail = self._maybe_syncopate(tail, style)
        leader = subject + tail
        follower = [
            [{"type": "rest", "duration": 4.0, "dynamic": "mf"}],
            [{"type": "rest", "duration": 4.0, "dynamic": "mf"}],
        ] + self._shift_measures(subject, -12)
        shift = self._key_shift(style, 0)
        return {
            "melody": self._shift_measures(leader, shift),
            "harmony": self._shift_measures(follower, shift),
        }

    def _quarter_pitches(self, pitches) -> list:
        return [
            {"type": "note", "pitch": pitch, "duration": 1.0, "dynamic": "mf"}
            for pitch in pitches
        ]
