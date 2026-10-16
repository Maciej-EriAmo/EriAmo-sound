# music_analyzer_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
Analizator Muzyczny EriAmo v5.9.1 [COMPATIBILITY FIX]
- Dostosowany do rdzenia v5.9.1 (brak osi 'etyka', nowa oś 'improwizacja')
- Mapowanie cech "etycznych" na Affections (Wzniosłość) i Improwizację (Porządek)
"""
import numpy as np
from amocore_v59 import AXES_LIST, EPHEMERAL_AXES


class MusicAnalyzer:
    """
    Analizator przekształcający cechy muzyczne na wektory wpływu.
    """
    AXES_MAP = {axis: i for i, axis in enumerate(AXES_LIST)}
    AXES_COUNT = len(AXES_LIST)
    
    # Współczynniki mapowania cech na osie.
    # Wartość może być krotką (axis_idx, value) LUB listą krotek [(idx, val), (idx, val)]
    COEFFICIENTS = {
        # === LOGIKA ===
        "FUGA": (AXES_MAP['logika'], 7.0),
        "KANON": (AXES_MAP['logika'], 5.0),
        "MENUET": (AXES_MAP['logika'], 2.5),
        "ZLOZONY": (AXES_MAP['logika'], 3.0),
        "PUNK": (AXES_MAP['logika'], -2.0),
        "JAZZ": (AXES_MAP['logika'], 6.0),
        "PROSTY": (AXES_MAP['logika'], -1.0),
        "MATH": (AXES_MAP['logika'], 8.0),
        
        # === WIEDZA ===
        "BAROQUE": (AXES_MAP['wiedza'], 3.0),
        "KLASYCYZM": (AXES_MAP['wiedza'], 4.0),
        "ROMANTYZM": (AXES_MAP['wiedza'], 4.0),
        "HISTORYCZNY": (AXES_MAP['wiedza'], 5.0),
        
        # === AFFECTIONS (Pamięć głęboka / Emocje wyższe) ===
        "DOLCE": (AXES_MAP['affections'], 3.0),
        "CON_FUOCO": (AXES_MAP['affections'], 6.0),
        "LAMENTOSO": (AXES_MAP['affections'], -6.0),
        "INTYMNA": (AXES_MAP['affections'], 4.0),
        "HEAVY_METAL": (AXES_MAP['affections'], -5.0),
        "TRAGEDIA": (AXES_MAP['affections'], -8.0),
        "WZNIOSLY": (AXES_MAP['affections'], 7.0),
        "NOSTALGICZNY": (AXES_MAP['affections'], -3.0),
        "CHWALA": (AXES_MAP['affections'], 8.0),
        
        # === BYT (Istnienie, Fizyczność) ===
        "LIVE": (AXES_MAP['byt'], 5.0),
        "RAW": (AXES_MAP['byt'], 4.0),
        "ACOUSTIC": (AXES_MAP['byt'], 3.0),
        "BASS": (AXES_MAP['byt'], 4.0),
        "HEAVY": (AXES_MAP['byt'], 5.0),
        "SYNTH": (AXES_MAP['byt'], -2.0),
        "DIGITAL": (AXES_MAP['byt'], -3.0),
        "LOFI": (AXES_MAP['byt'], 2.0),
        
        # === IMPROWIZACJA (Swoboda vs Porządek) - ZASTĘPUJE ETYKĘ ===
        # Wartości ujemne = Porządek/Rytuał (dawniej wysoka Etyka)
        # Wartości dodatnie = Chaos/Swoboda (dawniej niska Etyka)
        
        "HEROIC": (AXES_MAP['affections'], 6.0),      # Heroizm to teraz uczucie chwały
        "SACRED": [
            (AXES_MAP['affections'], 7.0),            # Wzniosłość
            (AXES_MAP['improwizacja'], -5.0)          # Rytuał (Porządek)
        ],
        "EPIC": (AXES_MAP['affections'], 5.0),
        
        "HARMONIA": (AXES_MAP['improwizacja'], -3.0), # Porządek
        "DISSONANCE": (AXES_MAP['improwizacja'], 3.0),# Nieporządek
        "DARK": (AXES_MAP['affections'], -4.0),
        "SATANIC": [
            (AXES_MAP['affections'], -5.0),           # Mrok
            (AXES_MAP['improwizacja'], 8.0)           # Bunt/Chaos
        ],
        
        # === Cechy ZŁOŻONE ===
        "POWER_METAL": [
            (AXES_MAP['affections'], 6.0), # Pozytywna energia
            (AXES_MAP['byt'], 4.0),        # Mocne uderzenie
            (AXES_MAP['czas'], 5.0),       # Szybkość
            (AXES_MAP['improwizacja'], -2.0) # Dyscyplina rytmiczna
        ],
        "CHAOS": [
            (AXES_MAP['logika'], -6.0),    # Burzy logikę
            (AXES_MAP['kreacja'], 4.0),    # Rodzi gwiazdy
            (AXES_MAP['improwizacja'], 10.0) # Totalna swoboda
        ],
        "REGGAE": [
            (AXES_MAP['czas'], -2.0),      # Laid back
            (AXES_MAP['affections'], 3.0), # Positive vibration
            (AXES_MAP['improwizacja'], 3.0) # Luz
        ],
        "DRAMATYCZNY": [
            (AXES_MAP['emocje'], 8.0),     # Wysokie pobudzenie
            (AXES_MAP['affections'], -2.0) # Napięcie
        ],

        # === EMOCJE (Efemeryczne) ===
        "EKSTAZA": (AXES_MAP['emocje'], 15.0),
        "GNIEW": (AXES_MAP['emocje'], -12.0),
        "WESOLY": (AXES_MAP['emocje'], 5.0),
        "MELANCHOLIA": (AXES_MAP['emocje'], -3.0),
        "RADOSC": (AXES_MAP['emocje'], 6.0),
        "SMUTEK": (AXES_MAP['emocje'], -5.0),
        "EUFORIA": (AXES_MAP['emocje'], 10.0),
        
        # === CZAS ===
        "ALLEGRO": (AXES_MAP['czas'], 3.0),
        "PRESTO": (AXES_MAP['czas'], 5.0),
        "ADAGIO": (AXES_MAP['czas'], -3.0),
        "ROCK": (AXES_MAP['czas'], 4.0),
        "POP": (AXES_MAP['czas'], 2.0),
        
        # === PRZESTRZEŃ ===
        "AMBIENT": (AXES_MAP['przestrzen'], 4.0),
        "REVERB": (AXES_MAP['przestrzen'], 3.0),
        "ORKIESTROWY": (AXES_MAP['przestrzen'], 5.0),
        "KOSMICZNY": (AXES_MAP['przestrzen'], 8.0),
        "ECHO": (AXES_MAP['przestrzen'], 4.0),
        "STEREO": (AXES_MAP['przestrzen'], 2.0),
        
        # === KREACJA ===
        "IMPROWIZACJA": (AXES_MAP['kreacja'], 4.0),
        "PROG_ROCK": (AXES_MAP['kreacja'], 7.0),
        "EKSPERYMENTALNY": (AXES_MAP['kreacja'], 6.0),
    }

    def __init__(self, core, logger):
        self.core = core
        self.logger = logger

    def calculate_change_vector(self, features: list) -> np.ndarray:
        F = np.zeros(self.AXES_COUNT)
        recognized = []
        unknown = []
        
        seen = set()
        unique = []
        for feature in features:
            key = str(feature).upper().strip()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(feature)

        for f in unique:
            key = f.upper().strip()
            if key in self.COEFFICIENTS:
                entry = self.COEFFICIENTS[key]
                if isinstance(entry, list):
                    for idx, val in entry:
                        F[idx] += val
                else:
                    idx, val = entry
                    F[idx] += val
                recognized.append(key)
            else:
                unknown.append(key)
        
        if unknown:
            self.core.log(f"[UWAGA] Nierozpoznane cechy: {unknown}", "YELLOW")
        return F

    def analyze_and_shift(self, features: list, description: str, mode: str = "!teach"):
        self.core.apply_time_based_decay()
        F_bazowe = self.calculate_change_vector(features)
        scale = 0.1 if mode == "!simulate" else 1.0
        F_final = F_bazowe * scale

        is_compressed, cos_alpha = self.core.check_ontological_compression(F_bazowe)
        emotion = self._get_emotion(cos_alpha, F_bazowe[self.AXES_MAP['affections']])

        for i, axis in enumerate(self.core.AXES):
            if F_final[i] != 0:
                self.core.shift_axis(axis, "INCREMENT", F_final[i])

        self.core.log(f"\n{'='*50}", "CYAN")
        if is_compressed:
            self.core.log(f"ANALIZA (KOMPRESJA): {description}", "GRAY")
            self.core.log(f"Tożsamość potwierdzona (cos α = {cos_alpha:.4f}).", "GRAY")
        else:
            self.core.log(f"ANALIZA (NOWOŚĆ): {description}", "GREEN")
            self.core.log(f"Zmiana trajektorii (cos α = {cos_alpha:.4f}).", "YELLOW")
        
        self.core.log(f"{'='*50}", "CYAN")
        self.core.log(f"Cechy: {features}", "WHITE")
        self.core.log(f"Interpretacja: {emotion}", "PINK")
        
        self.logger.log_state(self.core, F_final, cos_alpha, emotion, description, mode, compressed=is_compressed)

    def _get_emotion(self, cos_a: float, aff_val: float) -> str:
        if aff_val < -3.0:
            if cos_a < -0.4: return "Konflikt Wewnętrzny"
            else: return "Smutek / Kontemplacja"
        if aff_val > 3.0:
            if cos_a > 0.6: return "Zachwyt / Potwierdzenie"
            else: return "Ciepło / Czułość"
        if cos_a > 0.98: return "Harmonia Całkowita (Tożsamość)"
        elif cos_a > 0.4: return "Akceptacja / Spokój"
        elif cos_a > -0.4: return "Zdziwienie / Nowość"
        else: return "Dystans / Obcość"

    def get_feature_info(self, feature_name: str) -> dict:
        key = feature_name.upper()
        if key not in self.COEFFICIENTS: return {"exists": False}
        entry = self.COEFFICIENTS[key]
        if isinstance(entry, list):
            info_val = entry[0][1]
            axis_name = AXES_LIST[entry[0][0]] + " i inne"
        else:
            info_val = entry[1]
            axis_name = AXES_LIST[entry[0]]
        axes = [AXES_LIST[item[0]] for item in entry] if isinstance(entry, list) else [axis_name]
        ephemeral = any(axis in EPHEMERAL_AXES for axis in axes)
        return {"exists": True, "name": key, "axis": axis_name, "value": info_val, "is_ephemeral": ephemeral}

    def list_all_features(self) -> dict:
        grouped = {axis: [] for axis in AXES_LIST}
        for feature, entry in self.COEFFICIENTS.items():
            if isinstance(entry, list): idx, val = entry[0]
            else: idx, val = entry
            axis = AXES_LIST[idx]
            grouped[axis].append((feature, val))
        for axis in grouped:
            grouped[axis].sort(key=lambda x: x[1], reverse=True)
        return grouped
