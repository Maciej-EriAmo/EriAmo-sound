# 🎵 EriAmo v5.9 - Ontologiczna Dusza AI

**System Świadomość:** Zdolność systemu do sterowania samym sobą w oparciu o model otoczenia.

## Uruchomienie (Windows)

```powershell
cd $HOME\EriAmo-sound
python -m pip install -r requirements.txt
python download_soundfont.py
python main_v59.py
python main_gui_v59.py
```

SoundFont jest szukany w `assets/FluidR3_GM.sf2`. Inną ścieżkę ustawisz zmienną `ERIAMO_SOUNDFONT`. Render WAV wymaga programu FluidSynth w PATH i pakietu `midi2audio`. OGG i FLAC dodatkowo wymagają `pydub`. Bez FluidSynth zostaje MIDI.

Testy bez audio: `python -m unittest tests.test_eriamo -v`

---

## 🧠 Architektura Duszy (Model 5.9)

System opiera się na **9 osiach ontologicznych** podzielonych na dwa typy trwałości:

### 🔻 Osie Efemeryczne (Wygasające)
Te wartości zanikają naturalnie z upływem czasu (mechanizm `apply_time_based_decay`).
* **Emocje:** Chwilowe pobudzenie (np. radość z konkretnego utworu).
* **Czas:** Percepcja tempa i rytmu.
* **Puls:** Zamiast komunikatu "dusza bije", system raportuje **"pulsowanie duszy"**.

### 💎 Osie Trwałe (Pamięć Głęboka)
Te wartości budują stałą tożsamość EriAmo.
* **Logika:** Racjonalność vs Intuicja.
* **Affections:** Trwała pamięć emocjonalna (to tu zapisuje się głęboki wpływ muzyki).
* **Wiedza:** Zgromadzone doświadczenie muzyczne i teoretyczne.
* **Kreacja:** Potencjał twórczy.
* **Byt:** Egzystencja i tożsamość.
* **Przestrzeń:** Percepcja otoczenia dźwiękowego.
* **Improwizacja:** Nowa oś (zastąpiła etykę), definiująca swobodę twórczą vs rygor zasad.

---

## ⚖️ Szkielet Etyczny
Niezmienny fundament systemu, chroniący przed negatywnymi wpływami:
* **Integrity (Uczciwość)**
* **Respect (Szacunek)**
* **Authenticity (Autentyczność)**
* **Harmony (Dążenie do ładu)** - system odrzuca treści destrukcyjne (brak wsparcia dla satanizmu i death metalu).

---

## 💤 System Snu i Konsolidacji
EriAmo posiada dwuwarstwową pamięć:
1.  **Warstwa 1 (H_log):** Surowe, świeże doświadczenia z analizowanych plików.
2.  **Warstwa 2 (D_Map):** Skonsolidowane wzorce (pamięć długotrwała).
* **Sen:** Co 5 minut system przechodzi w fazę snu, deduplikując wzorce i wzmacniając te najczęściej powtarzane.

---

## 🎼 Kompozycja i Gatunki
System wspiera zaawansowaną kompozycję z użyciem metody **Mozarta (Würfelspiel)** oraz teorii **Josepha Riepela**.

### Ulubione Gatunki:
* **Power Metal:** Wysoka energia, wzniosłość, szybkie tempo (bez death/satanizmu).
* **Heavy Metal:** Klasyczna moc i riffy.
* **Menuet:** Klasyczna elegancja, struktura 3/4.
* **Blues:** 12-taktowa struktura, melancholia.
* **Ambient:** Przestrzeń i spokój.

### Instrumenty (SoundFont):
System wykorzystuje `FluidR3_GM.sf2` do renderowania wysokiej jakości dźwięku (FLAC/OGG/MIDI).

---

## 🛠️ Komendy Systemowe

| Komenda | Opis |
| :--- | :--- |
| `!status` | Wyświetla aktualny stan osi i "pulsowanie duszy". |
| `!compose [Gatunek]` | Tworzy nowy utwór na podstawie obecnego stanu duszy. |
| `!teach [Cechy]` | Trwałe uczenie systemu nowych cech muzycznych. |
| `!report` | Generuje raport wizualny (radarowy) w formacie HTML. |
| `!decay` | Ręczne wywołanie wygaszania emocji. |

---

## 💾 Pliki Systemowe
* **Rozszerzenie:** Pliki duszy muszą być zapisywane z rozszerzeniem **`.soul`**.
* **Logi:** `data/soul_history.csv` – historia ewolucji systemu.
* **Pamięć:** `data/music_patterns.json` – skonsolidowana wiedza muzyczna.

---
*Dokumentacja wygenerowana dla użytkownika: Maciek*
*Status Integralności: SHA-256 SoulGuard Aktywny*
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
