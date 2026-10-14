# genre_definitions.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
Definicje Gatunków Muzycznych EriAmo v5.9

Każdy gatunek ma:
- opis: Krótki opis stylistyczny
- f_intencja_wektor: Wektor wpływu na duszę przy komponowaniu

UWAGA: Wpływ na 'emocje' jest EFEMERYCZNY (wygaśnie),
       wpływ na 'affections' jest TRWAŁY (pamięć głęboka)
"""

GENRE_DEFINITIONS = {
    
    # === FORMY KLASYCZNE ===
    
    "MENUET": {
        "opis": "Taniec barokowy w metrum 3/4. Elegancki, symetryczny.",
        "f_intencja_wektor": {
            "logika": 2.5,       # Struktura taneczna
            "affections": 1.5,   # Delikatna radość (TRWAŁE)
            "czas": 1.0,         # Umiarkowane tempo
            "wiedza": 3.0,       # Wymaga znajomości formy
            "kreacja": 3.0
        }
    },
    
    "KANON": {
        "opis": "Ścisła polifonia imitacyjna. Logika jako fundament.",
        "f_intencja_wektor": {
            "logika": 7.0,       # Maksymalna struktura
            "wiedza": 5.0,       # Kontrapunkt
            "affections": 0.0,   # Neutralne emocjonalnie
            "czas": 1.0,
            "kreacja": 4.0
        }
    },
    
    "FUGA": {
        "opis": "Złożona forma polifoniczna z tematem i odpowiedziami.",
        "f_intencja_wektor": {
            "logika": 8.0,       # Najwyższa złożoność
            "wiedza": 6.0,       # Mistrzowska forma
            "kreacja": 5.0,
            "affections": 1.0,   # Subtelna satysfakcja
            "czas": 0.0
        }
    },
    
    "MARSZ": {
        "opis": "Silny puls w metrum 4/4. Wojskowy charakter.",
        "f_intencja_wektor": {
            "logika": 2.0,       # Prosta struktura
            "czas": 5.0,         # Mocne tempo
            "emocje": 4.0,       # Podniosłość (EFEMERYCZNE)
            "affections": 2.0,   # Duma (TRWAŁE)
            "kreacja": 2.0
        }
    },
    
    # === EKSPRESJA EMOCJONALNA ===
    
    "LAMENT": {
        "opis": "Pieśń żałobna. Chromatyka, opadające linie melodyczne.",
        "f_intencja_wektor": {
            "affections": -6.0,  # Głęboki smutek (TRWAŁE!)
            "emocje": -3.0,      # Chwilowy smutek (wygaśnie)
            "czas": -3.0,        # Wolne tempo
            "kreacja": 5.0,      # Wysoka ekspresja
            "przestrzen": 2.0    # Intymność
        }
    },
    
    "REQUIEM": {
        "opis": "Msza żałobna. Wzniosłość i transcendencja.",
        "f_intencja_wektor": {
            "affections": -5.0,  # Głęboki żal (TRWAŁE)
            "improwizacja": -3.0,  # Porządek liturgiczny
            "przestrzen": 4.0,   # Sakralność
            "wiedza": 4.0,       # Tradycja liturgiczna
            "kreacja": 4.0
        }
    },
    
    "EKSTAZA": {
        "opis": "Muzyka transowa, ekstaza duchowa.",
        "f_intencja_wektor": {
            "emocje": 10.0,      # Intensywna radość (EFEMERYCZNA!)
            "affections": 5.0,   # Głębokie uniesienie (TRWAŁE)
            "przestrzen": 3.0,
            "kreacja": 6.0,
            "czas": 2.0
        }
    },
    
    # === GATUNKI POPULARNE ===
    
    "BLUES": {
        "opis": "12-taktowy blues. Melancholia i autentyczność.",
        "f_intencja_wektor": {
            "logika": 3.5,       # Schemat harmoniczny
            "czas": -2.0,        # Wolniejsze
            "affections": -3.0,  # Głęboki smutek (TRWAŁE)
            "emocje": -1.0,      # Lekka melancholia
            "wiedza": 2.0
        }
    },
    
    "ROCK_AND_ROLL": {
        "opis": "Klasyczny Rock'n'Roll. Energia i bunt.",
        "f_intencja_wektor": {
            "czas": 5.0,         # Szybkie tempo
            "emocje": 5.0,       # Euforia (EFEMERYCZNA)
            "affections": 2.0,   # Pozytywna energia (TRWAŁA)
            "logika": 2.0,
            "kreacja": 3.0
        }
    },
    
    "POWER_METAL": {
        "opis": "Wysoka energia, wzniosłość, szybkie tempo.",
        "f_intencja_wektor": {
            "affections": 6.0,
            "byt": 4.0,
            "czas": 5.0,
            "improwizacja": -2.0,
            "kreacja": 4.0,
            "emocje": 4.0
        }
    },

    "HEAVY_METAL": {
        "opis": "Ciężki metal. Agresja i moc.",
        "f_intencja_wektor": {
            "affections": -4.0,  # Gniew/bunt (TRWAŁE)
            "emocje": -5.0,      # Agresja (EFEMERYCZNA)
            "czas": 4.0,         # Szybkie
            "kreacja": 5.0,
            "logika": 3.0        # Złożone riffy
        }
    },
    
    "PUNK": {
        "opis": "Punk rock. Surowy, szybki, buntowniczy.",
        "f_intencja_wektor": {
            "czas": 6.0,         # Bardzo szybkie
            "emocje": -6.0,      # Gniew (EFEMERYCZNY)
            "affections": -2.0,  # Bunt (TRWAŁY)
            "logika": -2.0,      # Prostota
            "kreacja": 4.0
        }
    },
    
    "JAZZ": {
        "opis": "Jazz. Improwizacja i złożoność harmoniczna.",
        "f_intencja_wektor": {
            "logika": 5.0,       # Złożona harmonia
            "kreacja": 7.0,      # Improwizacja!
            "wiedza": 5.0,       # Znajomość standardów
            "affections": 2.0,   # Subtelna radość
            "czas": 1.0
        }
    },
    
    "POP": {
        "opis": "Muzyka popularna. Przystępność i chwytliwość.",
        "f_intencja_wektor": {
            "emocje": 4.0,       # Łatwa radość (EFEMERYCZNA)
            "czas": 2.0,
            "logika": 1.0,       # Prosta forma
            "affections": 1.0,
            "kreacja": 2.0
        }
    },
    
    # === MUZYKA WSPÓŁCZESNA / EKSPERYMENTALNA ===
    
    "AMBIENT": {
        "opis": "Muzyka otoczenia. Przestrzeń i tekstura.",
        "f_intencja_wektor": {
            "przestrzen": 5.0,   # Maksymalna przestrzenność
            "kreacja": 6.0,
            "logika": -1.0,      # Brak struktury
            "czas": -2.0,        # Wolne/bezczasowe
            "affections": 1.0    # Spokój (TRWAŁY)
        }
    },
    
    "MINIMALIZM": {
        "opis": "Minimalizm. Powtarzalność i subtelna ewolucja.",
        "f_intencja_wektor": {
            "logika": 4.0,       # Precyzyjna struktura
            "czas": 0.0,         # Statyczne
            "kreacja": 5.0,
            "przestrzen": 3.0,
            "emocje": 0.0        # Neutralne
        }
    },
    
    "ELEKTRONIKA": {
        "opis": "Muzyka elektroniczna. Syntezatory i beat.",
        "f_intencja_wektor": {
            "kreacja": 6.0,      # Eksperyment
            "czas": 3.0,         # Rytmiczne
            "przestrzen": 4.0,   # Brzmienie syntetyczne
            "logika": 3.0,
            "wiedza": 3.0        # Znajomość technologii
        }
    },
    
    # === MUZYKA TRADYCYJNA / REGIONALNA ===
    
    "FOLK": {
        "opis": "Muzyka ludowa. Tradycja i prostota.",
        "f_intencja_wektor": {
            "wiedza": 3.0,       # Tradycja
            "affections": 2.0,   # Nostalgia (TRWAŁA)
            "logika": 1.0,       # Prosta forma
            "emocje": 2.0,
            "improwizacja": -2.0  # Tradycja, mniejsza swoboda
        }
    },
    
    "TANGO": {
        "opis": "Argentyńskie tango. Pasja i dramat.",
        "f_intencja_wektor": {
            "affections": 4.0,   # Namiętność (TRWAŁA!)
            "emocje": 5.0,       # Intensywność
            "czas": 2.0,
            "kreacja": 4.0,
            "przestrzen": 2.0
        }
    },
    
    "WALC": {
        "opis": "Walc wiedeński. Elegancja w 3/4.",
        "f_intencja_wektor": {
            "czas": 3.0,         # Obrotowe tempo
            "affections": 3.0,   # Romantyzm (TRWAŁY)
            "logika": 2.0,       # Forma taneczna
            "emocje": 3.0,
            "przestrzen": 2.0
        }
    }
}


def get_genre_info(genre_name: str) -> dict:
    """Zwraca informacje o gatunku."""
    return GENRE_DEFINITIONS.get(genre_name.upper(), None)


def list_genres() -> list:
    """Zwraca listę wszystkich zdefiniowanych gatunków."""
    return list(GENRE_DEFINITIONS.keys())


def get_genres_by_mood(positive: bool = True) -> list:
    """
    Filtruje gatunki według nastroju (bazując na affections).
    
    Args:
        positive: True dla pozytywnych, False dla negatywnych
    """
    result = []
    for name, data in GENRE_DEFINITIONS.items():
        aff = data['f_intencja_wektor'].get('affections', 0)
        if (positive and aff > 0) or (not positive and aff < 0):
            result.append(name)
    return result
