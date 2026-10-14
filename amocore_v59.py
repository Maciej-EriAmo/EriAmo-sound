# amocore_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
System Ontologicznej Pamięci Muzyki v5.9.2 [STABLE + SLEEP]
- TRYB: UNBOUNDED (Historia Liniowa, Nieskończony Wzrost)
- FILTR ONTOLOGICZNY: Kompresja redundancji (> 0.98 cos similarity)
- SoulGuard: Integralność SHA-256
- NOWE: Oś IMPROWIZACJA (zamiast etyka) + SZKIELET ETYCZNY (stały)
- NOWE: SYSTEM SNU - konsolidacja pamięci (z dziadka Ai_KuRz5i6)

ARCHITEKTURA DUSZY:
==================
┌─────────────────────────────────────────────────────────┐
│  OSIE (zmienne, -∞ do +∞)                               │
│  ├── logika      : racjonalność vs intuicja            │
│  ├── emocje      : pobudzenie (efemeryczne)            │
│  ├── affections  : pamięć emocjonalna (trwała)         │
│  ├── wiedza      : zgromadzona wiedza                  │
│  ├── czas        : percepcja tempa (efemeryczne)       │
│  ├── kreacja     : potencjał twórczy                   │
│  ├── byt         : egzystencja, tożsamość              │
│  ├── przestrzen  : percepcja przestrzeni               │
│  └── improwizacja: swoboda vs reguły (NOWA)            │
├─────────────────────────────────────────────────────────┤
│  SZKIELET ETYCZNY (stały, niezmienny)                   │
│  ├── integrity   : uczciwość twórcza                   │
│  ├── respect     : szacunek dla tradycji i słuchacza   │
│  ├── authenticity: autentyczność wyrazu                │
│  └── harmony     : dążenie do harmonii (nie chaosu)    │
├─────────────────────────────────────────────────────────┤
│  SYSTEM SNU (konsolidacja pamięci)                      │
│                                                         │
│  WARSTWA 1 (H_log):        WARSTWA 2 (D_Map):          │
│  ┌─────────────────┐  SEN  ┌─────────────────────────┐ │
│  │ Surowe          │ ────► │ Skonsolidowane wzorce   │ │
│  │ doświadczenia   │ 5min  │ - deduplikacja          │ │
│  │ muzyczne        │       │ - wagi rosną z czasem   │ │
│  └─────────────────┘       └─────────────────────────┘ │
│           │                           │                 │
│           ▼ SZKIELET                  ▼ TREŚĆ          │
│       ┌───────────────────────────────────┐            │
│       │        KOMPOZYCJA                 │            │
│       │  struktura z W1 + styl z W2       │            │
│       └───────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
"""
import numpy as np
import threading
import time
import csv
import os
import tempfile
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd

# =============================================================================
# DEFINICJA ONTOLOGICZNA: 9 WEKTORÓW DUSZY
# =============================================================================

AXES_LIST = [
    "logika",       # 0: racjonalność ↔ intuicja
    "emocje",       # 1: pobudzenie emocjonalne (efemeryczne)
    "affections",   # 2: pamięć emocjonalna (trwała, rośnie wolno)
    "wiedza",       # 3: zgromadzona wiedza i doświadczenie
    "czas",         # 4: percepcja tempa (efemeryczne)
    "kreacja",      # 5: potencjał twórczy
    "byt",          # 6: egzystencja, tożsamość
    "przestrzen",   # 7: percepcja przestrzeni dźwiękowej
    "improwizacja"  # 8: NOWA - swoboda twórcza vs ścisłe reguły
]

# Osie podlegające wygaszaniu (efemeryczne - szybko zanikają)
EPHEMERAL_AXES = ["emocje", "czas"]

# Osie trwałe (pamięć głęboka - nie zanikają)
PERSISTENT_AXES = ["affections", "logika", "wiedza", "kreacja", "byt", "przestrzen", "improwizacja"]

# Próg Kompresji Ontologicznej
ONTOLOGICAL_THRESHOLD = 0.98

def _atomic_write_json(path: str, payload) -> None:
    """Zapis JSON przez plik tymczasowy i podmianę, żeby przerwanie nie zostało w połowie pliku."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".eriamo-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


# =============================================================================
# SYSTEM SNU - DWUWARSTWOWA PAMIĘĆ MUZYCZNA
# =============================================================================
"""
Przywrócony z dziadka (Ai_KuRz5i6_en.py).

WARSTWA 1 (H_log - doświadczenia):
- Surowe dane z analizy utworów
- Wektory cech muzycznych
- Krótkoterminowa, nadpisywana

WARSTWA 2 (D_Map - definicje/wzorce):
- Skonsolidowane wzorce muzyczne
- Wagi rosną przy powtórzeniach
- Długoterminowa, kumulatywna

SEN:
- Co 5 minut (konfigurowalny)
- Przenosi wzorce z H_log do D_Map
- Deduplikuje (podobne wzorce → jeden z wyższą wagą)
- Wzmacnia często występujące cechy
"""


