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
from genre_definitions import GENRE_DEFINITIONS, list_genres
from instruments import list_instrument_names
from session import EriAmoSession

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
    final_hash = core.compute_integrity_hash()
    print(f"🔐 SOULGUARD HASH: {final_hash}")
    print("="*60 + "\n")

def print_help():
    print("\n" + "="*70)
    print("📖 POMOC ERIAMO v5.9")
    print("="*70)
    print("\n🎵 KOMPOZYCJA (NOWOŚĆ!):")
    print("  !compose GATUNEK [INSTRUMENT] - Komponuj z wyborem barwy")
    print("     np. !compose BLUES SAX")
    print("     np. !compose MENUET DIST_GUITAR")
    names = ", ".join(list_instrument_names())
    print(f"     Instrumenty: {names}")
    print("  !genres                      - Lista gatunków")
    
    print("\n🎓 NAUKA I ANALIZA:")
    print("  !teach \"Tytuł\" CECHY          - Trwałe uczenie")
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
    print("  !report, !trajectory, !status, !compare")
    print("="*70 + "\n")

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
            
            try: parts = shlex.split(raw)
            except ValueError:
                print("❌ Błąd: Niezamknięty cudzysłów"); continue
            
            cmd = parts[0].lower()
            
            # ========== KOMPOZYCJA (ZMODYFIKOWANA) ==========
            if cmd == "!compose":
                if len(parts) < 2:
                    print("❌ Użycie: !compose GATUNEK [INSTRUMENT]")
                    print(f"   Dostępne: {', '.join(list_genres()[:5])}...")
                    print(f"   Instrumenty: {', '.join(list_instrument_names())}")
                    continue
                
                genre = parts[1].upper()
                instr = parts[2] if len(parts) > 2 else None
                
                try:
                    paths = session.compose(genre, instrument=instr)
                    print("\n" + "="*60)
                    print(f"✅ SKOMPONOWANO: {genre}" + (f" ({instr})" if instr else ""))
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
                if len(parts) < 2: print("❌ Użycie: !file ścieżka"); continue
                session.learn_file(parts[1])

            elif cmd == "!play":
                _play_command(parts[1] if len(parts) > 1 else None)

            elif cmd == "!stop":
                from midi_windows import stop_midi
                if stop_midi():
                    print("Zatrzymano odtwarzanie MIDI.")
                else:
                    print("Nic nie jest odtwarzane.")
            
            elif cmd == "!genres":
                print("\n📚 DOSTĘPNE GATUNKI:")
                print("-"*60)
                for name in sorted(list_genres()):
                    info = GENRE_DEFINITIONS[name]
                    aff = info['f_intencja_wektor'].get('affections', 0)
                    mood = "💎+" if aff > 0 else ("💎-" if aff < 0 else "💎0")
                    print(f"  {name:<16} {mood}  {info['opis'][:40]}")
                print("-"*60 + "\n")
            
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
