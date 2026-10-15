# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
import os
import urllib.request
import sys

from soundfont import SOUNDFONT_MIN_BYTES, SOUNDFONT_URL, assets_soundfont_path


def download_soundfont():
    url = SOUNDFONT_URL
    path = assets_soundfont_path()
    folder = os.path.dirname(path)
    filename = os.path.basename(path)
    temporary = path + ".part"

    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[1/3] Utworzono folder '{folder}'")
    else:
        print(f"[1/3] Folder '{folder}' już istnieje")

    if os.path.exists(path) and os.path.getsize(path) >= SOUNDFONT_MIN_BYTES:
        print(f"[INFO] Plik '{filename}' już istnieje. Pomijam.")
        return
    if os.path.exists(path):
        print("[INFO] Wykryto niepełny SoundFont. Usuwanie i ponowne pobieranie...")
        os.remove(path)
    if os.path.exists(temporary):
        os.remove(temporary)

    print("[2/3] Pobieranie SoundFontu...")
    print("      To ok. 148 MB, proszę czekać...")

    try:
        def progress(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r      Pobrano: {percent}%")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\r      Pobrano: {count * block_size / 1024 / 1024:.2f} MB")
                sys.stdout.flush()

        urllib.request.urlretrieve(url, temporary, progress)
        size = os.path.getsize(temporary) if os.path.exists(temporary) else 0
        if size < SOUNDFONT_MIN_BYTES:
            raise RuntimeError(f"plik ma {size} bajtów, oczekiwano co najmniej {SOUNDFONT_MIN_BYTES}")
        os.replace(temporary, path)
        print("\n[3/3] Sukces! Plik gotowy do użycia.")
    except Exception as exc:
        if os.path.exists(temporary):
            os.remove(temporary)
        print(f"\n[BŁĄD] Nie udało się pobrać pliku: {exc}")


if __name__ == "__main__":
    download_soundfont()
