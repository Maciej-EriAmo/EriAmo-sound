# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Generatory menuetu: Mozart Würfelspiel i Joseph Riepel."""
import random


class MenuetMixin:
    # ============= STYLE HISTORYCZNE MENUETÓW =============
    
    MENUET_MASTERS = {
        'MOZART_DICE': {
            'name': 'Mozart Würfelspiel K.516f',
            'era': 'Klasycyzm (1787)',
            'description': 'Muzyczna gra w kości - tablica 176 taktów, losowanie daje menueta',
            'characteristics': {
                'polyphonic_tendency': 0.2,
                'ornament_density': 0.5,
                'rhythmic_complexity': 0.4,
                'harmonic_richness': 0.6,
                'bass_style': 'simple',
                'melodic_leaps': 0.3,
                'chromaticism': 0.3,
            },
            'typical_patterns': {
                'rhythm': [[1.0, 1.0, 1.0], [2.0, 1.0], [1.0, 2.0]],
                'bass_rhythm': [[3.0]],  # Prosty bas na całą miarę
                'motif_types': ['galant', 'graceful', 'simple'],
                'cadence_style': 'galant',
            },
            'signature_moves': [
                'dice_selection',     # Wybór przez "kości" (sterowane emocjami)
                'modular_phrases',    # Modularne frazy
                'interchangeable'     # Wymienne takty
            ],
            # TABLICA MOZARTA - uproszczona wersja (oryginał ma 176 taktów)
            # Każdy wiersz = wynik rzutu (2-12), każda kolumna = numer taktu (1-8 dla części A, 1-8 dla B)
            # Wartości to indeksy do DICE_MEASURES
            'dice_table_A': [
                # Rzut:  t1   t2   t3   t4   t5   t6   t7   t8
                [96,  22,  141, 41,  105, 122, 11,  30],   # 2
                [32,  6,   128, 63,  146, 46,  134, 81],   # 3
                [69,  95,  158, 13,  153, 55,  110, 24],   # 4
                [40,  17,  113, 85,  161, 2,   159, 100],  # 5
                [148, 74,  163, 45,  80,  97,  36,  107],  # 6
                [104, 157, 27,  167, 154, 68,  118, 91],   # 7
                [152, 60,  171, 53,  99,  133, 21,  127],  # 8
                [119, 84,  114, 50,  140, 86,  169, 94],   # 9
                [98,  142, 42,  156, 75,  129, 62,  123],  # 10
                [3,   87,  165, 61,  135, 47,  147, 33],   # 11
                [54,  130, 10,  103, 28,  37,  106, 5],    # 12
            ],
            'dice_table_B': [
                # Rzut:  t9   t10  t11  t12  t13  t14  t15  t16
                [70,  121, 26,  9,   112, 49,  109, 14],   # 2
                [117, 39,  126, 56,  174, 18,  116, 83],   # 3
                [66,  139, 15,  132, 73,  58,  145, 79],   # 4
                [90,  176, 7,   34,  67,  160, 52,  170],  # 5
                [25,  143, 64,  125, 76,  136, 1,   93],   # 6
                [138, 71,  150, 29,  101, 162, 23,  151],  # 7
                [16,  155, 57,  175, 43,  168, 89,  172],  # 8
                [120, 88,  48,  166, 51,  115, 72,  111],  # 9
                [65,  77,  19,  82,  137, 38,  149, 8],    # 10
                [102, 4,   31,  164, 144, 59,  173, 78],   # 11
                [35,  20,  108, 92,  12,  124, 44,  131],  # 12
            ],
        },
        
        'BACH': {
            'name': 'Johann Sebastian Bach',
            'era': 'Barok (1685-1750)',
            'characteristics': {
                # Styl polifoniczny, kontrapunkt nawet w tańcach
                'polyphonic_tendency': 0.7,      # Wysoka polifonia
                'ornament_density': 0.4,         # Umiarkowane ozdobniki
                'rhythmic_complexity': 0.5,      # Średnia złożoność rytmiczna
                'harmonic_richness': 0.8,        # Bogata harmonika
                'bass_style': 'walking',         # Bas kroczący
                'melodic_leaps': 0.4,            # Umiarkowane skoki
                'sequence_probability': 0.6,     # Częste sekwencje
            },
            'typical_patterns': {
                'rhythm': [[1.0, 1.0, 1.0], [1.0, 0.5, 0.5, 1.0], [0.5, 0.5, 0.5, 0.5, 1.0]],
                'bass_rhythm': [[1.0, 1.0, 1.0], [0.5, 0.5, 0.5, 0.5, 1.0]],  # Bas ruchliwy
                'motif_types': ['ascending', 'descending', 'sequence'],
                'cadence_style': 'elaborate',    # Rozbudowane kadencje
            },
            'signature_moves': [
                'counterpoint_bass',      # Bas kontrapunktujący
                'sequential_development', # Rozwinięcie sekwencyjne
                'invertible_counterpoint' # Kontrapunkt odwracalny
            ]
        },
        
        'MOZART': {
            'name': 'Wolfgang Amadeus Mozart',
            'era': 'Klasycyzm (1756-1791)',
            'characteristics': {
                'polyphonic_tendency': 0.3,      # Homofonia dominuje
                'ornament_density': 0.6,         # Więcej ornamentów (tryle, mordenty)
                'rhythmic_complexity': 0.4,      # Elegancka prostota
                'harmonic_richness': 0.6,        # Klarowna harmonika
                'bass_style': 'alberti',         # Bas Albertiego
                'melodic_leaps': 0.3,            # Głównie ruch krokowy
                'chromaticism': 0.4,             # Subtelna chromatyka
            },
            'typical_patterns': {
                'rhythm': [[1.0, 1.0, 1.0], [2.0, 1.0], [1.0, 0.5, 0.5, 1.0]],
                'bass_rhythm': [[1.0, 1.0, 1.0]],  # Prosty, regularny bas
                'motif_types': ['arch', 'descending', 'graceful'],
                'cadence_style': 'galant',
            },
            'signature_moves': [
                'alberti_bass',           # Bas Albertiego (rozkładany akord)
                'grace_notes',            # Przednutki
                'chromatic_approach',     # Chromatyczne podejścia
                'singing_melody'          # Melodia śpiewna
            ]
        },
        
        'HANDEL': {
            'name': 'Georg Friedrich Händel',
            'era': 'Barok (1685-1759)',
            'characteristics': {
                'polyphonic_tendency': 0.5,      # Mieszanka
                'ornament_density': 0.5,         # Umiarkowane
                'rhythmic_complexity': 0.6,      # Punktowane rytmy!
                'harmonic_richness': 0.7,        # Bogata
                'bass_style': 'stately',         # Dostojny, majestatyczny
                'melodic_leaps': 0.5,            # Więcej skoków (fanfarowe)
                'dotted_rhythm': 0.7,            # PUNKTOWANE RYTMY - cecha charakterystyczna
            },
            'typical_patterns': {
                'rhythm': [[1.5, 0.5, 1.0], [1.0, 1.5, 0.5], [1.5, 1.5]],  # Punktowane!
                'bass_rhythm': [[1.5, 0.5, 1.0], [1.0, 1.0, 1.0]],
                'motif_types': ['fanfare', 'stately', 'dotted'],
                'cadence_style': 'majestic',
            },
            'signature_moves': [
                'dotted_rhythm',          # Rytm punktowany
                'fanfare_leaps',          # Skoki fanfarowe (kwarty, kwinty)
                'hemiola',                # Hemiola (3+3 → 2+2+2)
                'terraced_dynamics'       # Dynamika tarasowa
            ]
        },
        
        'HAYDN': {
            'name': 'Joseph Haydn',
            'era': 'Klasycyzm (1732-1809)',
            'characteristics': {
                'polyphonic_tendency': 0.4,
                'ornament_density': 0.3,         # Oszczędne ozdobniki
                'rhythmic_complexity': 0.5,
                'harmonic_richness': 0.5,
                'bass_style': 'supportive',      # Wspierający
                'melodic_leaps': 0.4,
                'humor': 0.6,                    # Element humoru/zaskoczenia!
            },
            'typical_patterns': {
                'rhythm': [[1.0, 1.0, 1.0], [1.0, 2.0], [0.5, 0.5, 1.0, 1.0]],
                'bass_rhythm': [[1.0, 1.0, 1.0], [2.0, 1.0]],
                'motif_types': ['arch', 'repeated', 'surprising'],
                'cadence_style': 'witty',
            },
            'signature_moves': [
                'surprise_pause',         # Niespodziewana pauza
                'witty_turn',             # Dowcipny zwrot
                'folk_element',           # Element ludowy
                'unexpected_dynamic'      # Niespodziewana dynamika
            ]
        },
        
        'RIEPEL': {
            'name': 'Joseph Riepel (teoretyk)',
            'era': 'Galant (1709-1782)',
            'characteristics': {
                'polyphonic_tendency': 0.2,      # Czysta homofonia
                'ornament_density': 0.3,         # Oszczędne
                'rhythmic_complexity': 0.3,      # Prosta, taneczna
                'harmonic_richness': 0.4,        # Klarowna
                'bass_style': 'galant',          # Typowy galant
                'melodic_leaps': 0.2,            # Ruch krokowy
            },
            'typical_patterns': {
                'rhythm': [[1.0, 1.0, 1.0], [2.0, 1.0], [1.0, 2.0]],
                'bass_rhythm': [[1.0, 1.0, 1.0]],
                'motif_types': ['ascending', 'descending', 'arch'],
                'cadence_style': 'textbook',
            },
            'signature_moves': [
                'perfect_symmetry',       # Idealna symetria 4+4
                'clear_cadence',          # Czytelne kadencje
                'stepwise_motion'         # Ruch sekundowy
            ]
        }
    }

    # ============= MENUET (RIEPEL'S THEORY - FULL IMPLEMENTATION) =============
    
    def _generate_menuet_polyphonic(self, tonic: int = 60, master_style: str = None) -> dict:
        """
        Menuet według zasad Josepha Riepela (1709-1782)
        z traktatów "Anfangsgründe zur musikalischen Setzkunst".
        
        NOWOŚĆ: System mieszania stylów historycznych!
        Gdy ciekawość jest wysoka, system losuje kombinację:
        - Bazowy styl (np. Riepel)
        - + cechy drugiego mistrza (np. rytmy Händla)
        
        NOWOŚĆ v6: Tonacja z pamięci!
        System uczy się preferowanych tonacji z analizowanych utworów.
        
        Struktura 16-taktowa (A: 8 taktów + B: 8 taktów):
        
        CZĘŚĆ A (Satz):
          - Vordersatz (t.1-4): motyw → półkadencja (Halbschluss) na V
          - Nachsatz (t.5-8): odpowiedź → pełna kadencja (Ganzschluss) I
          
        CZĘŚĆ B (Fortspinnung + Rückgang):
          - Fortspinnung (t.9-12): rozwinięcie, modulacja do V lub vi
          - Rückgang (t.13-16): powrót do I, kadencja końcowa
        
        Args:
            tonic: MIDI nuta toniki (domyślnie 60 = C4)
            master_style: Wymuszony styl ('BACH', 'MOZART', etc.) lub None dla auto
        """
        metrics = self._get_soul_metrics()
        
        # === WYBÓR STYLU NA PODSTAWIE CIEKAWOŚCI ===
        style_config = self._select_menuet_style(metrics, master_style)
        
        # === NOWE: TONACJA Z PAMIĘCI ===
        memory_style = metrics.get('memory_style', {})
        tonic, is_minor = self._resolve_tonic(tonic, memory_style)
        
        # Stopnie skali od toniki
        I = tonic
        II = tonic + 2
        IV = tonic + 5
        V = tonic + 7
        VI = tonic + 9
        
        # === SKALA: DUR lub MOLL na podstawie pamięci ===
        if is_minor:
            # Skala molowa naturalna (2 oktawy)
            # T-S-T-T-S-T-T = 0,2,3,5,7,8,10
            scale = [tonic + i for i in [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24]]
            # Korekta stopni dla moll
            II = tonic + 2
            IV = tonic + 5
            V = tonic + 7
            VI = tonic + 8  # mała seksta w mollu
        else:
            # Skala durowa (2 oktawy)
            # T-T-S-T-T-T-S = 0,2,4,5,7,9,11
            scale = [tonic + i for i in [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]]
        
        # === CHROMATYKA z pamięci ===
        chromatic_density = memory_style.get('chromatic_density', 0.0)
        if chromatic_density > 0.15:  # Jeśli utwory uczące miały chromatykę
            # Dodaj nuty chromatyczne do skali
            chromatic_notes = []
            for i in range(len(scale) - 1):
                if scale[i + 1] - scale[i] > 1:
                    chromatic_notes.append(scale[i] + 1)
            scale = sorted(set(scale + chromatic_notes))
        
        # Generuj motyw 2-taktowy z wybranym stylem
        motif = self._riepel_generate_motif(tonic, scale, metrics, style_config)
        
        melody, harmony = [], []
        
        # ==================== CZĘŚĆ A: SATZ (8 taktów) ====================
        
        # --- Vordersatz (t.1-4): motyw → półkadencja na V ---
        
        # Takt 1-2: Motyw główny (I)
        melody.extend(motif['melody'])
        harmony.extend(self._riepel_bass_pattern(I, 'I', 2))
        
        # Takt 3: Przejście do dominanty
        m3_melody = self._riepel_transition_measure(scale, V, metrics, direction='up')
        melody.append(m3_melody)
        harmony.extend(self._riepel_bass_pattern(IV, 'IV', 1))
        
        # Takt 4: Półkadencja (Halbschluss) - zatrzymanie na V
        m4_melody = self._riepel_half_cadence_melody(V, scale)
        melody.append(m4_melody)
        harmony.extend(self._riepel_bass_pattern(V, 'V_HC', 1))
        
        # --- Nachsatz (t.5-8): odpowiedź → pełna kadencja I ---
        
        # Takt 5-6: Wariant motywu (odpowiedź)
        answer = self._riepel_generate_answer(motif, scale, metrics)
        melody.extend(answer['melody'])
        harmony.extend(self._riepel_bass_pattern(I, 'I', 1))
        harmony.extend(self._riepel_bass_pattern(IV, 'IV', 1))
        
        # Takt 7: Przygotowanie kadencji
        m7_melody = self._riepel_precadence_measure(scale, V, metrics)
        melody.append(m7_melody)
        harmony.extend(self._riepel_bass_pattern(V, 'V7', 1))
        
        # Takt 8: Pełna kadencja (Ganzschluss) - V→I
        m8_melody = self._riepel_full_cadence_melody(I, scale)
        melody.append(m8_melody)
        harmony.extend(self._riepel_bass_pattern(I, 'I_CAD', 1))
        
        # ==================== CZĘŚĆ B: FORTSPINNUNG + RÜCKGANG (8 taktów) ====================
        
        # --- Fortspinnung (t.9-12): rozwinięcie, MODULACJA DO DOMINANTY ---
        # Riepel: Część B często moduluje do V (dominanty) jako nowej toniki
        # W C-dur: modulacja do G-dur (V = nowe I)
        
        # Skala dominanty (G-dur jeśli tonika to C)
        dominant_scale = [V + i for i in [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]]
        
        # Takt 9-10: Motyw TRANSPONOWANY do dominanty
        fort_motif = self._riepel_fortspinnung_motif(motif, V, dominant_scale, metrics)
        melody.extend(fort_motif['melody'])
        # Harmonia: G jako nowe I, potem D jako nowe V
        harmony.extend(self._riepel_bass_pattern(V, 'I_DOM', 1))      # t.9: G (= I w G-dur)
        harmony.extend(self._riepel_bass_pattern(V + 7, 'V_DOM', 1))  # t.10: D (= V w G-dur)
        
        # Takt 11: Sekwencja opadająca (powrót do C-dur)
        m11_melody = self._riepel_sequence_measure(scale, VI, metrics)
        melody.append(m11_melody)
        harmony.extend(self._riepel_bass_pattern(VI, 'vi', 1))  # t.11: A (vi) - pivot
        
        # Takt 12: Dominanta głównej tonacji (przygotowanie powrotu)
        m12_melody = self._riepel_transition_measure(scale, V, metrics, direction='down')
        melody.append(m12_melody)
        harmony.extend(self._riepel_bass_pattern(V, 'V_RETURN', 1))  # t.12: G (V) - powrót
        
        # --- Rückgang (t.13-16): powrót do I, kadencja końcowa ---
        
        # Takt 13-14: Powrót do tonacji głównej
        ruck_motif = self._riepel_ruckgang_motif(motif, I, scale, metrics)
        melody.extend(ruck_motif['melody'])
        harmony.extend(self._riepel_bass_pattern(I, 'I', 1))
        harmony.extend(self._riepel_bass_pattern(IV, 'IV', 1))
        
        # Takt 15: Przygotowanie kadencji końcowej
        m15_melody = self._riepel_precadence_measure(scale, V, metrics)
        melody.append(m15_melody)
        harmony.extend(self._riepel_bass_pattern(V, 'V7', 1))
        
        # Takt 16: Finalna kadencja (Ganzschluss)
        m16_melody = self._riepel_final_cadence_melody(I, scale)
        melody.append(m16_melody)
        harmony.extend(self._riepel_bass_pattern(I, 'I_FINAL', 1))
        
        return {
            'melody': melody, 
            'harmony': harmony,
            'structure': {
                'form': 'Binary (A:||:B:||)',
                'A_repeat': (0, 8),
                'B_repeat': (8, 16),
                'tonic': tonic
            },
            'style_info': style_config  # Informacje o użytym stylu
        }
    
    def _emotion_dice_roll(self, metrics: dict) -> int:
        """
        Rzut kośćmi sterowany emocjami i pamięcią.
        
        Zamiast losowego 2-12, wynik jest modulowany przez stan duszy:
        - Wysokie emocje → wyższe wyniki (bardziej dramatyczne takty)
        - Niska energia → niższe wyniki (spokojniejsze takty)
        - Wysoka kreacja → większa wariancja
        
        Returns:
            int: Wynik "rzutu" 2-12
        """
        emocje = metrics.get('emocje', 0)
        kreacja = metrics.get('kreacja', 50)
        improv = metrics.get('improwizacja', 0)
        
        # Bazowy rzut (symulacja 2 kości)
        base_roll = random.randint(1, 6) + random.randint(1, 6)
        
        # Modulacja emocjonalna
        emotion_mod = emocje / 50  # -2 do +2
        
        # Modulacja kreacji (więcej wariancji)
        if kreacja > 60:
            variance = random.randint(-2, 2)
        else:
            variance = random.randint(-1, 1)
        
        # Improwizacja pozwala na "oszustwo" w kościach
        if improv > 50 and random.random() < 0.3:
            # Czasem wybierz skrajny wynik
            base_roll = random.choice([2, 3, 11, 12])
        
        result = base_roll + int(emotion_mod) + variance
        return max(2, min(12, result))  # Ogranicz do 2-12
    
    def _generate_menuet_mozart_dice(self, tonic: int = 60) -> dict:
        """
        Menuet wygenerowany metodą Mozarta Würfelspiel (K.516f).
        
        Zamiast algorytmicznego generowania, używamy tablicy taktów
        i "rzutów kośćmi" sterowanych emocjami.
        
        To daje bardziej "mozartowski" rezultat - każdy takt jest 
        stylistycznie spójny, a losowość daje różnorodność.
        
        NAPRAWIONE: Bas jest synchronizowany z melodią!
        """
        metrics = self._get_soul_metrics()
        memory_style = metrics.get('memory_style', {})
        
        # Pobierz tablice kości
        dice_master = self.MENUET_MASTERS.get('MOZART_DICE', {})
        table_A = dice_master.get('dice_table_A', [])
        table_B = dice_master.get('dice_table_B', [])
        
        if not table_A or not table_B:
            # Fallback do Riepela jeśli brak tablic
            return self._generate_menuet_polyphonic(tonic, 'MOZART')
        
        tonic, is_minor = self._resolve_tonic(tonic, memory_style)
        
        # Skala
        if is_minor:
            scale = [tonic + i for i in [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24]]
        else:
            scale = [tonic + i for i in [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]]
        
        I = tonic
        V = tonic + 7
        IV = tonic + 5
        
        melody = []
        harmony = []
        dice_results = []
        
        # === CZĘŚĆ A: 8 taktów ===
        for measure_idx in range(8):
            # Rzut kośćmi (sterowany emocjami)
            roll = self._emotion_dice_roll(metrics)
            dice_results.append(roll)
            
            # Pobierz indeks taktu z tablicy (roll-2 bo tablica od 0, rzut od 2)
            table_idx = roll - 2
            if table_idx < len(table_A) and measure_idx < len(table_A[table_idx]):
                measure_id = table_A[table_idx][measure_idx]
            else:
                measure_id = random.randint(1, 176)
            
            # Generuj takt na podstawie ID (uproszczone - generuj w stylu Mozarta)
            measure_notes = self._generate_dice_measure(measure_id, scale, metrics, measure_idx, 'A')
            melody.append(measure_notes)
            
            # === BAS ZSYNCHRONIZOWANY Z MELODIĄ ===
            bass_measure = self._mozart_consonant_bass(measure_notes, tonic, measure_idx, 'A', is_minor)
            harmony.append(bass_measure)
        
        # === CZĘŚĆ B: 8 taktów ===
        for measure_idx in range(8):
            roll = self._emotion_dice_roll(metrics)
            dice_results.append(roll)
            
            table_idx = roll - 2
            if table_idx < len(table_B) and measure_idx < len(table_B[table_idx]):
                measure_id = table_B[table_idx][measure_idx]
            else:
                measure_id = random.randint(1, 176)
            
            measure_notes = self._generate_dice_measure(measure_id, scale, metrics, measure_idx, 'B')
            melody.append(measure_notes)
            
            # === BAS ZSYNCHRONIZOWANY Z MELODIĄ ===
            bass_measure = self._mozart_consonant_bass(measure_notes, tonic, measure_idx, 'B', is_minor)
            harmony.append(bass_measure)
        
        return {
            'melody': melody,
            'harmony': harmony,
            'structure': {
                'form': 'Mozart Würfelspiel (A:||:B:||)',
                'A_repeat': (0, 8),
                'B_repeat': (8, 16),
                'tonic': tonic,
                'dice_results': dice_results  # Wyniki "rzutów"
            },
            'style_info': {
                'primary_master': 'MOZART_DICE',
                'primary_name': 'Mozart Würfelspiel K.516f',
                'dice_rolls': dice_results,
                'characteristics': dice_master.get('characteristics', {}),
            }
        }
    
    def _mozart_consonant_bass(self, melody_notes: list, tonic: int, measure_idx: int, 
                                section: str, is_minor: bool = False) -> list:
        """
        Generuje bas w stylu Mozarta, ZSYNCHRONIZOWANY z melodią.
        
        Zasady:
        1. Bas gra nuty konsonansowe względem melodii (tercje, kwinty, oktawy)
        2. Prosty rytm (głównie jedna nuta na takt lub bas Albertiego)
        3. Harmonia zależy od pozycji w formie
        """
        bass_notes = []
        
        # Określ akord na podstawie pozycji w formie
        # Część A: I-I-I-I-V-V-I-I (uproszczone)
        # Część B: V-V-ii-V-I-IV-V-I
        if section == 'A':
            chord_progression = [0, 0, 0, 5, 7, 7, 0, 0]  # Względem toniki
        else:  # B
            chord_progression = [7, 7, 2, 7, 0, 5, 7, 0]
        
        chord_offset = chord_progression[measure_idx] if measure_idx < len(chord_progression) else 0
        chord_root = tonic + chord_offset
        
        # Znajdź dominującą nutę melodii w tym takcie
        if melody_notes:
            melody_pitches = [n['pitch'] for n in melody_notes if n.get('type') == 'note']
            if melody_pitches:
                # Pierwsza nuta taktu jest najważniejsza
                melody_first = melody_pitches[0]
            else:
                melody_first = tonic + 12  # Fallback
        else:
            melody_first = tonic + 12
        
        # === ZNAJDŹ KONSONANSOWY BAS ===
        # Konsonanse: unison (0), tercja (3,4), kwinta (7), oktawa (12)
        consonant_intervals = [0, 3, 4, 7, 8, 9, 12]  # Dodałem sekstę (8,9) też OK
        
        # Bazowy bas to korzeń akordu, ale przesuń o oktawę w dół
        bass_pitch = chord_root - 12  # Oktawa niżej niż tonika
        if bass_pitch < 36:  # Nie za nisko (C2)
            bass_pitch = chord_root
        
        # Sprawdź czy bas jest konsonansowy z melodią
        interval_to_melody = abs(melody_first - bass_pitch) % 12
        
        if interval_to_melody not in consonant_intervals:
            # Szukaj najbliższego konsonansu
            best_bass = bass_pitch
            best_distance = 100
            
            for cons in consonant_intervals:
                # Spróbuj nuty która tworzy konsonans z melodią
                candidate = melody_first - cons
                while candidate < 36:  # Nie za nisko
                    candidate += 12
                while candidate > 60:  # Nie za wysoko dla basu
                    candidate -= 12
                
                # Preferuj nuty bliskie korzeniowi akordu
                distance = abs(candidate % 12 - chord_root % 12)
                if distance < best_distance:
                    best_distance = distance
                    best_bass = candidate
            
            bass_pitch = best_bass
        
        # === RYTM BASU (prosty, mozartowski) ===
        # Wybór stylu: prosta nuta na takt lub bas Albertiego
        if measure_idx in [3, 7, 11, 15]:  # Kadencje - prosta nuta
            bass_notes.append({
                'type': 'note', 
                'pitch': bass_pitch, 
                'duration': 3.0,  # Cały takt
                'dynamic': 'mf'
            })
        elif random.random() < 0.6:  # 60% - prosty bas
            bass_notes.append({
                'type': 'note',
                'pitch': bass_pitch,
                'duration': 3.0,
                'dynamic': 'mp'
            })
        else:  # 40% - bas Albertiego (rozkładany akord)
            # Tercja i kwinta nad basem
            third = bass_pitch + (3 if is_minor else 4)
            fifth = bass_pitch + 7
            
            # Wzór Albertiego: bas-kwinta-tercja lub bas-tercja-kwinta
            if random.random() < 0.5:
                pattern = [bass_pitch, fifth, third]
            else:
                pattern = [bass_pitch, third, fifth]
            
            for i, p in enumerate(pattern):
                bass_notes.append({
                    'type': 'note',
                    'pitch': p,
                    'duration': 1.0,
                    'dynamic': 'mp' if i > 0 else 'mf'
                })
        
        return bass_notes
    
    def _generate_dice_measure(self, measure_id: int, scale: list, metrics: dict, 
                               measure_idx: int, section: str) -> list:
        """
        Generuje pojedynczy takt w stylu mozartowskiej gry w kości.
        
        measure_id determinuje "charakter" taktu (w oryginale to były zapisane takty).
        My generujemy je algorytmicznie, ale measure_id wpływa na wybór wzorca.
        """
        memory_style = metrics.get('memory_style', {})
        improv = metrics.get('improv_params', {})
        freedom = improv.get('freedom_level', 0.5)
        
        # measure_id wpływa na charakter taktu
        pattern_type = measure_id % 8  # 8 typów wzorców
        
        # Typowe rytmy mozartowskie dla menueta
        rhythms = [
            [1.0, 1.0, 1.0],           # 0: równe ćwierćnuty
            [2.0, 1.0],                 # 1: półnuta + ćwierćnuta
            [1.0, 2.0],                 # 2: ćwierćnuta + półnuta
            [1.0, 0.5, 0.5, 1.0],       # 3: ćwierć + dwie ósemki + ćwierć
            [0.5, 0.5, 0.5, 0.5, 1.0],  # 4: cztery ósemki + ćwierć
            [1.0, 0.5, 0.5, 0.5, 0.5],  # 5: ćwierć + cztery ósemki
            [1.5, 0.5, 1.0],            # 6: punktowana (bardziej händlowska)
            [0.5, 0.5, 1.0, 1.0],       # 7: dwie ósemki + dwie ćwierćnuty
        ]
        
        rhythm = rhythms[pattern_type]
        
        # Wzorce melodyczne zależne od pozycji w formie
        if section == 'A':
            if measure_idx == 0:
                # Początek - akord toniczny
                start_idx = random.choice([0, 2, 4])  # I, III, V stopień
            elif measure_idx == 3 or measure_idx == 7:
                # Kadencja - kieruj do toniki lub dominanty
                start_idx = random.choice([0, 4])
            else:
                start_idx = random.randint(0, len(scale) // 2)
        else:  # B
            if measure_idx == 0:
                # Początek B - często od dominanty
                start_idx = 4  # V stopień
            elif measure_idx == 7:
                # Zakończenie - tonika
                start_idx = 0
            else:
                start_idx = random.randint(0, len(scale) // 2)
        
        # Generuj nuty
        notes = []
        current_idx = start_idx
        
        for i, dur in enumerate(rhythm):
            # Dynamika
            dyn = 'mf' if i == 0 else 'mp'
            
            # Pitch
            pitch = scale[min(current_idx, len(scale) - 1)]
            notes.append({'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': dyn})
            
            # Ruch melodyczny (typowy dla Mozarta - głównie krokowy z okazjonalnymi skokami)
            if random.random() < 0.7:  # 70% kroki
                step = random.choice([-1, 1, 1, -1, 0])
            else:  # 30% skoki
                step = random.choice([-2, 2, -3, 3])
            
            # Pamięć może zwiększyć skoki
            if memory_style.get('leap_ratio', 0.3) > 0.5:
                if random.random() < 0.3:
                    step = random.choice([-3, -2, 2, 3, 4])
            
            current_idx = max(0, min(len(scale) - 1, current_idx + step))
        
        return notes
    
    def _select_menuet_style(self, metrics: dict, forced_style: str = None) -> dict:
        """
        Wybiera styl menuetu na podstawie ciekawości lub wymusza podany.
        
        Gdy ciekawość wysoka → mieszanka stylów (np. Riepel + Händel)
        Gdy niska → czysty styl
        
        Returns:
            dict z konfiguracją stylu do użycia
        """
        available_masters = list(self.MENUET_MASTERS.keys())
        
        # Jeśli wymuszony styl
        if forced_style and forced_style.upper() in available_masters:
            primary = forced_style.upper()
            secondary = None
        else:
            stored = metrics.get("curiosity")
            if isinstance(stored, dict) and "value" in stored:
                curiosity_value = float(stored["value"])
            else:
                try:
                    from amocore_v59 import get_curiosity_engine
                    engine = get_curiosity_engine()
                    curiosity = engine.compute_curiosity(
                        metrics.get("kreacja", 0),
                        metrics.get("wiedza", 0),
                        metrics.get("emocje", 0),
                    )
                    curiosity_value = curiosity["value"]
                except Exception:
                    curiosity_value = 0

            if curiosity_value > 60:
                primary = random.choice(available_masters)
                secondary = random.choice([m for m in available_masters if m != primary])
                self.core.log(
                    f"[STYLE] Wysoka ciekawość ({curiosity_value:.0f}) → fuzja: {primary} + {secondary}",
                    "CYAN",
                )
            elif curiosity_value > 20:
                # ŚREDNIA: Losowy pojedynczy styl
                primary = random.choice(available_masters)
                secondary = None
            else:
                # NISKA: Domyślny Riepel
                primary = 'RIEPEL'
                secondary = None
        
        # Buduj konfigurację
        primary_style = self.MENUET_MASTERS[primary]
        
        config = {
            'primary_master': primary,
            'primary_name': primary_style['name'],
            'secondary_master': secondary,
            'characteristics': primary_style['characteristics'].copy(),
            'patterns': primary_style['typical_patterns'].copy(),
            'signature_moves': primary_style['signature_moves'].copy(),
            'fusion': secondary is not None
        }
        
        # Jeśli fuzja - mieszaj cechy
        if secondary:
            secondary_style = self.MENUET_MASTERS[secondary]
            config['secondary_name'] = secondary_style['name']
            
            # Mieszaj charakterystyki (średnia ważona: 60% primary, 40% secondary)
            for key, val in secondary_style['characteristics'].items():
                if key in config['characteristics']:
                    config['characteristics'][key] = (
                        0.6 * config['characteristics'][key] + 0.4 * val
                    )
            
            # Dodaj wzorce z secondary
            for key, patterns in secondary_style['typical_patterns'].items():
                if key in config['patterns']:
                    config['patterns'][key] = config['patterns'][key] + patterns
            
            # Dodaj signature moves z secondary
            config['signature_moves'].extend(secondary_style['signature_moves'])
        
        return config

    def _riepel_generate_motif(self, tonic: int, scale: list, metrics: dict, style_config: dict = None) -> dict:
        """
        Generuje 2-taktowy motyw z uwzględnieniem stylu historycznego.
        
        Zasady bazowe (Riepel):
        - Prosta, taneczna rytmika
        - Na beat 1: dźwięki akordowe
        - Bez dramatycznych skoków (max tercja/kwarta)
        
        STYLE HISTORYCZNE modyfikują:
        - BACH: Sekwencje, kontrapunkt, ruchliwy bas
        - MOZART: Melodia śpiewna, bas Albertiego, przednutki
        - HÄNDEL: Rytmy punktowane, skoki fanfarowe, hemiola
        - HAYDN: Element zaskoczenia, dowcipne zwroty
        
        PAMIĘĆ MUZYCZNA wpływa na:
        - repetition_density → ilość powtórzeń
        - leap_ratio → skoki vs kroki
        - syncopation_feel → nierówności rytmiczne
        """
        melody_measures = []
        
        # Pobierz parametry improwizacji
        improv = metrics.get('improv_params', {})
        freedom = improv.get('freedom_level', 0.5)
        allow_leaps = improv.get('allow_large_leaps', False)
        ornament_density = improv.get('ornamentation_density', 0.5)
        
        # === NOWE: Pobierz styl z pamięci ===
        memory_style = metrics.get('memory_style', {})
        mem_repetition = memory_style.get('repetition_density', 0.3)
        mem_leaps = memory_style.get('leap_ratio', 0.3)
        mem_syncopation = memory_style.get('syncopation_feel', 0.2)
        mem_regularity = memory_style.get('rhythmic_regularity', 0.5)
        
        # Moduluj parametry na podstawie pamięci
        if mem_leaps > 0.5:
            allow_leaps = True  # Pamięć nauczyła skoków
        
        # Pobierz charakterystyki stylu (jeśli dostępne)
        if style_config:
            char = style_config.get('characteristics', {})
            patterns = style_config.get('patterns', {})
            signatures = style_config.get('signature_moves', [])
            master = style_config.get('primary_master', 'RIEPEL')
        else:
            char = {}
            patterns = {}
            signatures = []
            master = 'RIEPEL'
        
        # Znajdź indeks toniki w skali
        tonic_idx = 0
        for i, p in enumerate(scale):
            if p % 12 == tonic % 12:
                tonic_idx = i
                break
        
        # === ROZSZERZONA PULA DŹWIĘKÓW (na podstawie pamięci) ===
        # Bazowe dźwięki akordowe toniki (I, III, V, I')
        chord_indices = [tonic_idx, tonic_idx + 2, tonic_idx + 4, tonic_idx + 7]
        chord_indices = [i for i in chord_indices if i < len(scale)]
        
        # PAMIĘĆ: Rozszerz pulę dźwięków jeśli system nauczył się różnorodności
        pitch_variance = memory_style.get('pitch_variance', 0.3)
        dominant_pitch = memory_style.get('dominant_pitch_class', 0.0)
        
        # Dostępne dźwięki (rozszerzane przez pamięć)
        if pitch_variance > 0.6:
            # Wysoka wariancja - używaj CAŁEJ skali + chromatyki
            available_indices = list(range(len(scale)))
            # Dodaj nuty chromatyczne między stopniami
            chromatic_additions = []
            for idx in available_indices[:-1]:
                if idx + 1 < len(scale) and scale[idx + 1] - scale[idx] > 1:
                    chromatic_additions.append(scale[idx] + 1)
            # Rozszerz skalę
            extended_scale = sorted(set(scale + chromatic_additions))
        elif pitch_variance > 0.4:
            # Średnia wariancja - cała skala diatoniczna
            available_indices = list(range(len(scale)))
            extended_scale = scale
        else:
            # Niska wariancja - głównie akordy
            available_indices = chord_indices
            extended_scale = scale
        
        # PAMIĘĆ: Preferuj pewne stopnie skali na podstawie tego czego się nauczył
        # dominant_pitch_class jest znormalizowany 0-1 (0=C, 0.5=F#, 1.0=B)
        preferred_pitch_class = int(dominant_pitch * 11)  # 0-11
        
        # Znajdź indeksy w skali które odpowiadają preferowanej klasie
        preferred_indices = []
        for i, p in enumerate(extended_scale if pitch_variance > 0.4 else scale):
            if p % 12 == preferred_pitch_class:
                preferred_indices.append(i)
        
        # Wagi dla wyboru dźwięków początkowych
        # Jeśli pamięć preferuje inną nutę niż tonika, zwiększ jej szansę
        start_weights = {}
        for idx in available_indices:
            if idx in preferred_indices:
                start_weights[idx] = 3.0  # Preferowana przez pamięć
            elif idx in chord_indices:
                start_weights[idx] = 2.0  # Akord toniczny
            else:
                start_weights[idx] = 1.0  # Reszta skali
        
        # === WYBÓR TYPU MOTYWU (zależny od stylu, improwizacji I PAMIĘCI) ===
        if patterns.get('motif_types'):
            motif_types = patterns['motif_types']
        elif freedom < 0.3:
            motif_types = ['ascending', 'descending', 'repeated']
        elif freedom < 0.7:
            motif_types = ['ascending', 'descending', 'arch', 'pendulum', 'repeated']
        else:
            motif_types = ['ascending', 'descending', 'arch', 'pendulum', 'repeated', 'chromatic', 'leaping']
        
        # PAMIĘĆ: Jeśli nauczyła powtórzeń, dodaj więcej repeated
        if mem_repetition > 0.5:
            motif_types.extend(['repeated', 'repeated'])
        
        # PAMIĘĆ: Jeśli nauczyła skoków, dodaj leaping
        if mem_leaps > 0.5 and 'leaping' not in motif_types:
            motif_types.append('leaping')
        
        # Specjalne typy dla mistrzów
        if master == 'HANDEL' and random.random() < 0.5:
            motif_types.append('fanfare')
            motif_types.append('dotted')
        elif master == 'BACH' and random.random() < 0.5:
            motif_types.append('sequence')
        elif master == 'HAYDN' and random.random() < 0.3:
            motif_types.append('surprising')
        
        motif_type = random.choice(motif_types)
        
        # === WYBÓR RYTMU (zależny od stylu) ===
        if patterns.get('rhythm'):
            # Użyj rytmów z wybranego stylu
            rhythm_patterns = patterns['rhythm']
        elif freedom < 0.3:
            rhythm_patterns = [
                [1.0, 1.0, 1.0],
                [2.0, 1.0],
                [1.0, 2.0],
            ]
        elif freedom < 0.6:
            rhythm_patterns = [
                [1.0, 1.0, 1.0],
                [1.0, 0.5, 0.5, 1.0],
                [2.0, 1.0],
                [1.0, 2.0],
                [0.5, 0.5, 1.0, 1.0],
                [1.0, 1.0, 0.5, 0.5],
                [1.5, 1.5],
            ]
        else:
            rhythm_patterns = [
                [1.0, 1.0, 1.0],
                [1.0, 0.5, 0.5, 1.0],
                [0.5, 0.5, 1.0, 1.0],
                [1.0, 1.0, 0.5, 0.5],
                [1.5, 1.5],
                [1.0, 0.5, 0.5, 0.5, 0.5],
                [0.5, 0.5, 0.5, 0.5, 1.0],
                [0.75, 0.25, 1.0, 1.0],
            ]
        
        # HÄNDEL: preferuj rytmy punktowane
        if master == 'HANDEL' and char.get('dotted_rhythm', 0) > 0.5:
            dotted_rhythms = [[1.5, 0.5, 1.0], [1.0, 1.5, 0.5], [1.5, 1.5]]
            rhythm_patterns = dotted_rhythms + rhythm_patterns
        
        rhythm1 = random.choice(rhythm_patterns)
        rhythm2 = random.choice(rhythm_patterns)
        
        # === Takt 1: Początek motywu ===
        m1 = []
        
        # Wybierz początkową nutę (teraz z uwzględnieniem pamięci!)
        if pitch_variance > 0.4 and start_weights:
            # Użyj wag z pamięci
            weighted_options = []
            for idx, weight in start_weights.items():
                if idx < len(extended_scale if pitch_variance > 0.4 else scale):
                    weighted_options.extend([idx] * int(weight * 2))
            if weighted_options:
                start_options = weighted_options
            else:
                start_options = [tonic_idx, tonic_idx + 2, tonic_idx + 4]
        else:
            start_options = [tonic_idx, tonic_idx + 2, tonic_idx + 4]
        
        # HÄNDEL: preferuj skoki (fanfarowe początki)
        if master == 'HANDEL' and 'fanfare_leaps' in signatures:
            start_options = [tonic_idx, tonic_idx + 4, tonic_idx + 7]  # I, V, I'
        
        # Użyj rozszerzonej skali jeśli wysoka wariancja
        working_scale = extended_scale if pitch_variance > 0.4 else scale
        
        start_idx = random.choice([i for i in start_options if i < len(working_scale)])
        current_idx = start_idx
        
        for i, dur in enumerate(rhythm1):
            dyn = 'mf' if i == 0 else 'mp'
            
            # HAYDN: niespodziewana dynamika
            if master == 'HAYDN' and 'unexpected_dynamic' in signatures and random.random() < 0.2:
                dyn = 'f' if dyn == 'mp' else 'p'
            
            pitch = working_scale[min(current_idx, len(working_scale) - 1)]
            
            # MOZART: przednutki (grace notes)
            if master == 'MOZART' and 'grace_notes' in signatures and i == 0 and random.random() < 0.3:
                # Dodaj przednutkę (nie zmienia struktury, tylko atrybut)
                grace_pitch = working_scale[min(current_idx + 1, len(working_scale) - 1)]
                m1.append({'type': 'note', 'pitch': grace_pitch, 'duration': 0.125, 'dynamic': 'mp', 'grace': True})
            
            m1.append({'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': dyn})
            
            # Ruch melodyczny zależny od typu motywu
            if motif_type == 'ascending':
                step = random.choice([1, 1, 2])
            elif motif_type == 'descending':
                step = random.choice([-1, -1, -2])
            elif motif_type == 'arch':
                step = 1 if i < len(rhythm1) // 2 else -1
            elif motif_type == 'pendulum':
                step = 1 if i % 2 == 0 else -1
            elif motif_type == 'fanfare':
                # HÄNDEL: skoki kwartowe/kwintowe
                step = random.choice([-4, -3, 3, 4, 5])
            elif motif_type == 'dotted':
                step = random.choice([1, 2, -1])
            elif motif_type == 'sequence':
                # BACH: sekwencja (powtórzenie wzoru o sekundę niżej)
                step = -2 if i > 0 else random.choice([1, 2])
            elif motif_type == 'surprising':
                # HAYDN: niespodziewany zwrot
                step = random.choice([-3, -2, 0, 0, 2, 3])
            elif motif_type == 'graceful':
                # MOZART: elegancki ruch krokowy
                step = random.choice([-1, 1, 1])
            elif motif_type == 'chromatic' and freedom > 0.6:
                step = random.choice([-1, 1])
            elif motif_type == 'leaping' and allow_leaps:
                step = random.choice([-3, -2, 2, 3, 4])
            else:  # repeated
                step = random.choice([0, 0, 1, -1])
            
            # PAMIĘĆ: Zwiększ zakres skoków jeśli wysoka wariancja
            if pitch_variance > 0.5 and random.random() < pitch_variance:
                step = int(step * 1.5)  # Większe skoki
            
            current_idx = max(0, min(len(working_scale) - 1, current_idx + step))
        
        melody_measures.append(m1)
        
        # === Takt 2: Kontynuacja/zamknięcie motywu ===
        m2 = []
        
        # Punkt docelowy (zależny od pamięci!)
        if pitch_variance > 0.5 and preferred_indices:
            # Preferuj zakończenie na nucie z pamięci
            target_options = preferred_indices + [tonic_idx + 2, tonic_idx + 4]
        else:
            target_options = [tonic_idx + 2, tonic_idx + 4, tonic_idx]
        
        target_idx = random.choice([i for i in target_options if i < len(working_scale)])
        
        for i, dur in enumerate(rhythm2):
            dyn = 'mf' if i == 0 else 'mp'
            
            if i == len(rhythm2) - 1:
                final_idx = target_idx
            else:
                direction = 1 if target_idx > current_idx else -1
                if current_idx != target_idx:
                    current_idx += direction * random.choice([0, 1, 1])
                final_idx = current_idx
            
            pitch = working_scale[min(max(0, final_idx), len(working_scale) - 1)]
            m2.append({'type': 'note', 'pitch': pitch, 'duration': dur, 'dynamic': dyn})
        
        melody_measures.append(m2)
        
        return {
            'melody': melody_measures, 
            'last_idx': target_idx, 
            'motif_type': motif_type,
            'style': master
        }

    def _riepel_generate_answer(self, motif: dict, scale: list, metrics: dict) -> dict:
        """
        Generuje odpowiedź na motyw (Nachsatz) - wariant prowadzący do kadencji.
        """
        melody_measures = []
        
        answer_techniques = ['transpose_down', 'invert', 'rhythmic_variation', 'sequence']
        technique = random.choice(answer_techniques)
        
        # Losowy interwał transpozycji
        transpose_interval = random.choice([-1, -2, -3])  # sekunda, tercja, kwarta w dół
        
        for m_idx, orig_measure in enumerate(motif['melody']):
            new_measure = []
            
            for n_idx, note in enumerate(orig_measure):
                new_note = note.copy()
                orig_pitch = note['pitch']
                
                try:
                    idx = scale.index(orig_pitch)
                except ValueError:
                    idx = len(scale) // 2
                
                if technique == 'transpose_down':
                    # Prosta transpozycja w dół
                    new_idx = max(0, idx + transpose_interval)
                    
                elif technique == 'invert':
                    # Inwersja - jeśli oryginał szedł w górę, odpowiedź idzie w dół
                    if n_idx > 0:
                        prev_pitch = orig_measure[n_idx - 1]['pitch']
                        try:
                            prev_idx = scale.index(prev_pitch)
                            orig_direction = idx - prev_idx
                            new_idx = max(0, min(len(scale) - 1, idx - orig_direction))
                        except ValueError:
                            new_idx = max(0, idx - 1)
                    else:
                        new_idx = max(0, idx + transpose_interval)
                        
                elif technique == 'rhythmic_variation':
                    # Zachowaj wysokość, zmień rytm (obsługiwane przez zmianę duration)
                    new_idx = max(0, idx + random.choice([-1, 0, 0]))
                    # Losowa zmiana rytmu
                    if random.random() > 0.5:
                        new_note['duration'] = max(0.5, note['duration'] * random.choice([0.5, 1.0, 1.5]))
                        
                else:  # sequence
                    # Sekwencja - powtórzenie wzoru na innej wysokości
                    sequence_offset = -2 if m_idx == 0 else -4
                    new_idx = max(0, idx + sequence_offset)
                
                new_note['pitch'] = scale[min(new_idx, len(scale) - 1)]
                new_measure.append(new_note)
            
            # Normalizuj długości do 3.0 (takt 3/4)
            total_dur = sum(n['duration'] for n in new_measure)
            if total_dur != 3.0 and new_measure:
                # Dostosuj ostatnią nutę
                diff = 3.0 - sum(n['duration'] for n in new_measure[:-1])
                new_measure[-1]['duration'] = max(0.5, diff)
            
            melody_measures.append(new_measure)
        
        return {'melody': melody_measures}
    
    def _riepel_bass_pattern(self, root: int, function: str, measures: int) -> list:
        """
        Generuje wzorzec basowy w stylu galant.
        Bas krokowy, wspierający kadencje, bez dominacji.
        
        Funkcje harmoniczne:
        - 'I', 'IV', 'V': podstawowe stopnie
        - 'V_HC': półkadencja (zatrzymanie na V)
        - 'V7': dominanta septymowa przed kadencją
        - 'I_CAD': kadencja pełna
        - 'I_FINAL': kadencja końcowa (mocna)
        - 'I_DOM': I w kontekście modulacji do dominanty
        - 'V_DOM': V w kontekście dominanty (= II głównej)
        - 'V_RETURN': V przygotowujące powrót do toniki
        - 'ii', 'vi': akordy poboczne
        """
        patterns = []
        bass = root - 12  # Oktawa niżej
        
        for _ in range(measures):
            m = []
            
            if function == 'I':
                # I-V-I lub I-III-V (styl galant)
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 1.0, 'dynamic': 'mp'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 1.0, 'dynamic': 'p'})
                
            elif function == 'IV':
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 2.0, 'dynamic': 'mp'})
                
            elif function == 'V':
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 1.0, 'dynamic': 'mp'})
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mp'})
                
            elif function == 'V_HC':
                # Półkadencja - zatrzymanie na V (Halbschluss)
                m.append({'type': 'note', 'pitch': bass, 'duration': 2.0, 'dynamic': 'mf'})
                m.append({'type': 'rest', 'duration': 1.0})
                
            elif function == 'V7':
                # Dominanta septymowa przed kadencją
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'f'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7, bass + 10], 'duration': 2.0, 'dynamic': 'mf'})
                
            elif function == 'I_CAD':
                # Kadencja pełna (Ganzschluss)
                m.append({'type': 'note', 'pitch': bass, 'duration': 2.0, 'dynamic': 'f'})
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                
            elif function == 'I_FINAL':
                # Kadencja końcowa (mocna, z fermatą)
                m.append({'type': 'note', 'pitch': bass, 'duration': 3.0, 'dynamic': 'f'})
            
            # === FUNKCJE MODULACYJNE (Fortspinnung) ===
            
            elif function == 'I_DOM':
                # I w kontekście dominanty (G jako nowe I)
                # Lżejszy, bardziej taneczny charakter
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mp'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 1.0, 'dynamic': 'p'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 1.0, 'dynamic': 'p'})
                
            elif function == 'V_DOM':
                # V w kontekście dominanty (D jako V/V)
                # Akord durowy z septymą
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 2.0, 'dynamic': 'mp'})
                
            elif function == 'V_RETURN':
                # V przygotowujące powrót (napięcie przed tonika)
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'f'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7, bass + 10], 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                
            elif function in ['ii', 'vi']:
                # Akordy poboczne (molowe)
                third = 3  # tercja mała
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mp'})
                m.append({'type': 'chord', 'pitch': [bass + third, bass + 7], 'duration': 2.0, 'dynamic': 'p'})
                
            else:
                # Domyślny wzorzec
                m.append({'type': 'note', 'pitch': bass, 'duration': 1.0, 'dynamic': 'mf'})
                m.append({'type': 'chord', 'pitch': [bass + 4, bass + 7], 'duration': 2.0, 'dynamic': 'mp'})
            
            patterns.append(m)
        
        return patterns
    
    def _riepel_transition_measure(self, scale: list, target: int, metrics: dict, direction: str = 'up') -> list:
        """Takt przejściowy - ruch skalowy do celu z losową wariacją."""
        m = []
        # Znajdź cel w skali
        target_idx = 0
        for i, p in enumerate(scale):
            if p % 12 == target % 12:
                target_idx = i
                break
        
        # Losowy wybór typu przejścia
        transition_type = random.choice(['scalar', 'skip', 'decorated'])
        
        if transition_type == 'scalar':
            # Ruch skalowy (3 ćwierćnuty)
            if direction == 'up':
                indices = [max(0, target_idx - 2), max(0, target_idx - 1), target_idx]
            else:
                indices = [min(len(scale) - 1, target_idx + 2), min(len(scale) - 1, target_idx + 1), target_idx]
            
            for i, idx in enumerate(indices):
                dyn = 'mf' if i == 0 else 'mp'
                m.append({'type': 'note', 'pitch': scale[idx], 'duration': 1.0, 'dynamic': dyn})
                
        elif transition_type == 'skip':
            # Skok + wypełnienie
            start_idx = target_idx + (3 if direction == 'up' else -3)
            start_idx = max(0, min(len(scale) - 1, start_idx))
            m.append({'type': 'note', 'pitch': scale[start_idx], 'duration': 1.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': scale[target_idx], 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': scale[target_idx], 'duration': 1.0, 'dynamic': 'mp'})
            
        else:  # decorated
            # Ozdobiony ruch z ósemkami
            if direction == 'up':
                idx1 = max(0, target_idx - 2)
                idx2 = max(0, target_idx - 1)
            else:
                idx1 = min(len(scale) - 1, target_idx + 2)
                idx2 = min(len(scale) - 1, target_idx + 1)
            
            m.append({'type': 'note', 'pitch': scale[idx1], 'duration': 1.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': scale[idx2], 'duration': 0.5, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': scale[target_idx], 'duration': 0.5, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': scale[target_idx], 'duration': 1.0, 'dynamic': 'mf'})
        
        return m
    
    def _riepel_half_cadence_melody(self, dominant: int, scale: list) -> list:
        """Melodia półkadencji - zatrzymanie na dominancie z losową wariacją."""
        m = []
        
        # Losowy wybór wariantu półkadencji
        variant = random.choice(['simple', 'decorated', 'suspension'])
        
        if variant == 'simple':
            # Prosta - długa nuta
            m.append({'type': 'note', 'pitch': dominant + 12, 'duration': 2.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': dominant + 12 + random.choice([0, 4, 7]), 'duration': 1.0, 'dynamic': 'p'})
            
        elif variant == 'decorated':
            # Ozdobiona
            m.append({'type': 'note', 'pitch': dominant + 12 + 7, 'duration': 1.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': dominant + 12 + 4, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': dominant + 12, 'duration': 1.0, 'dynamic': 'mf'})
            
        else:  # suspension
            # Z zawieszeniem
            m.append({'type': 'note', 'pitch': dominant + 12 + 5, 'duration': 1.5, 'dynamic': 'mf'})  # sus4
            m.append({'type': 'note', 'pitch': dominant + 12 + 4, 'duration': 1.5, 'dynamic': 'mp'})  # rozwiązanie
        
        return m
    
    def _riepel_precadence_measure(self, scale: list, dominant: int, metrics: dict) -> list:
        """Takt przed kadencją - napięcie z losową wariacją."""
        m = []
        leading_tone = dominant + 4  # VII stopień (tercja dominanty)
        
        # Losowy wybór figury przed-kadencyjnej
        figure = random.choice(['standard', 'chromatic', 'arpeggio'])
        
        if figure == 'standard':
            # Standardowa: VII - V - VII
            m.append({'type': 'note', 'pitch': leading_tone + 12, 'duration': 1.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': dominant + 12, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': leading_tone + 12, 'duration': 1.0, 'dynamic': 'mf'})
            
        elif figure == 'chromatic':
            # Chromatyczna: VI# - VII
            m.append({'type': 'note', 'pitch': dominant + 12 + 2, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': leading_tone + 12 - 1, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': leading_tone + 12, 'duration': 1.0, 'dynamic': 'f'})
            
        else:  # arpeggio
            # Arpeggio dominanty
            m.append({'type': 'note', 'pitch': dominant + 12, 'duration': 1.0, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': leading_tone + 12, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': dominant + 12 + 7, 'duration': 1.0, 'dynamic': 'mf'})
        
        return m
    
    def _riepel_full_cadence_melody(self, tonic: int, scale: list) -> list:
        """Melodia pełnej kadencji - rozwiązanie na tonikę z wariacją."""
        m = []
        
        # Losowy wybór zakończenia
        ending = random.choice(['simple', 'triumphant', 'gentle'])
        
        if ending == 'simple':
            m.append({'type': 'note', 'pitch': tonic + 12, 'duration': 2.0, 'dynamic': 'f'})
            m.append({'type': 'note', 'pitch': tonic + 12, 'duration': 1.0, 'dynamic': 'mf'})
            
        elif ending == 'triumphant':
            # Wysoka tonika
            m.append({'type': 'note', 'pitch': tonic + 24, 'duration': 1.5, 'dynamic': 'f'})
            m.append({'type': 'note', 'pitch': tonic + 12 + 7, 'duration': 0.5, 'dynamic': 'mf'})
            m.append({'type': 'note', 'pitch': tonic + 12, 'duration': 1.0, 'dynamic': 'mf'})
            
        else:  # gentle
            m.append({'type': 'note', 'pitch': tonic + 12 + 4, 'duration': 1.0, 'dynamic': 'mp'})
            m.append({'type': 'note', 'pitch': tonic + 12, 'duration': 2.0, 'dynamic': 'mf'})
        
        return m
    
    def _riepel_fortspinnung_motif(self, orig_motif: dict, new_tonic: int, new_scale: list, metrics: dict) -> dict:
        """
        Fortspinnung - rozwinięcie motywu w nowej tonacji (dominancie).
        
        Techniki Riepela dla Fortspinnung:
        1. Transpozycja motywu o kwintę w górę
        2. Inwersja (odbicie melodii)
        3. Augmentacja/diminucja rytmiczna
        4. Sekwencja (powtórzenie na innej wysokości)
        
        Args:
            orig_motif: Oryginalny motyw z części A
            new_tonic: Nowa tonika (dominanta = V stopień)
            new_scale: Skala nowej tonacji
            metrics: Metryki duszy (wpływają na wybór techniki)
        """
        melody_measures = []
        
        # Wybierz technikę na podstawie metryk
        kreacja = metrics.get('kreacja', 0)
        
        # Transpozycja o kwintę w górę (podstawowa technika)
        interval = 7  # kwinta czysta
        
        for m_idx, orig_measure in enumerate(orig_motif['melody']):
            new_measure = []
            
            for n_idx, note in enumerate(orig_measure):
                new_note = note.copy()
                
                # Transpozycja
                transposed_pitch = note['pitch'] + interval
                
                # Opcjonalna inwersja dla drugiego taktu (kreacja > 30)
                if m_idx == 1 and kreacja > 30:
                    # Inwersja względem pierwszej nuty taktu
                    if n_idx == 0:
                        pivot = transposed_pitch
                    else:
                        # Odbij interwał
                        original_interval = note['pitch'] - orig_measure[0]['pitch']
                        transposed_pitch = pivot - original_interval
                
                # Dopasuj do skali dominanty (unikaj fałszywych dźwięków)
                new_note['pitch'] = self._snap_to_scale(transposed_pitch, new_scale)
                
                # Delikatniejsza dynamika w Fortspinnung (kontrast z A)
                dyn_map = {'f': 'mf', 'mf': 'mp', 'mp': 'p'}
                new_note['dynamic'] = dyn_map.get(note.get('dynamic', 'mf'), 'mp')
                
                new_measure.append(new_note)
            
            melody_measures.append(new_measure)
        
        return {'melody': melody_measures}
    
    def _snap_to_scale(self, pitch: int, scale: list) -> int:
        """Dopasowuje wysokość do najbliższego dźwięku w skali."""
        if pitch in scale:
            return pitch
        # Znajdź najbliższy dźwięk w skali
        closest = min(scale, key=lambda x: abs(x - pitch))
        return closest
    
    def _riepel_sequence_measure(self, scale: list, target: int, metrics: dict) -> list:
        """Takt sekwencyjny - powtórzenie wzoru na innej wysokości."""
        m = []
        # Prosta sekwencja opadająca
        target_idx = 0
        for i, p in enumerate(scale):
            if p % 12 == target % 12:
                target_idx = i
                break
        
        # Trzy ćwierćnuty opadające
        for offset in [2, 1, 0]:
            idx = min(len(scale) - 1, target_idx + offset)
            m.append({'type': 'note', 'pitch': scale[idx], 'duration': 1.0, 'dynamic': 'mp'})
        
        return m
    
    def _riepel_ruckgang_motif(self, orig_motif: dict, tonic: int, scale: list, metrics: dict) -> dict:
        """
        Rückgang - powrót do tonacji głównej.
        Przypomnienie motywu, prowadzące do końca.
        """
        melody_measures = []
        
        # Użyj oryginalnego motywu, ale z modyfikacjami kadencyjnymi
        for m_idx, orig_measure in enumerate(orig_motif['melody']):
            new_measure = []
            for note in orig_measure:
                new_note = note.copy()
                # Możliwa drobna wariacja
                if random.random() > 0.7 and metrics['kreacja'] > 20:
                    # Ozdobnik
                    new_note['duration'] = max(0.5, note['duration'] - 0.5)
                new_measure.append(new_note)
            melody_measures.append(new_measure)
        
        return {'melody': melody_measures}
    
    def _riepel_final_cadence_melody(self, tonic: int, scale: list) -> list:
        """Finalna kadencja - mocne zakończenie na tonice."""
        m = []
        # Tonika z fermata (dłuższa wartość)
        m.append({'type': 'note', 'pitch': tonic + 12, 'duration': 3.0, 'dynamic': 'f', 'fermata': True})
        return m
