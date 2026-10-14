# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Generatory gatunków popularnych i form prostych."""
import random


class GenreMixin:
    # ============= LAMENT (SAD & DEEP) =============

    def _generate_lament_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(57, 'min'), (56, 'dim'), (55, 'maj'), (54, 'dim'),
                       (53, 'maj'), (52, 'maj'), (57, 'min'), (57, 'min')] * 2
        melody, harmony = [], []

        for root, ctype in progression:
            harmony.append([{'type': 'chord', 'pitch': self._build_chord_notes(root, ctype), 'duration': 4.0, 'dynamic': 'p'}])
            rh, beat = [], 0.0
            while beat < 4.0:
                dur = 1.0 if random.random() > 0.3 else 2.0
                if beat + dur > 4.0:
                    dur = 4.0 - beat
                pitch = root + 12 + random.choice([0, 2, 3, 5, 7])
                if metrics['affections'] < -40:
                    pitch += 12
                rh.append({'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': 'mp'})
                beat += dur
            melody.append(rh)
        return {'melody': melody, 'harmony': harmony}

    def _generate_ambient_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(48, 'maj7'), (53, 'maj7'), (55, 'sus4'), (48, 'maj7')] * 3
        melody, harmony = [], []

        for root, ctype in progression:
            cn = self._build_chord_notes(root, ctype)
            harmony.append([{'type': 'chord', 'pitch': [cn[0] - 12, cn[1], cn[2] + 12], 'duration': 4.0, 'dynamic': 'pp'}])
            rh = []
            if metrics['przestrzen'] > 5 or random.random() > 0.7:
                rh.append({'type': 'note', 'pitch': root + 24 + random.choice([0, 4, 7, 11, 14]), 'duration': 4.0, 'dynamic': 'ppp'})
            melody.append(rh)
        return {'melody': melody, 'harmony': harmony}

    def _generate_power_metal(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(40, 'power'), (40, 'power'), (36, 'power'), (38, 'power'),
                       (40, 'power'), (43, 'power'), (38, 'power'), (40, 'power')] * 2
        scale_e = [40, 42, 43, 45, 47, 48, 50, 52]
        melody, harmony = [], []

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

            rh, beat = [], 0.0
            while beat < 4.0:
                dur = self._get_rhythm_duration(metrics, 10.0)
                if beat + dur > 4.0:
                    dur = 4.0 - beat
                pitch = random.choice(scale_e) + 24
                if metrics['affections'] > 0 and random.random() > 0.7:
                    pitch += 7
                rh.append({'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': 'f'})
                beat += dur
            melody.append(rh)
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 4)
        return {'melody': melody, 'harmony': harmony}

    def _generate_rock_polyphonic(self) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(57, 'maj')] * 4 + [(62, 'maj')] * 2 + [(57, 'maj')] * 2 + [(64, 'maj'), (62, 'maj'), (57, 'maj'), (64, 'maj')]
        progression *= 2
        rock_scale = [57, 60, 61, 62, 64, 67, 69]
        melody, harmony = [], []

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

            rh, beat = [], 0.0
            while beat < 4.0:
                dur = self._get_rhythm_duration(metrics, 5.0)
                if beat + dur > 4.0:
                    dur = 4.0 - beat
                note = random.choice(rock_scale)
                if metrics['affections'] < -20 and random.random() > 0.7:
                    note += 12
                rh.append({'type': 'note', 'pitch': note, 'duration': dur, 'dynamic': 'f'})
                beat += dur
            melody.append(rh)
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
        
        melody, harmony = [], []

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

            # === PRAWA RĘKA: MELODIA Z FILTREM FAŁSZU ===
            rh_measure = []
            beat = 0.0
            
            # Budujemy "wirtualny" pełny akord, żeby wiedzieć, które nuty są bezpieczne
            full_chord_notes = self._build_chord_notes(root, c_type)
            chord_classes = [n % 12 for n in full_chord_notes]
            
            # Bezpieczne nuty to te ze skali bluesowej, które są też w akordzie
            safe_notes = [n for n in blue_scale if (n % 12) in chord_classes]

            while beat < 4.0:
                dur = self._get_rhythm_duration(metrics, -2.0)
                if beat + dur > 4.0:
                    dur = 4.0 - beat
                
                # --- LOGIKA UNIKANIA FAŁSZU ---
                # Na mocnych częściach taktu (0.0 i 2.0) przy wysokiej Logice gramy czysto
                if metrics['logika'] > 10.0 and (beat == 0.0 or beat == 2.0 or beat == 1.0) and metrics['improwizacja'] < 50:
                    # Preferuj nuty akordowe
                    candidates = safe_notes if safe_notes else blue_scale
                    note = random.choice(candidates)
                else:
                    # Swoboda na słabszych częściach taktu
                    note = random.choice(blue_scale)
                
                # Dynamika
                dyn = 'p' if (metrics['affections'] < 0 and random.random() > 0.6) else 'mf'
                
                rh_measure.append({'type': 'note', 'pitch': note, 'duration': dur, 'dynamic': dyn})
                beat += dur
            melody.append(rh_measure)

        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 0)
        return {'melody': melody, 'harmony': harmony}

    def _generate_simple_poly(self, genre_name: str) -> dict:
        metrics = self._get_soul_metrics()
        progression = [(48, 'maj'), (53, 'maj'), (55, 'maj'), (48, 'maj')] * 4
        
        # Skala C-dur (pentatonika + F + B)
        scale = [60, 62, 64, 65, 67, 69, 71, 72]
        
        beats = 4.0
        melody, harmony = [], []
        for root, ctype in progression:
            chord_notes = self._build_chord_notes(root, ctype)
            harmony.append([
                {'type': 'chord', 'pitch': chord_notes, 'duration': beats, 'dynamic': 'mf'}
            ])

            rh_measure = []
            beat = 0.0
            chord_classes = [n % 12 for n in chord_notes]
            safe_notes = [n for n in scale if (n % 12) in chord_classes] or list(scale)

            while beat < beats:
                dur = self._get_rhythm_duration(metrics)
                if beat + dur > beats:
                    dur = beats - beat
                
                # Prosta logika konsonansu dla muzyki POP/SIMPLE
                if metrics['logika'] > 0 and beat == 0.0:
                     note = random.choice(safe_notes)
                else:
                     note = random.choice(scale)

                rh_measure.append({'type': 'note', 'pitch': note, 'duration': dur, 'dynamic': 'mf'})
                beat += dur
            melody.append(rh_measure)
        return {'melody': melody, 'harmony': harmony}

    def _generate_heavy_metal(self) -> dict:
        """Wolniejsze, niższe riffy niż power metal. Tonacja E."""
        metrics = self._get_soul_metrics()
        progression = [(40, "power"), (40, "power"), (35, "power"), (38, "power")] * 2
        scale_e = [40, 43, 45, 46, 47, 50, 52]
        melody, harmony = [], []
        for root, ctype in progression:
            cn = self._build_chord_notes(root, ctype)
            harmony.append([
                {"type": "chord", "pitch": cn, "duration": 2.0, "dynamic": "ff"},
                {"type": "chord", "pitch": cn, "duration": 1.0, "dynamic": "f"},
                {"type": "chord", "pitch": cn, "duration": 1.0, "dynamic": "mf"},
            ])
            rh, beat = [], 0.0
            while beat < 4.0:
                dur = max(0.5, self._get_rhythm_duration(metrics, -4.0))
                if beat + dur > 4.0:
                    dur = 4.0 - beat
                pitch = random.choice(scale_e) + 12
                rh.append({"type": "note", "pitch": pitch, "duration": dur, "dynamic": "ff"})
                beat += dur
            melody.append(rh)
        style = metrics.get("memory_style") or {}
        melody, harmony = self._apply_learned_key(melody, harmony, style, 4)
        return {"melody": melody, "harmony": harmony}

    def _generate_waltz(self) -> dict:
        """Walc 8+8 w 3/4. Takt 8 kończy się na kwincie, takt 16 na tonice."""
        metrics = self._get_soul_metrics()
        style = metrics.get("memory_style") or {}
        is_minor = bool(style.get("has_data")) and float(style.get("key_mode", 1.0)) < 0.5
        degrees = [0, 5, 0, 7, 0, 5, 7, 7, 7, 7, 0, 5, 0, 5, 7, 0]
        melody, harmony = [], []
        for index, degree in enumerate(degrees):
            root = 48 + degree
            ctype = "min" if is_minor and degree in (0, 5) else "maj"
            chord_notes = self._build_chord_notes(root, ctype)
            harmony.append([
                {"type": "note", "pitch": root - 12, "duration": 1.0, "dynamic": "mf"},
                {"type": "chord", "pitch": chord_notes, "duration": 1.0, "dynamic": "mp"},
                {"type": "chord", "pitch": chord_notes, "duration": 1.0, "dynamic": "mp"},
            ])
            if index == 7:
                melody.append(self._quarter_bar(65, 65, 67))
            elif index == 15:
                third = 63 if is_minor else 64
                melody.append(self._quarter_bar(third, 62, 60))
            else:
                melody.append(self._waltz_running(metrics, chord_notes))
        melody, harmony = self._apply_learned_key(melody, harmony, style, 0)
        return {"melody": melody, "harmony": harmony}

    def _quarter_bar(self, a: int, b: int, c: int) -> list:
        return [
            {"type": "note", "pitch": a, "duration": 1.0, "dynamic": "mf"},
            {"type": "note", "pitch": b, "duration": 1.0, "dynamic": "mf"},
            {"type": "note", "pitch": c, "duration": 1.0, "dynamic": "f"},
        ]

    def _waltz_running(self, metrics: dict, chord_notes: list) -> list:
        tones = [n + 12 for n in chord_notes]
        events = []
        beat = 0.0
        i = 0
        while beat < 3.0 - 1e-9:
            dur = self._get_rhythm_duration(metrics)
            if dur <= 0:
                dur = 1.0
            if beat + dur > 3.0:
                dur = 3.0 - beat
            events.append({
                "type": "note",
                "pitch": tones[i % len(tones)],
                "duration": dur,
                "dynamic": "mf",
            })
            beat += dur
            i += 1
        return events

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