class MusicMemory:
    """
    Dwuwarstwowa pamięć muzyczna z mechanizmem snu.
    
    Odpowiada za konsolidację wiedzy z analizowanych utworów.
    """
    
    DATA_DIR = "data"
    H_LOG_PATH = "data/music_experience.json"   # Warstwa 1: surowe doświadczenia
    D_MAP_PATH = "data/music_patterns.json"     # Warstwa 2: skonsolidowane wzorce
    
    # Cechy muzyczne które śledzimy
    MUSICAL_FEATURES = [
        'repetition_density',    # Gęstość powtórzeń (0-1)
        'leap_ratio',            # Stosunek skoków do kroków (0-1)
        'rhythmic_regularity',   # Regularność rytmiczna (0-1)
        'pitch_variance',        # Wariancja wysokości (0-1) - WAŻNE dla różnorodności!
        'note_density',          # Gęstość nut na takt (0-1)
        'interval_avg',          # Średni interwał (znormalizowany)
        'dominant_pitch_class',  # Dominująca klasa wysokości (0-11 → 0-1)
        'syncopation_feel',      # Poczucie synkopy (0-1)
        # NOWE cechy dla większej różnorodności:
        'pitch_range',           # Zakres wysokości (rozpiętość)
        'second_pitch_class',    # Druga najczęstsza nuta
        'chromatic_density',     # Gęstość chromatyki (nuty poza skalą)
        # TONACJA:
        'key_tonic',             # Tonika (0=C, 7/11=G, etc.)
        'key_mode',              # Tryb (1.0=dur, 0.0=moll)
    ]
    
    def __init__(self, sleep_interval: float = 300.0):  # 5 minut domyślnie
        """
        Args:
            sleep_interval: Interwał snu w sekundach (domyślnie 300 = 5 min)
        """
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self._lock = threading.RLock()
        
        # Warstwa 1: Doświadczenia (lista słowników)
        self.H_log = []
        
        # Warstwa 2: Wzorce (słownik z wagami)
        self.D_Map = {}
        
        # Stan snu
        self.sleep_interval = sleep_interval
        self.running = True
        self.is_sleeping = False
        self.last_sleep_time = time.time()
        self.sleep_count = 0
        self.experiences_since_sleep = 0
        
        # Wczytaj zapisane dane
        self._load_memory()
        
        # Uruchom cykl snu w tle
        self._start_sleep_cycle()
        
        print(f"\033[96m[MEMORY] MusicMemory aktywna. Sen co {sleep_interval/60:.1f} min.\033[0m")
    
    def _load_memory(self):
        """Wczytuje pamięć z plików."""
        try:
            if os.path.exists(self.H_LOG_PATH):
                with open(self.H_LOG_PATH, 'r', encoding='utf-8') as f:
                    self.H_log = json.load(f)
        except Exception as e:
            print(f"\033[93m[MEMORY] Nie można wczytać H_log: {e}\033[0m")
            self.H_log = []
        
        try:
            if os.path.exists(self.D_MAP_PATH):
                with open(self.D_MAP_PATH, 'r', encoding='utf-8') as f:
                    self.D_Map = json.load(f)
        except Exception as e:
            print(f"\033[93m[MEMORY] Nie można wczytać D_Map: {e}\033[0m")
            self.D_Map = {}
    
    def _save_memory(self):
        """Zapisuje pamięć do plików. Zamek trzyma spójny odczyt H_log i D_Map."""
        with self._lock:
            try:
                _atomic_write_json(self.H_LOG_PATH, self.H_log[-1000:])
                _atomic_write_json(self.D_MAP_PATH, self.D_Map)
            except Exception as e:
                print(f"\033[91m[MEMORY] Błąd zapisu: {e}\033[0m")
    
    def _start_sleep_cycle(self):
        """Uruchamia cykl snu w osobnym wątku."""
        def cycle():
            while self.running:
                time.sleep(self.sleep_interval)
                if not self.running:
                    break
                self._sleep()
        
        thread = threading.Thread(target=cycle, daemon=True)
        thread.start()
    
    def _sleep(self):
        """
        FAZA SNU - konsolidacja pamięci.
        
        1. Bierze ostatnie doświadczenia z H_log
        2. Ekstrahuje wzorce
        3. Dodaje/wzmacnia w D_Map
        4. Deduplikuje podobne wzorce
        """
        with self._lock:
            self._sleep_locked()

    def _sleep_locked(self):
        """Konsolidacja w tle. Wołane tylko przy trzymanym self._lock."""
        if not self.running:
            return
        self._consolidate_locked()

    def _consolidate_locked(self):
        """Scala świeże doświadczenia do D_Map. Działa także przy zamykaniu."""
        if self.is_sleeping:
            return
        
        self.is_sleeping = True
        start_time = time.time()
        
        print(f"\n\033[96m[SEN] 💤 Zasypiam... przetwarzam {len(self.H_log)} doświadczeń...\033[0m")
        
        processed = 0
        consolidated = 0
        
        # Przetwarzaj ostatnie doświadczenia (max 20)
        recent_experiences = self.H_log[-20:]
        
        for exp in recent_experiences:
            if time.time() - start_time > 5.0:  # Max 5 sekund snu
                break
            
            # Wyodrębnij wzorzec
            pattern_key = self._extract_pattern_key(exp)
            
            if pattern_key in self.D_Map:
                # Wzmocnij istniejący wzorzec
                self.D_Map[pattern_key]['weight'] = min(
                    self.D_Map[pattern_key]['weight'] + 1.0, 
                    100.0
                )
                self.D_Map[pattern_key]['reinforced_count'] += 1
                consolidated += 1
            else:
                # Dodaj nowy wzorzec
                self.D_Map[pattern_key] = {
                    'features': exp.get('features', {}),
                    'weight': 1.0,
                    'source': exp.get('source', 'unknown'),
                    'created_at': datetime.now().isoformat(),
                    'reinforced_count': 0
                }
                processed += 1
        
        # Deduplikacja - połącz bardzo podobne wzorce
        self._deduplicate_patterns()
        
        # Zapisz
        self._save_memory()
        
        # Aktualizuj stan
        self.last_sleep_time = time.time()
        self.sleep_count += 1
        self.experiences_since_sleep = 0
        self.is_sleeping = False
        
        duration = time.time() - start_time
        print(f"\033[92m[SEN] ✨ Obudziłem się! +{processed} nowych wzorców, +{consolidated} wzmocnionych ({duration:.1f}s)\033[0m")
        print(f"\033[92m[SEN] 📊 D_Map: {len(self.D_Map)} wzorców, H_log: {len(self.H_log)} doświadczeń\033[0m\n")
    
    def _extract_pattern_key(self, experience: dict) -> str:
        """
        Generuje klucz wzorca z doświadczenia.
        Podobne doświadczenia → ten sam klucz → konsolidacja.
        """
        features = experience.get('features', {})
        
        # Kwantyzuj cechy do kategorii (low/mid/high)
        def quantize(val, thresholds=(0.33, 0.66)):
            if val < thresholds[0]: return 'L'
            elif val < thresholds[1]: return 'M'
            else: return 'H'
        
        parts = []
        for feat in ['repetition_density', 'leap_ratio', 'rhythmic_regularity', 'syncopation_feel']:
            val = features.get(feat, 0.5)
            parts.append(f"{feat[:3]}:{quantize(val)}")
        tonic_pc = int(round(float(features.get("key_tonic", 0)) * 11)) % 12
        mode = "m" if float(features.get("key_mode", 1)) < 0.5 else "M"
        parts.append(f"ton:{tonic_pc}{mode}")
        
        return "|".join(parts)
    
    def _deduplicate_patterns(self):
        """
        Łączy podobne wzorce - ten z wyższą wagą pochłania słabszy.
        """
        if len(self.D_Map) < 2:
            return
        
        keys = list(self.D_Map.keys())
        merged = set()
        
        for i, k1 in enumerate(keys):
            if k1 in merged:
                continue
            for k2 in keys[i+1:]:
                if k2 in merged:
                    continue
                # Porównaj klucze - jeśli różnią się tylko jedną cechą, połącz
                diff = sum(1 for a, b in zip(k1.split('|'), k2.split('|')) if a != b)
                if diff <= 1:  # Bardzo podobne
                    # Połącz do silniejszego
                    if self.D_Map[k1]['weight'] >= self.D_Map[k2]['weight']:
                        self.D_Map[k1]['weight'] += self.D_Map[k2]['weight'] * 0.5
                        merged.add(k2)
                    else:
                        self.D_Map[k2]['weight'] += self.D_Map[k1]['weight'] * 0.5
                        merged.add(k1)
        
        # Usuń połączone
        for k in merged:
            del self.D_Map[k]
    
    def record_experience(self, features: dict, source: str = "analysis"):
        """
        Zapisuje nowe doświadczenie muzyczne (Warstwa 1).
        
        Args:
            features: Słownik cech muzycznych
            source: Źródło (np. nazwa pliku MIDI)
        """
        with self._lock:
            experience = {
                'timestamp': datetime.now().isoformat(),
                'features': features,
                'source': source,
                'vector': self._features_to_vector(features)
            }
            
            self.H_log.append(experience)
            self.experiences_since_sleep += 1
            
            # Auto-sen jeśli dużo doświadczeń
            if self.experiences_since_sleep > 10:
                print(f"\033[93m[MEMORY] Dużo nowych doświadczeń - wymuszam sen...\033[0m")
                self._sleep()
    
    def _features_to_vector(self, features: dict) -> list:
        """Konwertuje cechy do wektora numerycznego."""
        return [features.get(f, 0.0) for f in self.MUSICAL_FEATURES]
    
    def get_consolidated_style(self) -> dict:
        """
        Zwraca skonsolidowany styl z Warstwy 2 (D_Map).
        
        Używane przez kompozytor do generowania muzyki.
        Ważone średnie cech na podstawie wag wzorców.
        """
        with self._lock:
            return self._consolidated_style_unlocked()

    def _consolidated_style_unlocked(self) -> dict:
        if not self.D_Map:
            return {"has_data": False}
        
        total_weight = sum(p['weight'] for p in self.D_Map.values())
        if total_weight == 0:
            return {"has_data": False}
        
        consolidated = {f: 0.0 for f in self.MUSICAL_FEATURES}
        
        for pattern in self.D_Map.values():
            weight_ratio = pattern['weight'] / total_weight
            for feat, val in pattern.get('features', {}).items():
                if feat in consolidated:
                    consolidated[feat] += val * weight_ratio
        consolidated["has_data"] = True
        return consolidated
    
    def get_recent_style(self) -> dict:
        """
        Zwraca styl z ostatnich doświadczeń (Warstwa 1).
        
        Używane jako "świeża" inspiracja.
        """
        with self._lock:
            return self._recent_style_unlocked()

    def _recent_style_unlocked(self) -> dict:
        if not self.H_log:
            return {"has_data": False}
        
        recent = self.H_log[-5:]
        avg = {f: 0.0 for f in self.MUSICAL_FEATURES}
        
        for exp in recent:
            for feat, val in exp.get('features', {}).items():
                if feat in avg:
                    avg[feat] += val / len(recent)
        avg["has_data"] = True
        return avg
    
    def get_blended_style(self, recent_weight: float = 0.3) -> dict:
        """
        Zwraca zmieszany styl: świeży (W1) + skonsolidowany (W2).
        
        Args:
            recent_weight: Waga świeżych doświadczeń (0-1), reszta to D_Map
            
        Returns:
            dict z cechami muzycznymi do użycia w kompozycji
        """
        with self._lock:
            recent = self._recent_style_unlocked()
            consolidated = self._consolidated_style_unlocked()

        recent_ok = bool(recent.get("has_data"))
        consolidated_ok = bool(consolidated.get("has_data"))
        if not recent_ok and not consolidated_ok:
            return {"has_data": False}
        if recent_ok and not consolidated_ok:
            return dict(recent)
        if consolidated_ok and not recent_ok:
            return dict(consolidated)

        blended = {"has_data": True}
        for feat in self.MUSICAL_FEATURES:
            blended[feat] = (
                recent_weight * recent.get(feat, 0.5) +
                (1 - recent_weight) * consolidated.get(feat, 0.5)
            )
        return blended
    
    def force_sleep(self):
        """Wymusza natychmiastowy sen."""
        self._sleep()
    
    def get_status(self) -> dict:
        """Zwraca status pamięci."""
        with self._lock:
            return {
                'h_log_size': len(self.H_log),
                'd_map_size': len(self.D_Map),
                'total_weight': sum(p['weight'] for p in self.D_Map.values()),
                'sleep_count': self.sleep_count,
                'experiences_since_sleep': self.experiences_since_sleep,
                'is_sleeping': self.is_sleeping,
                'last_sleep': datetime.fromtimestamp(self.last_sleep_time).isoformat(),
            }
    
    def shutdown(self):
        """Zatrzymuje cykl snu, scala zaległe doświadczenia i zapisuje pamięć."""
        with self._lock:
            self.running = False
            if self.experiences_since_sleep > 0 and self.H_log:
                self._consolidate_locked()
            else:
                self._save_memory()
        print(f"\033[93m[MEMORY] Pamięć zapisana. Dobranoc.\033[0m")


