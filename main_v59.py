# main_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
EriAmo v5.9 - Główny Interfejs CLI (UPDATE)
- Wsparcie dla wyboru instrumentów przy kompozycji
- Wygaszanie emocji z zachowaniem affections
"""
import shlex

from amocore_v59 import AXES_LIST, EPHEMERAL_AXES, under_home

_PATH_MARK = "\ue000"
from genre_definitions import get_genre_info, list_genres
from instruments import list_instrument_names
from session import EriAmoSession
from soul_composer_v59 import SoulComposerV59

def print_banner():
    print("\033[96m")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     EriAmo v5.9 - Żywa Dusza AI z Pamięcią Głęboką         ║")
    print("║                                                            ║")
    print("║    🔻 Emocje: EFEMERYCZNE (wygasają z czasem)              ║")
    print("║    💎 Affections: TRWAŁE (pamięć głęboka)                  ║")
    print("║    🎵 Audio: FLAC/OGG + Wybór Instrumentów (Timbre)        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\033[0m")

def print_exit_summary(core):
    print("\n" + "="*60)
    print("🛑 PROCEDURA ZAMKNIĘCIA ERIAMO v5.9")
    print("="*60)
    vec = core.get_vector_copy()
    decay_info = core.get_decay_status()
    print(f"\nStan końcowy Duszy:")
    print("-"*40)
    for i, axis in enumerate(AXES_LIST):
        marker = "🔻" if axis in EPHEMERAL_AXES else "💎"
        print(f"  {marker} {axis.capitalize():12}: {vec[i]:+.2f}")
    print("-"*40)
    print(f"  Cykle wygaszania: {decay_info['cycles_applied']}")
    print(f"  Ostatnie wygaszenie: {decay_info['last_decay']}")
    print(f"  Emocje (🔻): {decay_info['current_emotions']:+.2f}")
    print(f"  Affections (💎): {decay_info['current_affections']:+.2f}")
    final_hash = core.compute_integrity_hash()
    print(f"🔐 SOULGUARD HASH: {final_hash}")
    print("="*60 + "\n")

def print_help():
    print("\n" + "="*70)
    print("📖 POMOC ERIAMO v5.9")
    print("="*70)
    print("\n🎵 KOMPOZYCJA:")
    print("  !compose GATUNEK [INSTRUMENT] [TONIKA]")
    print("     np. !compose BLUES DIST_GUITAR")
    print("     np. !compose MENUET G")
    print("     np. !compose MENUET RIEPEL")
    print("     np. !compose MENUET DIST_GUITAR RIEPEL:G")
    names = ", ".join(list_instrument_names())
    print(f"     Instrumenty: {names}")
    tonics = ", ".join(SoulComposerV59.TONIC_MAP)
    print(f"     Toniki: {tonics}, RIEPEL, RIEPEL:G")
    generated = ", ".join(sorted(SoulComposerV59.GENERATED_GENRES))
    print(f"     Z generatorem: {generated}")
    print("  !genres                      - Katalog i oznaczenie generatora")
    print("  !compositions                - Zapisane MIDI")
    
    print("\n🎓 NAUKA I ANALIZA:")
    print("  !teach \"Tytuł\" CECHY          - Trwałe uczenie")
    print("  !simulate \"Tytuł\" CECHY       - Próba bez pełnego wpływu (0.1x)")
    print("  !web \"Artysta\" \"Utwór\"        - Nauka z MusicBrainz")
    print("  !file ŚCIEŻKA                 - Analiza pliku muzycznego") 
    print("\n⏱️ WYGASZANIE:")
    print("  !decay N                     - Ręczne wygaszanie (N cykli)")
    print("  !decay_status                - Stan systemu")
    
    print("\n🔊 ODTWARZANIE (Windows):")
    print("  !play                        - Ostatnie MIDI (EriAmo-midi albo syntezator Windows)")
    print("  !play ŚCIEŻKA                - Wskazany plik MIDI")
    print("  !stop                        - Zatrzymaj odtwarzanie")
    print("\n🔍 INNE:")
    print("  !report, !trajectory, !timeline, !emotions, !events, !status, !compare")
    print("="*70 + "\n")


def _parse_compose_tail(tokens):
    """Rozdziela instrument i tonikę. RIEPEL oraz nazwa z TONIC_MAP to tonika."""
    tonic_names = set(SoulComposerV59.TONIC_MAP)
    instrument = None
    riepel = False
    pitch = None
    for token in tokens:
        upper = token.upper()
        if upper == "RIEPEL":
            riepel = True
            continue
        if upper.startswith("RIEPEL:"):
            riepel = True
            key = upper.split(":", 1)[1]
            if key:
                pitch = key
            continue
        if upper in tonic_names:
            pitch = upper
            continue
        if instrument is None:
            instrument = token
    if riepel and pitch:
        tonic = f"RIEPEL:{pitch}"
    elif riepel:
        tonic = "RIEPEL"
    else:
        tonic = pitch
    return instrument, tonic

def split_command(raw: str) -> list[str]:
    """Dzieli komendę. Ukośnik w ścieżce Windows zostaje ukośnikiem."""
    protected = []
    quote = None
    index = 0
    while index < len(raw):
        char = raw[index]
        if quote is None:
            if char in "\"'":
                quote = char
            elif char == "\\":
                protected.append(_PATH_MARK)
                index += 1
                continue
            protected.append(char)
        elif quote == "'":
            if char == "'":
                quote = None
            protected.append(char)
        else:
            if char == "\\" and index + 1 < len(raw) and raw[index + 1] in "\\\"":
                protected.append(char)
                protected.append(raw[index + 1])
                index += 2
                continue
            if char == "\\":
                protected.append(_PATH_MARK)
                index += 1
                continue
            if char == '"':
                quote = None
            protected.append(char)
        index += 1
    parts = shlex.split("".join(protected))
    return [part.replace(_PATH_MARK, "\\") for part in parts]


def command_path(parts: list) -> str | None:
    """Ścieżka złożona ze wszystkich słów po komendzie."""
    if len(parts) < 2:
        return None
    text = " ".join(parts[1:]).strip()
    return text or None


def _announce_windows_midi(paths: dict) -> None:
    """Gra zapisane MIDI, gdy nie powstał WAV."""
    try:
        from midi_windows import play_composed_midi
        message = play_composed_midi(paths)
    except Exception as exc:
        print(f"  MIDI zapisane. Odtwarzanie Windows nieudane: {exc}")
        return
    if message:
        print(f"  {message}")


def _play_command(path: str | None) -> None:
    from midi_windows import newest_midi, play_midi, playback_label

    try:
        target = path if path else newest_midi(under_home("compositions"))
        played = play_midi(target)
    except Exception as exc:
        print(f"❌ {exc}")
        return
    print(f"Odtwarzam ({playback_label()}): {played}")


def main():
    print_banner()
    session = EriAmoSession()
    core = session.core

    print("\n💡 Wpisz 'help' aby zobaczyć komendy\n")

    try:
        _command_loop(session, core)
    finally:
        session.shutdown()


def _command_loop(session, core):
    while True:
        try:
            raw = input("\033[90mEriAmo> \033[0m").strip()
            if not raw: continue
            
            if raw.lower() in ["exit", "quit", "q"]:
                print_exit_summary(core)
                break
            
            if raw.lower() in ["help", "?", "pomoc"]:
                print_help()
                continue
            
            try: parts = split_command(raw)
            except ValueError:
                print("❌ Błąd: Niezamknięty cudzysłów"); continue
            
            cmd = parts[0].lower()
            
            # ========== KOMPOZYCJA (ZMODYFIKOWANA) ==========
            if cmd == "!compose":
                if len(parts) < 2:
                    print("❌ Użycie: !compose GATUNEK [INSTRUMENT] [TONIKA]")
                    print(f"   Z generatorem: {', '.join(sorted(SoulComposerV59.GENERATED_GENRES))}")
                    print(f"   Instrumenty: {', '.join(list_instrument_names())}")
                    continue
                
                genre = parts[1].upper()
                instr, tonic = _parse_compose_tail(parts[2:])
                
                try:
                    paths = session.compose(genre, instrument=instr, tonic=tonic)
                    print("\n" + "="*60)
                    label = genre
                    if instr:
                        label += f" ({instr})"
                    if tonic:
                        label += f" [{tonic}]"
                    print(f"✅ SKOMPONOWANO: {label}")
                    print("="*60)
                    for key, path in paths.items():
                        if path: print(f"  {key.upper():4}: {path}")
                    _announce_windows_midi(paths)
                    print("="*60 + "\n")
                except ValueError as e:
                    print(f"❌ {e}")
            
            # ========== RESZTA KOMEND (BEZ ZMIAN) ==========
            elif cmd in ["!teach", "!simulate"]:
                if len(parts) < 3: print("❌ Użycie: !teach \"Tytuł\" CECHY..."); continue
                session.teach(parts[2:], parts[1], mode=cmd)
            
            elif cmd == "!web":
                if len(parts) < 3: print("❌ Użycie: !web \"Artysta\" \"Utwór\""); continue
                session.learn_web(parts[1], parts[2])
            
            elif cmd == "!file":
                path = command_path(parts)
                if not path:
                    print("❌ Użycie: !file ścieżka")
                    continue
                session.learn_file(path)

            elif cmd == "!play":
                _play_command(command_path(parts))

            elif cmd == "!stop":
                from midi_windows import stop_midi
                if stop_midi():
                    print("Zatrzymano odtwarzanie MIDI.")
                else:
                    print("Nic nie jest odtwarzane.")
            
            elif cmd == "!genres":
                print("\n📚 KATALOG GATUNKÓW:")
                print("-"*60)
                generated = SoulComposerV59.GENERATED_GENRES
                for name in sorted(list_genres()):
                    info = get_genre_info(name)
                    if not info:
                        continue
                    aff = info['f_intencja_wektor'].get('affections', 0)
                    mood = "💎+" if aff > 0 else ("💎-" if aff < 0 else "💎0")
                    ready = "generator" if name in generated else "katalog"
                    print(f"  {name:<16} {mood}  [{ready:<9}] {info['opis'][:32]}")
                print("-"*60 + "\n")

            elif cmd == "!compositions":
                session.visualizer.list_compositions()
            
            elif cmd == "!report": session.visualizer.create_complete_report()
            elif cmd == "!trajectory": session.visualizer.create_3d_trajectory()
            elif cmd == "!timeline": session.visualizer.create_timeline_evolution()
            elif cmd == "!emotions": session.visualizer.create_emotional_map()
            
            elif cmd == "!decay":
                try:
                    cycles = int(parts[1]) if len(parts) > 1 else 1
                except ValueError:
                    print("❌ Podaj liczbę całkowitą cykli.")
                    continue
                print(f"\n⏱️ Ręczne wygaszanie: {cycles} cykli...")
                try:
                    vec_before, vec_after = session.decay(cycles)
                except ValueError as decay_error:
                    print(f"❌ {decay_error}")
                    continue
                print(f"  🔻 Emocje: {vec_before[AXES_LIST.index('emocje')]:+.2f} → {vec_after[AXES_LIST.index('emocje')]:+.2f}")
                print("  Zapisano w historii duszy.")
                print("")
            
            elif cmd == "!decay_status":
                status = core.get_decay_status()
                print("\n⏱️ STATUS WYGASZANIA:")
                print(f"  Cykle: {status['cycles_applied']}, Ostatni: {status['last_decay']}")
                print(f"  Emocje (🔻): {status['current_emotions']:+.2f}")
                print(f"  Affections (💎): {status['current_affections']:+.2f}")
                print("")
            
            elif cmd == "!compare":
                if len(parts) < 3: print("❌ Użycie: !compare ID_A ID_B"); continue
                try:
                    id_a, id_b = int(parts[1]), int(parts[2])
                except ValueError:
                    print("❌ ID muszą być liczbami całkowitymi.")
                    continue
                session.reporter.create_report(id_a, id_b)
            
            elif cmd == "!events": session.reporter.list_events()
            
            elif cmd == "!status":
                vec = core.get_vector_copy()
                print("\n" + "="*60 + "\n📊 AKTUALNY STAN DUSZY v5.9\n" + "="*60)
                for i, axis in enumerate(AXES_LIST):
                    val = vec[i]
                    bar = "█" * int(abs(val) / 2)
                    marker, color = ("🔻", "\033[90m") if axis in EPHEMERAL_AXES else ("💎", "\033[0m")
                    print(f"{color}{marker} {axis.capitalize():12} [{'+' if val >= 0 else '-'}]: {bar} {val:+.2f}\033[0m")
                print("-"*60 + f"\n{core.get_emotional_state_description()}\n" + "-"*60)
                print(f"🔐 Hash: {core.compute_integrity_hash()[:40]}...\n" + "="*60 + "\n")
            
            else:
                print(f"❌ Nieznana komenda: {cmd}")

        except KeyboardInterrupt:
            print_exit_summary(core); break
        except Exception as e:
            print(f"❌ Błąd: {e}")
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
