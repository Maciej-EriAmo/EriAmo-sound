# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Odtwarzanie MIDI.

Gdy obok jest zbudowany EriAmo-midi, !play woła eriamo-midi.exe.
Z SoundFontem gra WASAPI. Bez banku ten sam exe gra syntezator Windows.
Gdy exe nie ma, zostaje lokalny winmm.
"""
from __future__ import annotations

import os
import subprocess
import sys

_player: subprocess.Popen | None = None
_wav_playing = False


def windows_midi_available() -> bool:
    return sys.platform == "win32"


def _validated_path(path: str) -> str:
    if path is None or not str(path).strip():
        raise ValueError("Brak ścieżki MIDI.")
    if '"' in str(path):
        raise ValueError("Ścieżka MIDI nie może zawierać cudzysłowu.")
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return path


def _mci(winmm, command: str) -> tuple[int, str]:
    import ctypes

    buf = ctypes.create_unicode_buffer(512)
    error = winmm.mciSendStringW(command, buf, len(buf), None)
    return int(error), buf.value


def probe_midi(path: str) -> int:
    """Otwiera plik w sekwencerze Windows i zwraca długość we wskaźniku utworu."""
    import ctypes

    path = _validated_path(path)
    if not windows_midi_available():
        raise OSError("Syntezator MIDI Windows jest dostępny tylko w Windows.")
    winmm = ctypes.WinDLL("winmm")
    alias = "eriamo_probe"
    error, message = _mci(winmm, f'open "{path}" type sequencer alias {alias}')
    if error:
        raise RuntimeError(message or f"Windows nie otworzył MIDI (kod {error}).")
    try:
        error, length = _mci(winmm, f"status {alias} length")
        if error:
            raise RuntimeError(length or f"Windows nie odczytał długości MIDI (kod {error}).")
        return int(length)
    finally:
        _mci(winmm, f"close {alias}")


def stop_midi() -> bool:
    """Przerywa odtwarzanie uruchomione z tego procesu."""
    global _player, _wav_playing
    stopped = False
    if _wav_playing:
        import winsound

        winsound.PlaySound(None, winsound.SND_PURGE)
        _wav_playing = False
        stopped = True
    player = _player
    _player = None
    if player is not None and player.poll() is None:
        player.terminate()
        stopped = True
    return stopped


def rust_player_path() -> str | None:
    """eriamo-midi.exe: ERIAMO_MIDI_PLAYER, potem release, potem debug."""
    candidates = []
    env = os.environ.get("ERIAMO_MIDI_PLAYER")
    if env:
        candidates.append(env)
    root = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "EriAmo-midi", "target")
    )
    candidates.append(os.path.join(root, "release", "eriamo-midi.exe"))
    candidates.append(os.path.join(root, "debug", "eriamo-midi.exe"))
    for path in candidates:
        if path and os.path.isfile(path):
            return os.path.abspath(path)
    return None


def resolved_soundfont() -> str | None:
    try:
        from soundfont import resolve_soundfont
    except Exception:
        return None
    try:
        return resolve_soundfont()
    except Exception:
        return None


def playback_label() -> str:
    if not rust_player_path():
        return "syntezator Windows"
    if resolved_soundfont():
        return "EriAmo-midi (SoundFont)"
    return "EriAmo-midi (syntezator Windows)"


def play_command(path: str) -> list[str]:
    player = rust_player_path()
    if not player:
        return [sys.executable, os.path.abspath(__file__), path]
    soundfont = resolved_soundfont()
    if soundfont:
        return [player, "play", "--soundfont", soundfont, path]
    return [player, "play", path]


def play_midi(path: str) -> str:
    """Gra plik w tle. Zwraca ścieżkę bezwzględną."""
    path = _validated_path(path)
    if probe_midi(path) <= 0:
        raise RuntimeError("Plik MIDI nie ma dźwięku, który Windows mógłby zagrać.")
    stop_midi()
    flags = 0
    if sys.platform == "win32":
        flags = (
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW
        )
    global _player
    _player = subprocess.Popen(
        play_command(path),
        creationflags=flags,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    return path


def render_with_player(midi_path: str, wav_path: str) -> str:
    """'ok', 'missing-player', albo opis błędu."""
    player = rust_player_path()
    soundfont = resolved_soundfont()
    if not player or not soundfont:
        return "missing-player"
    try:
        result = subprocess.run(
            [player, "render", "--soundfont", soundfont, midi_path, wav_path],
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return "Render WAV przekroczył 180 sekund."
    except OSError as exc:
        return f"Nie udało się uruchomić EriAmo-midi: {exc}"
    if result.returncode != 0 or not os.path.isfile(wav_path):
        detail = (result.stderr or result.stdout or "").strip()
        return detail or f"EriAmo-midi zakończył się kodem {result.returncode}."
    return "ok"


def play_wav(path: str) -> str:
    """Gra WAV w tle przez winsound. Zwraca ścieżkę bezwzględną."""
    import winsound

    path = _validated_path(path)
    stop_midi()
    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    global _wav_playing
    _wav_playing = True
    return path


def play_composed_midi(paths: dict) -> str | None:
    """Gra WAV kompozycji, a gdy go nie ma — MIDI."""
    if not windows_midi_available() or not paths:
        return None
    wav = paths.get("wav")
    if wav:
        if os.path.isfile(wav):
            played = play_wav(wav)
            return f"Odtwarzam WAV: {played}"
        return None
    if not paths.get("midi"):
        return None
    played = play_midi(paths["midi"])
    return f"Odtwarzam MIDI przez {playback_label()}: {played}"


def newest_midi(folder: str) -> str:
    if not folder or not os.path.isdir(folder):
        raise FileNotFoundError("Brak katalogu kompozycji.")
    files = [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if name.lower().endswith(".mid")
    ]
    if not files:
        raise FileNotFoundError("Brak plików MIDI w katalogu kompozycji.")
    return max(files, key=os.path.getmtime)


def _play_blocking(path: str) -> int:
    import ctypes

    path = _validated_path(path)
    winmm = ctypes.WinDLL("winmm")
    alias = "eriamo_play"
    error, message = _mci(winmm, f'open "{path}" type sequencer alias {alias}')
    if error:
        sys.stderr.write((message or f"Windows nie otworzył MIDI (kod {error}).") + "\n")
        return 1
    try:
        error, message = _mci(winmm, f"play {alias} wait")
        if error:
            sys.stderr.write((message or f"Odtwarzanie MIDI nieudane (kod {error}).") + "\n")
            return 1
        return 0
    finally:
        _mci(winmm, f"close {alias}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(2)
    sys.exit(_play_blocking(sys.argv[1]))