# Globalna instancja pamięci
_music_memory = None

def get_music_memory() -> MusicMemory:
    """Zwraca globalną instancję pamięci muzycznej."""
    global _music_memory
    if _music_memory is None:
        _music_memory = MusicMemory()
    return _music_memory


def shutdown_music_memory():
    """Zapisuje pamięć, jeśli kompozycja albo nauka zdążyły ją utworzyć."""
    if _music_memory is not None:
        _music_memory.shutdown()


def analyze_midi_for_learning(midi_path: str) -> dict:
    """Wczytuje MIDI raz i liczy cechy pamięci nut."""
    try:
        from music21 import converter
        score = converter.parse(midi_path)
    except ImportError:
        print("\033[91m[ANALYZE] Brak music21! Zainstaluj: pip install music21\033[0m")
        return {}
    except Exception as e:
        print(f"\033[91m[ANALYZE] Błąd wczytywania MIDI: {e}\033[0m")
        return {}
    return _learning_features_from_score(score)


def _learning_features_from_score(score) -> dict:
    """Cechy pamięci nut z partytury, która jest już wczytana."""
    if score is None:
        return {}
    notes = []
    timings = []

    try:
        from music21 import note as m21_note, chord as m21_chord

        try:
            detected_key = score.analyze('key')
            key_tonic = detected_key.tonic.midi % 12  # 0-11
            key_mode = 1.0 if detected_key.mode == 'major' else 0.0
        except Exception:
            key_tonic = 0  # C
            key_mode = 1.0  # major

        for element in score.flatten().notes:
            if isinstance(element, m21_note.Note):
                notes.append(element.pitch.midi)
                timings.append(float(element.offset))
            elif isinstance(element, m21_chord.Chord):
                # Dla akordów bierzemy wszystkie nuty
                for pitch in element.pitches:
                    notes.append(pitch.midi)
                    timings.append(float(element.offset))
                    
    except ImportError:
        print("\033[91m[ANALYZE] Brak music21! Zainstaluj: pip install music21\033[0m")
        return {}
    except Exception as e:
        print(f"\033[91m[ANALYZE] Błąd wczytywania MIDI: {e}\033[0m")
        return {}
    
    if len(notes) < 5:
        print(f"\033[93m[ANALYZE] Za mało nut w pliku ({len(notes)})\033[0m")
        return {}
    
    # Oblicz cechy
    features = {}
    
    # 1. Gęstość powtórzeń
    repeats = sum(1 for i in range(1, len(notes)) if notes[i] == notes[i-1])
    features['repetition_density'] = min(1.0, repeats / (len(notes) * 0.5))
    
    # 2. Stosunek skoków do kroków
    intervals = [abs(notes[i+1] - notes[i]) for i in range(len(notes)-1)]
    leaps = sum(1 for i in intervals if i > 2)
    features['leap_ratio'] = leaps / len(intervals) if intervals else 0.5
    
    # 3. Regularność rytmiczna
    if len(timings) > 1:
        time_intervals = [timings[i+1] - timings[i] for i in range(len(timings)-1) if timings[i+1] != timings[i]]
        if time_intervals:
            unique_intervals = len(set(time_intervals))
            features['rhythmic_regularity'] = 1.0 - min(1.0, unique_intervals / (len(time_intervals) * 0.5))
        else:
            features['rhythmic_regularity'] = 0.5
    else:
        features['rhythmic_regularity'] = 0.5
    
    # 4. Wariancja wysokości
    pitch_variance = np.std(notes) / 12.0 if len(notes) > 1 else 0.5
    features['pitch_variance'] = min(1.0, pitch_variance)
    
    # 5. Gęstość nut (na "takt" - aproksymacja)
    if timings and max(timings) > 0:
        features['note_density'] = min(1.0, len(notes) / (max(timings) + 1))
    else:
        features['note_density'] = 0.5
    
    # 6. Średni interwał
    features['interval_avg'] = min(1.0, np.mean(intervals) / 12.0) if intervals else 0.5
    
    # 7. Dominująca klasa wysokości
    from collections import Counter
    pitch_classes = [n % 12 for n in notes]
    pitch_counter = Counter(pitch_classes)
    most_common = pitch_counter.most_common(2)
    features['dominant_pitch_class'] = most_common[0][0] / 11.0 if most_common else 0.5
    
    # 8. Poczucie synkopy (nierówność interwałów czasowych)
    if len(timings) > 2:
        time_intervals = [timings[i+1] - timings[i] for i in range(len(timings)-1) if timings[i+1] != timings[i]]
        if time_intervals and np.mean(time_intervals) > 0:
            syncopation = np.std(time_intervals) / np.mean(time_intervals)
            features['syncopation_feel'] = min(1.0, syncopation)
        else:
            features['syncopation_feel'] = 0.0
    else:
        features['syncopation_feel'] = 0.0
    
    # === NOWE CECHY dla większej różnorodności ===
    
    # 9. Zakres wysokości (rozpiętość melodii)
    pitch_range = max(notes) - min(notes) if notes else 0
    features['pitch_range'] = min(1.0, pitch_range / 36.0)  # 36 = 3 oktawy
    
    # 10. Druga najczęstsza nuta (dla bogatszej palety)
    if len(most_common) > 1:
        features['second_pitch_class'] = most_common[1][0] / 11.0
    else:
        features['second_pitch_class'] = features['dominant_pitch_class']
    
    # 11. Gęstość chromatyki (nuty poza skalą diatoniczną C-dur/a-moll)
    diatonic = {0, 2, 4, 5, 7, 9, 11}  # C, D, E, F, G, A, B
    chromatic_count = sum(1 for p in pitch_classes if p not in diatonic)
    features['chromatic_density'] = chromatic_count / len(pitch_classes) if pitch_classes else 0.0
    
    # === NOWE: Tonacja ===
    # 12. Tonika (0-11 znormalizowane do 0-1)
    features['key_tonic'] = key_tonic / 11.0
    
    # 13. Tryb (1.0 = dur, 0.0 = moll)
    features['key_mode'] = key_mode
    
    return features


