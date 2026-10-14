# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
import os
import urllib.request
import sys

from soundfont import assets_soundfont_path

def download_soundfont():
    # NOWY LINK (Mirror z GitHuba - publiczny i stabilny)
    url = "https://github.com/urish/cinto/raw/master/media/FluidR3_GM.sf2"
    
    path = assets_soundfont_path()
    folder = os.path.dirname(path)
    filename = os.path.basename(path)

    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[1/3] Utworzono folder '{folder}'")
    else:
        print(f"[1/3] Folder '{folder}' już istnieje")

    if os.path.exists(path):
        # Sprawdzamy rozmiar, żeby nie zostawić uszkodzonego pliku (np. pustego po błędzie 403)
        if os.path.getsize(path) < 1000:
            print("[INFO] Wykryto uszkodzony plik. Usuwanie i ponowne pobieranie...")
            os.remove(path)
        else:
            print(f"[INFO] Plik '{filename}' już istnieje. Pomijam.")
            return

    print(f"[2/3] Pobieranie SoundFontu z GitHuba...")
    print(f"      To ok. 140 MB, proszę czekać...")
    
    try:
        def progress(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r      Pobrano: {percent}%")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\r      Pobrano: {count * block_size / 1024 / 1024:.2f} MB")
                sys.stdout.flush()

        urllib.request.urlretrieve(url, path, progress)
        print("\n[3/3] Sukces! Plik gotowy do użycia.")
    except Exception as e:
        print(f"\n[BŁĄD] Nie udało się pobrać pliku: {e}")

if __name__ == "__main__":
    download_soundfont()
