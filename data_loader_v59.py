# data_loader_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
Loader Danych Zewnętrznych EriAmo v5.9 [INSTRUMENT AWARE]
- Integracja z MusicBrainz API (zabezpieczona)
- Analiza plików nutowych (Music21)
- Wykrywanie INSTRUMENTÓW (Mapowanie brzmień MIDI na cechy Duszy)
- Automatyczne pobieranie metadanych z MIDI i naprawa kodowania
"""
import os
import re

try:
    import music21
    MUSIC21_AVAIL = True
except ImportError:
    MUSIC21_AVAIL = False

try:
    import musicbrainzngs
    MUSICBRAINZ_AVAIL = True
except ImportError:
    MUSICBRAINZ_AVAIL = False


class ExternalKnowledgeLoader:
    """Loader wiedzy zewnętrznej z różnych źródeł."""
    
    # Mapowanie numerów MIDI (0-127) na Cechy Ontologiczne EriAmo
    INSTRUMENT_FEATURES = {
        # Piana (0-7)
        0: ["KLASYCYZM"], 1: ["JAZZ"], 6: ["BAROQUE"],
        # Organy (16-23)
        19: ["SACRED", "WZNIOSLY", "ETYKA"], # Church Organ
        21: ["FOLK", "RADOSC"], # Accordion
        # Gitary (24-31)
        24: ["INTYMNA", "ACOUSTIC"], # Nylon
        25: ["FOLK", "BYT"], # Steel
        29: ["ROCK", "BYT"], # Overdriven
        30: ["HEAVY_METAL", "POWER_METAL", "RAW", "BYT"], # Distortion
        # Basy (32-39)
        32: ["BASS", "JAZZ"], # Acoustic Bass
        33: ["BASS", "ROCK"], # Finger Bass
        38: ["SYNTH", "ELEKTRONIKA"], # Synth Bass
        # Smyczki (40-47) & Zespoły (48-55)
        40: ["ROMANTYZM", "LAMENTOSO"], # Violin
        42: ["LAMENTOSO", "INTYMNA"], # Cello
        48: ["ORKIESTROWY", "WZNIOSLY"], # String Ensemble
        52: ["SACRED", "WZNIOSLY", "CHWALA"], # Choir Aahs
        # Dęte (56-79)
        56: ["JAZZ", "HEROIC"], # Trumpet
        61: ["HEROIC", "POWER_METAL"], # Brass Section
        65: ["JAZZ", "INTYMNA"], # Sax
        73: ["DOLCE", "INTYMNA"], # Flute
        # Syntezatory (80-103)
        80: ["ELEKTRONIKA", "FUTURYSTYCZNY"], # Square Lead
        89: ["AMBIENT", "PRZESTRZEN"], # Warm Pad
        91: ["SACRED", "PRZESTRZEN"], # Choir Pad
        96: ["AMBIENT", "KOSMICZNY"], # Rain
        # Etniczne (104-111)
        104: ["EKSPERYMENTALNY", "WESOLY"], # Sitar
    }
    
    def __init__(self):
        if MUSICBRAINZ_AVAIL:
            try:
                musicbrainzngs.set_useragent("EriAmoAI", "5.9", "contact@eriamo.project")
                print("[LOADER] Połączono z MusicBrainz API.")
            except Exception as e:
                print(f"[LOADER] Tryb offline (MusicBrainz error): {e}")

    def _analyze_text_heuristics(self, text: str) -> list:
        """Analiza heurystyczna tekstu (tytuł, artysta)."""
        if not text: return []
        text = text.lower()
        features = set()
        
        # === STYL / EPOKA ===
        style_map = {
            ('bach', 'handel', 'vivaldi', 'petzold', 'telemann'): "BAROQUE",
            ('mozart', 'haydn', 'beethoven', 'clementi'): "KLASYCYZM",
            ('chopin', 'liszt', 'schubert', 'schumann', 'brahms', 'wagner'): "ROMANTYZM",
            ('metallica', 'iron maiden', 'slayer', 'megadeth', 'sabbath', 'accept'): "HEAVY_METAL",
            ('blind guardian', 'helloween', 'rhapsody', 'sabaton'): "POWER_METAL",
            ('maleo', 'marley', 'reggae'): "REGGAE",
            ('pink floyd', 'yes', 'genesis', 'king crimson'): "PROG_ROCK",
            ('cocteau', 'eno', 'aphex'): "AMBIENT",
            ('miles davis', 'coltrane', 'monk', 'parker'): "JAZZ",
        }
        for k, v in style_map.items():
            if any(w in text for w in k): features.add(v)
        
        # === FORMA ===
        form_map = {
            ('minuet', 'menuet'): "MENUET", ('fuga', 'fugue'): "FUGA",
            ('kanon', 'canon'): "KANON", ('requiem', 'missa'): "LAMENTOSO",
            ('march', 'marsz'): "MARSZ", ('nocturne', 'nokturn'): "INTYMNA",
            ('sonata', 'etiuda'): "ZLOZONY", ('chaos',): "CHAOS", ('dramatic',): "DRAMATYCZNY"
        }
        for k, v in form_map.items():
            if any(w in text for w in k): features.add(v)
            
        if 'major' in text or 'dur' in text: features.add("RADOSC")
        if 'minor' in text or 'moll' in text: features.add("MELANCHOLIA")
        
        return list(features)

    def _map_genre_to_features(self, genre_list: list) -> list:
        """Mapuje gatunki z MusicBrainz na cechy."""
        if not genre_list: return []
        features = set()
        mapping = {
            "metal": ["HEAVY_METAL", "CON_FUOCO"],
            "power metal": ["POWER_METAL", "WZNIOSLY", "PRESTO"],
            "rock": ["ROCK", "ALLEGRO"], "punk": ["PUNK", "PRESTO", "GNIEW"],
            "jazz": ["JAZZ", "ZLOZONY", "IMPROWIZACJA"], "pop": ["POP", "ALLEGRO"],
            "reggae": ["REGGAE", "SPOKOJ"], "ballad": ["LAMENTOSO", "INTYMNA"],
            "blues": ["MELANCHOLIA", "ADAGIO"], "ambient": ["AMBIENT", "PRZESTRZEN"],
            "electronic": ["EKSPERYMENTALNY", "KREACJA"], "classical": ["KLASYCYZM", "ZLOZONY"],
            "baroque": ["BAROQUE", "LOGIKA"], "romantic": ["ROMANTYZM", "EMOCJE"],
            "choral": ["WZNIOSLY", "SACRED"], "death metal": ["HEAVY_METAL", "TRAGEDIA"]
        }
        for genre in genre_list:
            g = str(genre).lower()
            for k, v in mapping.items():
                if k in g: features.update(v)
        return list(features)

    def get_context_from_web(self, artist_name: str, track_title: str) -> list:
        """Pobiera kontekst z MusicBrainz API."""
        combined = f"{artist_name} {track_title}"
        features = set(self._analyze_text_heuristics(combined))
        if not track_title and not artist_name: return list(features)

        print(f"[WEB] Szukam w MusicBrainz: '{artist_name}' - '{track_title}'...")
        if MUSICBRAINZ_AVAIL:
            try:
                query = []
                if track_title: query.append(f'"{track_title}"')
                if artist_name: query.append(f'artist:"{artist_name}"')
                result = musicbrainzngs.search_recordings(query=" AND ".join(query), limit=1)
                
                if result.get('recording-list'):
                    rec = result['recording-list'][0]
                    print(f"[WEB] Znaleziono: {rec.get('title', 'Unknown')}")
                    mb_tags = [t.get('name','') for t in rec.get('tag-list',[])]
                    
                    # Pobierz tagi artysty jeśli brak tagów utworu
                    if not mb_tags and rec.get('artist-credit'):
                        aid = rec['artist-credit'][0].get('artist', {}).get('id')
                        if aid:
                            ainfo = musicbrainzngs.get_artist_by_id(aid, includes=["tags"])
                            mb_tags = [t.get('name','') for t in ainfo['artist'].get('tag-list',[])]
                            
                    if mb_tags: features.update(self._map_genre_to_features(mb_tags))
                else:
                    print("[WEB] Brak wyników.")
            except Exception as e:
                print(f"[WEB] Błąd API: {e}")
        return list(features)

    def _decode_midi_text(self, raw_bytes: bytes) -> str:
        if not isinstance(raw_bytes, bytes): return str(raw_bytes)
        for enc in ['utf-8', 'cp1250', 'latin-1']:
            try: return raw_bytes.decode(enc).strip()
            except UnicodeDecodeError: continue
        return raw_bytes.decode('utf-8', errors='ignore').strip()

    def _analyze_instruments(self, score) -> list:
        """Skanuje plik w poszukiwaniu instrumentów i mapuje je na cechy."""
        features = set()
        try:
            # Music21 przechowuje instrumenty w obiektach part lub na początku streamu
            instruments = score.flatten().getElementsByClass('Instrument')
            found_progs = set()
            
            for inst in instruments:
                if inst.midiProgram is not None:
                    found_progs.add(inst.midiProgram)
            
            if found_progs:
                print(f"[NUTY] Znalezione instrumenty (MIDI Prog): {list(found_progs)}")
                
                for prog in found_progs:
                    # Szukaj dokładnego dopasowania
                    if prog in self.INSTRUMENT_FEATURES:
                        features.update(self.INSTRUMENT_FEATURES[prog])
                    else:
                        # Heurystyka grupowa (np. wszystkie gitary 24-31)
                        if 24 <= prog <= 31: features.add("ROCK")
                        elif 40 <= prog <= 47: features.add("KLASYCYZM")
                        elif 80 <= prog <= 103: features.add("ELEKTRONIKA")
                        
        except Exception as e:
            print(f"[NUTY] Błąd analizy instrumentów: {e}")
            
        return list(features)

    def open_score(self, file_path: str):
        """Jedno wczytanie pliku. Zwraca partyturę albo None."""
        if not MUSIC21_AVAIL:
            print("[NUTY] Music21 niedostępne")
            return None
        print(f"[NUTY] Analizuję: {os.path.basename(file_path)}...")
        try:
            return music21.converter.parse(file_path)
        except Exception as e:
            print(f"[NUTY] Krytyczny błąd: {e}")
            return None

    def parse_music_file(self, file_path: str) -> list:
        """Główna metoda analizy pliku."""
        score = self.open_score(file_path)
        if score is None:
            return []
        return self.features_from_score(score)

    def features_from_score(self, score) -> list:
        """Cechy ontologiczne z gotowej partytury."""
        if score is None:
            return []

        features = []
        try:
            # 1. INSTRUMENTY (NOWOŚĆ!)
            inst_features = self._analyze_instruments(score)
            features.extend(inst_features)
            
            # 2. METADANE
            extracted_text = []
            try:
                for evt in score.flatten().getElementsByClass(music21.midi.MidiEvent):
                    if evt.isText and isinstance(evt.data, bytes):
                        decoded = self._decode_midi_text(evt.data)
                        if len(decoded) > 2: extracted_text.append(decoded)
            except Exception:
                pass
            
            # TextBoxes
            for tb in score.flatten().getElementsByClass('TextBox'):
                if tb.content: extracted_text.append(str(tb.content))
                
            title_guess, artist_guess = "", ""
            if extracted_text:
                full_text = " ".join(list(dict.fromkeys(extracted_text)))
                print(f"[AUTO-INFO] Tekst: {full_text[:50]}...")
                if " - " in full_text:
                    parts = full_text.split(" - ", 1)
                    title_guess, artist_guess = parts[0].strip(), parts[1].strip()
                else:
                    title_guess = full_text.strip()
                
                if title_guess or artist_guess:
                    features.extend(self.get_context_from_web(artist_guess, title_guess))
            
            # 3. STRUKTURA (Tempo/Tonacja)
            try:
                tempos = score.metronomeMarkBoundaries()
                if tempos:
                    bpm = tempos[0][2].number
                    if bpm >= 140: features.append("PRESTO")
                    elif bpm >= 100: features.append("ALLEGRO")
                    elif bpm <= 60: features.append("ADAGIO")
                
                key = score.analyze('key')
                if key:
                    if key.mode == 'minor': features.append("MELANCHOLIA")
                    elif key.mode == 'major': features.append("RADOSC")
                    
                # Prosta detekcja chaosu/złożoności
                notes_count = len(score.flatten().notes)
                if notes_count > 1000: features.append("EPIC") # Długi/gęsty utwór
                
            except Exception:
                pass
            
            final = list(set(features))
            print(f"[NUTY] Wynik końcowy: {final}")
            return final
            
        except Exception as e:
            print(f"[NUTY] Krytyczny błąd: {e}")
            return []