def learn_from_score(score, source: str) -> dict:
    """Zapisuje cechy gotowej partytury do pamięci nut i zwraca je."""
    features = _learning_features_from_score(score)
    if not features:
        return {}
    get_music_memory().record_experience(features, source)
    return features


def learn_from_midi(midi_path: str) -> bool:
    """Uczy system z pliku MIDI. Jedno wczytanie."""
    try:
        from music21 import converter
        score = converter.parse(midi_path)
    except ImportError:
        print("\033[91m[ANALYZE] Brak music21! Zainstaluj: pip install music21\033[0m")
        return False
    except Exception as e:
        print(f"\033[91m[ANALYZE] Błąd wczytywania MIDI: {e}\033[0m")
        return False
    return bool(learn_from_score(score, os.path.basename(midi_path)))

# =============================================================================
# SZKIELET ETYCZNY (STAŁY, NIEZMIENNY)
# =============================================================================

ETHICS_FRAMEWORK = {
    "integrity": {
        "value": 1.0,  # Zawsze 1.0 (maksymalna uczciwość)
        "description": "Uczciwość twórcza - nie plagiat, nie manipulacja",
        "immutable": True
    },
    "respect": {
        "value": 1.0,
        "description": "Szacunek dla tradycji muzycznej i słuchacza",
        "immutable": True
    },
    "authenticity": {
        "value": 1.0,
        "description": "Autentyczność wyrazu - szczerość artystyczna",
        "immutable": True
    },
    "harmony": {
        "value": 1.0,
        "description": "Dążenie do harmonii, piękna, nie destrukcji",
        "immutable": True
    }
}

def get_ethics_check(action: str) -> bool:
    """
    Sprawdza czy działanie jest zgodne ze szkieletem etycznym.
    Zwraca True jeśli działanie jest etyczne, False jeśli nie.
    
    Przykłady działań nieetycznych:
    - Plagiat (narusza integrity)
    - Celowe tworzenie hałasu dla bólu (narusza harmony)
    - Manipulacja emocjonalna (narusza respect)
    """
    unethical_keywords = [
        "plagiat", "kradzież", "manipulacja", "destrukcja",
        "ból", "cierpienie", "krzywda", "oszustwo"
    ]
    action_lower = action.lower()
    for keyword in unethical_keywords:
        if keyword in action_lower:
            return False
    return True

def get_ethics_report() -> dict:
    """Zwraca raport o stanie szkieletu etycznego."""
    return {
        "status": "INTACT",
        "values": {k: v["value"] for k, v in ETHICS_FRAMEWORK.items()},
        "description": "Szkielet etyczny jest stały i niezmienny",
        "total_integrity": sum(v["value"] for v in ETHICS_FRAMEWORK.values()) / len(ETHICS_FRAMEWORK)
    }


# =============================================================================
# OŚ IMPROWIZACJA - DOKUMENTACJA
# =============================================================================
"""
OŚ IMPROWIZACJA (zastąpiła oś 'etyka'):

Zakres: -100 do +100 (bez twardych limitów)

INTERPRETACJA:
-100 : Ścisłe trzymanie się reguł, zero odstępstw
 -50 : Konserwatywne podejście, minimalne wariacje
   0 : Balans między regułami a swobodą
 +50 : Swobodne podejście, częste wariacje
+100 : Pełna improwizacja, maksymalna swoboda

WPŁYW NA KOMPOZYCJĘ:
- Niska improwizacja (-):
  * Ścisłe schematy harmoniczne
  * Przewidywalne rytmy
  * Klasyczne kadencje
  * Minimalne ornamenty
  
- Wysoka improwizacja (+):
  * Nieoczekiwane modulacje
  * Synkopy i przesunięcia rytmiczne
  * Rozszerzone akordy
  * Bogate ornamenty
  * Chromatyka
"""


@dataclass
class SoulVector:
    """Wektor stanu duszy z timestampem."""
    values: np.ndarray
    timestamp: float = field(default_factory=time.time)


class SoulStateLogger:
    """Logger zapisujący historię stanów duszy do CSV z bezpieczną migracją."""
    FILE_PATH = "data/soul_history.csv"
    
    # Definicja kolejności kolumn (zaktualizowana: etyka → improwizacja)
    HEADER = ["timestamp", "id_event", "description", "mode", "cos_alpha", "compression", "emotion_msg"] + \
             [f"S_{axis}" for axis in AXES_LIST] + [f"F_{axis}" for axis in AXES_LIST]

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.event_counter = 0
        self._known_last_id = 0
        self._initialize_and_migrate_file()
        self.event_counter = self._known_last_id

    def _initialize_and_migrate_file(self):
        """Inicjalizuje plik lub wykonuje migrację struktury. Ostatni numer zdarzenia zostaje w pamięci."""
        if not os.path.exists(self.FILE_PATH) or os.path.getsize(self.FILE_PATH) == 0:
            with open(self.FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.HEADER)
            return

        try:
            df = pd.read_csv(self.FILE_PATH)
            current_columns = list(df.columns)
            needs_migration = False
            
            # Migracja: etyka → improwizacja
            if "S_etyka" in current_columns and "S_improwizacja" not in current_columns:
                print("[SYSTEM] Migracja: etyka → improwizacja...")
                df = df.rename(columns={
                    "S_etyka": "S_improwizacja",
                    "F_etyka": "F_improwizacja"
                })
                # Konwersja wartości: stara etyka (0-100) → nowa improwizacja (start od 0)
                # Zakładamy że wysoka etyka = konserwatywne podejście = niska improwizacja
                df["S_improwizacja"] = 50.0 - df["S_improwizacja"].fillna(0) * 0.5
                df["F_improwizacja"] = df["F_improwizacja"].fillna(0)
                needs_migration = True
            
            # Dodaj brakującą kolumnę compression
            if "compression" not in current_columns:
                df['compression'] = "NO"
                needs_migration = True
            
            if needs_migration:
                df = df.reindex(columns=self.HEADER)
                df.to_csv(self.FILE_PATH, index=False)
                print("[SYSTEM] Migracja zakończona sukcesem.")
            if not df.empty and "id_event" in df.columns:
                self._known_last_id = int(df.iloc[-1]["id_event"])
                
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            print("[ERROR] Plik historii uszkodzony. Tworzenie nowego.")
            with open(self.FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.HEADER)
        except Exception as e:
            print(f"[ERROR] Błąd weryfikacji historii: {e}")

    def log_state(self, core, F_vector, cos_alpha, emotion_msg, description, mode, compressed=False):
        """Zapisuje stan duszy do historii."""
        try:
            self.event_counter += 1
            comp_status = "YES" if compressed else "NO"
            
            row = [datetime.now().isoformat(), self.event_counter, description, mode, 
                   f"{cos_alpha:.4f}", comp_status, emotion_msg] + \
                  core.get_vector_copy().tolist() + F_vector.tolist()
            
            with open(self.FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(row)
            
            if compressed:
                core.log(f"[AUDYT] Stan #{self.event_counter} SKOMPRESOWANY (Redundancja).", "GRAY")
            else:
                core.log(f"[AUDYT] Stan #{self.event_counter} Zapisany (Nowa Jakość).", "CYAN")
                
        except PermissionError:
            core.log("[BŁĄD ZAPISU] Plik historii jest otwarty w innym programie!", "RED")


class EriAmoCore:
    """Rdzeń ontologiczny duszy muzycznej."""
    AXES = AXES_LIST
    HISTORY_PATH = "data/soul_history.csv"
    
    # Konfiguracja wygaszania osi efemerycznych
    DECAY_CONFIG = {
        'emocje': {'rate': 0.05, 'half_life': 10, 'floor': 0.0, 'ceiling': None},
        'czas': {'rate': 0.03, 'half_life': 20, 'floor': 0.0, 'ceiling': None}
    }
    
    def __init__(self):
        self.lock = threading.RLock()
        self.vector = SoulVector(np.zeros(len(self.AXES), dtype=float))
        self.last_decay_time = time.time()
        self.decay_cycle_count = 0
        
        # Szkielet etyczny (stały, niezmienny)
        self.ethics = ETHICS_FRAMEWORK.copy()
        
        if not self.load_soul_from_history():
            # Wartości początkowe dla nowej duszy
            self.vector.values[self.AXES.index('improwizacja')] = 0.0  # Balans
            self.vector.values[self.AXES.index('wiedza')] = 5.0
            self.vector.values[self.AXES.index('kreacja')] = 10.0
            self.log("EriAmo Core v5.9.1: Narodziny nowej Duszy.", "GREEN")
            self.log("  └─ Oś 'improwizacja' zastąpiła 'etyka'", "CYAN")
            self.log("  └─ Szkielet etyczny: AKTYWNY (stały)", "CYAN")
        else:
            self.log("EriAmo Core v5.9.1: Dusza wczytana (Reinkarnacja).", "PINK")
            current_hash = self.compute_integrity_hash()
            self.log(f"[SOULGUARD] Hash: {current_hash[:16]}...", "YELLOW")

    def log(self, msg: str, color: str = "WHITE"):
        colors = {
            "GREEN": "\033[92m", "RED": "\033[91m", "CYAN": "\033[96m", 
            "YELLOW": "\033[93m", "PINK": "\033[95m", "WHITE": "\033[0m", "GRAY": "\033[90m"
        }
        print(f"{colors.get(color, '')}{msg}\033[0m")

    def load_soul_from_history(self) -> bool:
        if not os.path.exists(self.HISTORY_PATH): return False
        try:
            df = pd.read_csv(self.HISTORY_PATH)
            if df.empty: return False
            last_row = df.iloc[-1]
            new_values = []
            for axis in self.AXES:
                col_name = f"S_{axis}"
                if col_name in last_row:
                    new_values.append(float(last_row[col_name]))
                else:
                    # Fallback dla migracji etyka → improwizacja
                    if axis == "improwizacja" and "S_etyka" in last_row:
                        old_etyka = float(last_row["S_etyka"])
                        new_values.append(50.0 - old_etyka * 0.5)
                    else:
                        new_values.append(0.0)
            self.vector.values = np.array(new_values)
            return True
        except Exception as e:
            self.log(f"[BŁĄD WCZYTYWANIA] {e}", "RED")
            return False

    def check_ontological_compression(self, F_vector: np.ndarray) -> tuple:
        with self.lock:
            S = self.vector.values
            norm_s = np.linalg.norm(S)
            norm_f = np.linalg.norm(F_vector)
            if norm_s == 0 or norm_f == 0: return False, 0.0
            cos_alpha = np.dot(S, F_vector) / (norm_s * norm_f)
            is_compressed = cos_alpha > ONTOLOGICAL_THRESHOLD
            return is_compressed, cos_alpha

    def shift_axis(self, axis: str, action: str, value: float) -> bool:
        """
        Przesuwa wartość osi.
        
        UWAGA: Oś 'improwizacja' nie ma limitów (może być ujemna lub dodatnia).
        Szkielet etyczny NIE jest osią i nie może być modyfikowany.
        """
        with self.lock:
            if axis not in self.AXES:
                # Sprawdź czy ktoś próbuje modyfikować etykę
                if axis in ["etyka", "integrity", "respect", "authenticity", "harmony"]:
                    self.log(f"[ETHICS] Próba modyfikacji szkieletu etycznego ZABLOKOWANA.", "RED")
                    return False
                return False
            
            i = self.AXES.index(axis)
            
            if action == "INCREMENT":
                self.vector.values[i] += value
            elif action == "SET":
                self.vector.values[i] = value
            elif action == "DECAY":
                self.vector.values[i] *= (1.0 - value)
            
            # Improwizacja nie ma twardych limitów, ale można soft-clampować
            # if axis == "improwizacja":
            #     self.vector.values[i] = np.clip(self.vector.values[i], -100, 100)
            
            return True

    def get_vector_copy(self) -> np.ndarray:
        with self.lock: return self.vector.values.copy()
    
    def get_improv_level(self) -> float:
        """Zwraca aktualny poziom improwizacji (-100 do +100)."""
        with self.lock:
            return float(self.vector.values[self.AXES.index('improwizacja')])
    
    def get_ethics_status(self) -> dict:
        """Zwraca status szkieletu etycznego (zawsze stały)."""
        return get_ethics_report()

    def apply_emotion_decay(self, cycles: int = 1):
        with self.lock:
            for axis in EPHEMERAL_AXES:
                if axis not in self.DECAY_CONFIG: continue
                config = self.DECAY_CONFIG[axis]
                idx = self.AXES.index(axis)
                old_val = self.vector.values[idx]
                decay_factor = (1 - config['rate']) ** cycles
                new_val = old_val * decay_factor
                if config['floor'] is not None:
                    if old_val > 0: new_val = max(new_val, config['floor'])
                    else: new_val = min(new_val, -config['floor'])
                if abs(new_val) < 0.01: new_val = 0.0
                self.vector.values[idx] = new_val
            self.decay_cycle_count += cycles
            self.last_decay_time = time.time()

    def apply_time_based_decay(self):
        current_time = time.time()
        elapsed_minutes = (current_time - self.last_decay_time) / 60.0
        if elapsed_minutes >= 1.0:
            cycles = int(elapsed_minutes)
            self.apply_emotion_decay(cycles)

    def get_emotional_state_description(self) -> str:
        with self.lock:
            emocje = float(self.vector.values[self.AXES.index('emocje')])
            affections = float(self.vector.values[self.AXES.index('affections')])
            improv = float(self.vector.values[self.AXES.index('improwizacja')])
        
        if abs(emocje) < 1.0: emotion_desc = "neutralne"
        elif emocje > 0: emotion_desc = "pobudzone (+)"
        else: emotion_desc = "wyciszone (-)"
        
        if abs(affections) < 10.0: affect_desc = "rozwijające się"
        elif affections > 100.0: affect_desc = "MONUMENTALNE (+)"
        elif affections < -100.0: affect_desc = "MONUMENTALNE (-)"
        elif affections > 0: affect_desc = "utrwalone (+)"
        else: affect_desc = "utrwalone (-)"
        
        if improv < -30: improv_desc = "ścisłe reguły"
        elif improv > 30: improv_desc = "swobodna"
        else: improv_desc = "zbalansowana"
        
        return f"Puls: {emotion_desc} ({emocje:.1f}) | Byt: {affect_desc} ({affections:.1f}) | Improw: {improv_desc} ({improv:.1f})"

    def compute_integrity_hash(self) -> str:
        with self.lock:
            data_str = "|".join([f"{x:.8f}" for x in self.vector.values]) + "".join(self.AXES)
            # Dodaj szkielet etyczny do hasha
            ethics_str = "|".join([f"{k}:{v['value']}" for k, v in self.ethics.items()])
            full_data = data_str + "|ETHICS|" + ethics_str
            return hashlib.sha256(full_data.encode('utf-8')).hexdigest()

    def get_decay_status(self) -> dict:
        with self.lock:
            return {
                'cycles_applied': self.decay_cycle_count,
                'last_decay': datetime.fromtimestamp(self.last_decay_time).isoformat(),
                'ephemeral_axes': EPHEMERAL_AXES,
                'persistent_axes': PERSISTENT_AXES,
                'current_emotions': float(self.vector.values[self.AXES.index('emocje')]),
                'current_affections': float(self.vector.values[self.AXES.index('affections')]),
                'current_improv': float(self.vector.values[self.AXES.index('improwizacja')])
            }

    def create_memory_dump(self, filename: str = None) -> str:
        os.makedirs("data/dumps", exist_ok=True)
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"soul_dump_{timestamp}.soul"
        filepath = f"data/dumps/{filename}"
        
        with self.lock:
            dump_data = {
                "meta": {
                    "version": "5.9.1",
                    "created_at": datetime.now().isoformat(),
                    "integrity_hash": self.compute_integrity_hash(),
                    "growth_mode": "UNBOUNDED",
                    "note": "Oś 'improwizacja' zastąpiła 'etyka'. Szkielet etyczny jest stały."
                },
                "soul_vector": {axis: float(self.vector.values[i]) for i, axis in enumerate(self.AXES)},
                "ethics_framework": {k: v["value"] for k, v in self.ethics.items()},
                "classification": {
                    "ephemeral": {axis: float(self.vector.values[self.AXES.index(axis)]) for axis in EPHEMERAL_AXES},
                    "persistent": {axis: float(self.vector.values[self.AXES.index(axis)]) for axis in PERSISTENT_AXES}
                },
                "decay_status": {"cycles_applied": self.decay_cycle_count, "last_decay_time": self.last_decay_time}
            }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
        self.log(f"[DUMP] Zrzut duszy: {filepath}", "GREEN")
        return filepath

    def load_memory_dump(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
            with self.lock:
                for axis, val in data['soul_vector'].items():
                    if axis in self.AXES:
                        self.vector.values[self.AXES.index(axis)] = float(val)
                    # Migracja ze starego formatu
                    elif axis == "etyka" and "improwizacja" not in data['soul_vector']:
                        improv_val = 50.0 - float(val) * 0.5
                        self.vector.values[self.AXES.index('improwizacja')] = improv_val
                        
                self.decay_cycle_count = data['decay_status'].get('cycles_applied', 0)
            
            if data['meta'].get('integrity_hash', '') == self.compute_integrity_hash():
                self.log(f"[DUMP] Zweryfikowano: {filepath}", "GREEN")
            else:
                self.log(f"[DUMP] Wczytano (Hash Mismatch - możliwa migracja): {filepath}", "YELLOW")
            return True
        except Exception as e:
            self.log(f"[DUMP ERROR] {e}", "RED")
            return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def interpret_improv_for_composition(improv_value: float) -> dict:
    """
    Interpretuje wartość osi improwizacji dla kompozytora.
    
    Returns:
        dict z parametrami wpływającymi na kompozycję
    """
    # Normalizuj do zakresu 0-1 dla łatwiejszego użycia
    normalized = (improv_value + 100) / 200  # -100→0, 0→0.5, +100→1
    normalized = max(0, min(1, normalized))
    
    return {
        "freedom_level": normalized,  # 0 = ścisłe reguły, 1 = pełna swoboda
        
        # Harmonika
        "allow_chromatic": normalized > 0.4,
        "allow_modal_interchange": normalized > 0.5,
        "allow_unexpected_modulation": normalized > 0.6,
        "extended_chords_probability": normalized * 0.8,
        
        # Rytmika
        "syncopation_probability": normalized * 0.6,
        "rubato_allowed": normalized > 0.3,
        "tempo_variation_range": normalized * 0.2,  # 0-20% wariacji tempa
        
        # Melodyka
        "ornamentation_density": normalized,
        "allow_large_leaps": normalized > 0.5,
        "chromatic_passing_tones": normalized > 0.4,
        
        # Forma
        "strict_phrase_length": normalized < 0.3,
        "allow_extensions": normalized > 0.4,
        "cadence_decoration": normalized * 0.7,
        
        # Opis słowny
        "description": (
            "bardzo konserwatywne" if normalized < 0.2 else
            "konserwatywne" if normalized < 0.4 else
            "zbalansowane" if normalized < 0.6 else
            "swobodne" if normalized < 0.8 else
            "bardzo swobodne / improwizowane"
        )
    }


# =============================================================================
# META-OŚ EMERGENTNA: CIEKAWOŚĆ
# =============================================================================
"""
CIEKAWOŚĆ - nie jest przechowywana, lecz obliczana dynamicznie.

Formuła:
    ciekawość = f(kreacja, wiedza, emocje) + modyfikatory

Składniki:
    - KREACJA (waga 0.4): Wysoka kreacja = chęć tworzenia nowego
    - WIEDZA (waga 0.3): Średnia wiedza = optymalna ciekawość
                         (za mało = brak podstaw, za dużo = "wiem wszystko")
    - EMOCJE (waga 0.3): Pobudzenie emocjonalne napędza eksplorację

Krzywa wiedzy (odwrócona U):
    wiedza=0   → ciekawość niska (brak podstaw do eksploracji)
    wiedza=50  → ciekawość maksymalna (wystarczająco dużo by pytać)
    wiedza=100 → ciekawość spada ("ekspert" mniej pyta)

Mechanika znudzenia:
    - Powtarzanie tego samego → ciekawość rośnie
    - Odkrycie czegoś nowego → chwilowe zaspokojenie
    
Zakres wyjściowy: -100 do +100
    -100 : Stagnacja, zero zainteresowania nowością
       0 : Balans eksploracja/eksploatacja  
    +100 : Maksymalna ciekawość, głód nowości
"""


class CuriosityEngine:
    """Silnik obliczający emergentną ciekawość."""
    
    # Wagi składników
    WEIGHT_KREACJA = 0.40
    WEIGHT_WIEDZA = 0.30
    WEIGHT_EMOCJE = 0.30
    
    # Parametry krzywej wiedzy (odwrócona U)
    WIEDZA_OPTIMUM = 50.0  # Punkt maksymalnej ciekawości
    WIEDZA_SPREAD = 40.0   # Szerokość krzywej
    
    def __init__(self):
        self.boredom_counter = {}  # Licznik powtórzeń gatunków
        self.discovery_cooldown = 0  # Czas od ostatniego odkrycia
        self.last_genres = []  # Historia ostatnich gatunków
        
    def compute_curiosity(self, kreacja: float, wiedza: float, emocje: float) -> dict:
        """
        Oblicza emergentną ciekawość.
        
        Args:
            kreacja: Wartość osi kreacji
            wiedza: Wartość osi wiedzy
            emocje: Wartość osi emocji
            
        Returns:
            dict z wartością ciekawości i składnikami
        """
        # === Składnik KREACJA ===
        # Liniowy: wysoka kreacja = wysoka ciekawość
        kreacja_component = self._normalize(kreacja) * 100
        
        # === Składnik WIEDZA (krzywa odwróconej U) ===
        # Gaussowska krzywa: maksimum przy WIEDZA_OPTIMUM
        wiedza_norm = self._normalize(wiedza) * 100
        wiedza_diff = abs(wiedza_norm - self.WIEDZA_OPTIMUM)
        import math
        wiedza_component = 100 * math.exp(-(wiedza_diff ** 2) / (2 * self.WIEDZA_SPREAD ** 2))
        
        # === Składnik EMOCJE ===
        # Absolutna wartość: zarówno pozytywne jak i negatywne emocje napędzają ciekawość
        emocje_component = min(100, abs(emocje) * 2)
        
        # === Kombinacja ważona ===
        base_curiosity = (
            self.WEIGHT_KREACJA * kreacja_component +
            self.WEIGHT_WIEDZA * wiedza_component +
            self.WEIGHT_EMOCJE * emocje_component
        )
        
        # === Modyfikatory ===
        boredom_bonus = self._compute_boredom_bonus()
        discovery_penalty = self._compute_discovery_penalty()
        
        final_curiosity = base_curiosity + boredom_bonus - discovery_penalty
        
        # Normalizuj do zakresu -100 do +100
        # (base jest 0-100, modyfikatory mogą przesunąć)
        final_curiosity = (final_curiosity - 50) * 2  # Przeskaluj do -100..+100
        final_curiosity = max(-100, min(100, final_curiosity))
        
        return {
            'value': final_curiosity,
            'components': {
                'kreacja': kreacja_component,
                'wiedza': wiedza_component,
                'emocje': emocje_component,
                'boredom_bonus': boredom_bonus,
                'discovery_penalty': discovery_penalty
            },
            'description': self._describe_curiosity(final_curiosity),
            'recommendation': self._get_recommendation(final_curiosity)
        }
    
    def _normalize(self, value: float, min_val: float = -100, max_val: float = 100) -> float:
        """Normalizuje wartość do zakresu 0-1."""
        return max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    def _compute_boredom_bonus(self) -> float:
        """Oblicza bonus za znudzenie (powtarzanie gatunków)."""
        if not self.last_genres:
            return 0.0
        
        # Sprawdź ile razy z rzędu ten sam gatunek
        if len(self.last_genres) >= 2:
            last = self.last_genres[-1]
            streak = sum(1 for g in reversed(self.last_genres) if g == last)
            # Bonus rośnie z liczbą powtórzeń: 0, 5, 12, 21, 32...
            return min(40, streak * (streak + 1))
        return 0.0
    
    def _compute_discovery_penalty(self) -> float:
        """Oblicza penalty za niedawne odkrycie (zaspokojenie)."""
        # Penalty maleje z czasem
        return max(0, 20 - self.discovery_cooldown * 5)
    
    def register_composition(self, genre: str, was_novel: bool = False):
        """
        Rejestruje ukończoną kompozycję.
        
        Args:
            genre: Nazwa gatunku
            was_novel: Czy zawierała nowatorskie elementy
        """
        self.last_genres.append(genre)
        if len(self.last_genres) > 10:
            self.last_genres.pop(0)
        
        # Aktualizuj licznik znudzenia
        self.boredom_counter[genre] = self.boredom_counter.get(genre, 0) + 1
        
        # Odkrycie resetuje cooldown
        if was_novel:
            self.discovery_cooldown = 0
        else:
            self.discovery_cooldown += 1
    
    def register_discovery(self):
        """Rejestruje odkrycie czegoś nowego."""
        self.discovery_cooldown = 0
    
    def suggest_new_genre(self, current_genre: str, available_genres: list) -> str:
        """
        Sugeruje nowy gatunek na podstawie ciekawości.
        
        Preferuje gatunki mniej eksplorowane.
        """
        if not available_genres:
            return current_genre
        
        # Sortuj po liczbie kompozycji (rosnąco)
        genre_counts = [(g, self.boredom_counter.get(g, 0)) for g in available_genres]
        genre_counts.sort(key=lambda x: x[1])
        
        # Zwróć najmniej eksplorowany (ale nie obecny jeśli to możliwe)
        for genre, count in genre_counts:
            if genre != current_genre:
                return genre
        
        return genre_counts[0][0]
    
    def _describe_curiosity(self, value: float) -> str:
        """Opisuje poziom ciekawości słownie."""
        if value < -60:
            return "stagnacja - brak zainteresowania nowością"
        elif value < -20:
            return "komfort - preferuje sprawdzone metody"
        elif value < 20:
            return "balans - otwartość na nowe przy zachowaniu tradycji"
        elif value < 60:
            return "eksploracja - aktywnie szuka nowych rozwiązań"
        else:
            return "głód nowości - musi spróbować czegoś zupełnie nowego!"
    
    def _get_recommendation(self, curiosity: float) -> dict:
        """Zwraca rekomendacje dla kompozytora na podstawie ciekawości."""
        if curiosity < -30:
            return {
                'action': 'STAY',
                'message': 'Kontynuuj w obecnym stylu',
                'risk_tolerance': 0.1,
                'novelty_seeking': False
            }
        elif curiosity < 30:
            return {
                'action': 'VARY',
                'message': 'Wprowadź subtelne wariacje',
                'risk_tolerance': 0.3,
                'novelty_seeking': False
            }
        elif curiosity < 70:
            return {
                'action': 'EXPLORE',
                'message': 'Eksperymentuj z nowymi elementami',
                'risk_tolerance': 0.6,
                'novelty_seeking': True
            }
        else:
            return {
                'action': 'REVOLUTIONIZE',
                'message': 'Czas na coś zupełnie nowego!',
                'risk_tolerance': 0.9,
                'novelty_seeking': True,
                'suggest_genre_change': True
            }


# Globalna instancja silnika ciekawości
_curiosity_engine = None


def get_curiosity_engine() -> CuriosityEngine:
    """Zwraca globalną instancję silnika ciekawości."""
    global _curiosity_engine
    if _curiosity_engine is None:
        _curiosity_engine = CuriosityEngine()
    return _curiosity_engine


def compute_curiosity_from_soul(core) -> dict:
    """
    Pomocnicza funkcja obliczająca ciekawość z obiektu EriAmoCore.
    
    Args:
        core: Instancja EriAmoCore
        
    Returns:
        dict z wartością ciekawości i metadanymi
    """
    engine = get_curiosity_engine()
    vector = core.get_vector_copy()
    
    kreacja = vector[core.AXES.index('kreacja')]
    wiedza = vector[core.AXES.index('wiedza')]
    emocje = vector[core.AXES.index('emocje')]
    
    return engine.compute_curiosity(kreacja, wiedza, emocje)
