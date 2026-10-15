# main_gui_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
EriAmo v5.9 - Interfejs Graficzny
- Wizualizacja wygaszania emocji
- Rozróżnienie osi efemerycznych i trwałych
- Bezpieczna obsługa wątków
"""
import customtkinter as ctk
import threading
import queue
import os
import sys
from pathlib import Path

# WAŻNE: Ustawienie backendu matplotlib PRZED importem
import matplotlib
matplotlib.use('Agg')  # Backend bez GUI - zapobiega konfliktom z Tkinter

from amocore_v59 import AXES_LIST, EPHEMERAL_AXES
from genre_definitions import list_genres
from instruments import list_instrument_names
from session import EriAmoSession

# Dark mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class EriAmoBrain(threading.Thread):
    """
    Wątek logiczny (backend).
    Wszystkie operacje I/O i obliczenia wykonywane są tutaj,
    żeby nie blokować GUI.
    """
    
    def __init__(self, session, cmd_queue, resp_queue):
        super().__init__(daemon=True)
        self.session = session
        self.core = session.core
        self.cmd_queue = cmd_queue
        self.resp_queue = resp_queue
        self.running = True

    def run(self):
        self.core.log("[SYSTEM] Wątek Mózgu: Aktywny", "CYAN")
        
        while self.running:
            try:
                task = self.cmd_queue.get(timeout=0.5)
                cmd_type = task['type']
                
                if cmd_type == 'STOP':
                    self.running = False
                    break
                
                elif cmd_type == 'ANALYZE':
                    self._handle_analyze(task)
                
                elif cmd_type == 'COMPOSE':
                    self._handle_compose(task)
                
                elif cmd_type == 'REPORT':
                    self._handle_report()
                
                elif cmd_type == 'DECAY':
                    cycles = task.get('cycles', 1)
                    self.session.decay(cycles)
                    self.resp_queue.put({"status": "LOG", "msg": f"Wygaszanie: {cycles} cykli (zapisane)"})
                
                # Zawsze aktualizuj stan po operacji
                self.send_soul_update()
                
            except queue.Empty:
                continue
            except Exception as e:
                import traceback
                self.resp_queue.put({
                    "status": "ERROR", 
                    "msg": f"Błąd: {e}\n{traceback.format_exc()}"
                })

    def _handle_analyze(self, task):
        """Obsługa analizy utworu."""
        title = task['title']
        features = list(task['features'])  # Kopia
        
        if task.get('artist'):
            try:
                web_features = self.session.loader.get_context_from_web(task['artist'], title)
                features.extend(web_features or [])
            except Exception as e:
                self.resp_queue.put({"status": "LOG", "msg": f"Web: {e}"})
        
        mode = "!teach" if task['mode'] == 'full' else "!simulate"
        self.session.teach(features, title, mode=mode)
        self.resp_queue.put({"status": "LOG", "msg": f"Analiza: {title}"})

    def _handle_compose(self, task):
        """Obsługa kompozycji."""
        genre = task['genre']
        instrument = task.get('instrument', None)  # Opcjonalny instrument
        try:
            paths = self.session.compose(genre, instrument=instrument)
            self.resp_queue.put({
                "status": "SUCCESS", 
                "msg": f"Skomponowano {genre}!" + (f" ({instrument})" if instrument else ""), 
                "data": paths
            })
        except Exception as e:
            self.resp_queue.put({"status": "ERROR", "msg": str(e)})

    def _handle_report(self):
        """Obsługa generowania raportu."""
        try:
            paths = self.session.visualizer.create_complete_report()
            self.resp_queue.put({"status": "REPORT_READY", "paths": paths})
        except Exception as e:
            self.resp_queue.put({"status": "ERROR", "msg": f"Raport: {e}"})

    def send_soul_update(self):
        """Wysyła aktualny stan do GUI."""
        try:
            vec = self.core.get_vector_copy()
            vector_dict = {AXES_LIST[i]: vec[i] for i in range(len(AXES_LIST))}
            decay_status = self.core.get_decay_status()
            self.resp_queue.put({
                "status": "UPDATE_VECTORS", 
                "data": vector_dict,
                "decay": decay_status
            })
        except Exception as e:
            print(f"[WARN] send_soul_update: {e}")


class EriAmoApp(ctk.CTk):
    """Główne okno aplikacji."""
    
    def __init__(self):
        super().__init__()
        
        self.title("EriAmo v5.9 - Soul Interface")
        self.geometry("1150x700")
        
        # Kolejki komunikacyjne
        self.cmd_queue = queue.Queue()
        self.resp_queue = queue.Queue()
        
        self.session = EriAmoSession()
        self.core = self.session.core
        
        # Start wątku roboczego
        self.brain = EriAmoBrain(self.session, self.cmd_queue, self.resp_queue)
        self.brain.start()
        
        # Buduj UI
        self._init_ui()
        
        # Start pętli GUI
        self._gui_loop_id = None
        self._start_gui_loop()
        
        # Początkowy stan
        self.after(100, lambda: self.brain.send_soul_update())

    def _init_ui(self):
        """Buduje interfejs użytkownika."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # === LEWY PANEL - WEKTORY ===
        self._build_left_panel()
        
        # === PRAWY PANEL - AKCJE ===
        self._build_right_panel()

    def _build_left_panel(self):
        """Panel z wektorami duszy."""
        self.frame_left = ctk.CTkFrame(self, width=270, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_left.grid_propagate(False)
        
        # Logo
        lbl_logo = ctk.CTkLabel(
            self.frame_left, 
            text="ERIAMO v5.9", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_logo.grid(row=0, column=0, padx=20, pady=(15, 3))
        
        # Subtitle
        lbl_sub = ctk.CTkLabel(
            self.frame_left,
            text="Efemeryczne | Trwale",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        lbl_sub.grid(row=1, column=0, padx=20, pady=(0, 10))
        
        # Paski wektorów
        self.vector_bars = {}
        self.vector_labels = {}
        
        for i, axis in enumerate(AXES_LIST):
            prefix = "[E]" if axis in EPHEMERAL_AXES else "[T]"
            
            lbl = ctk.CTkLabel(
                self.frame_left, 
                text=f"{prefix} {axis.upper()}: 0.0", 
                anchor="w",
                font=ctk.CTkFont(size=10)
            )
            lbl.grid(row=i*2+2, column=0, padx=20, pady=(6, 0), sticky="w")
            
            pbar = ctk.CTkProgressBar(self.frame_left, width=210, height=10)
            pbar.grid(row=i*2+3, column=0, padx=20, pady=(2, 0))
            pbar.set(0.5)
            
            # Kolory według typu osi
            if axis in EPHEMERAL_AXES:
                pbar.configure(progress_color="#7f8c8d")  # Szary
            elif axis == 'affections':
                pbar.configure(progress_color="#9b59b6")  # Fioletowy
            elif axis == 'improwizacja':
                pbar.configure(progress_color="#27ae60")  # Zielony
            elif axis in ['logika', 'wiedza']:
                pbar.configure(progress_color="#3498db")  # Niebieski
            else:
                pbar.configure(progress_color="#e67e22")  # Pomarańczowy
            
            self.vector_bars[axis] = pbar
            self.vector_labels[axis] = lbl
        
        # Przycisk Decay
        btn_decay = ctk.CTkButton(
            self.frame_left, 
            text="Wygas emocje (1 cykl)",
            command=self._send_decay,
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            height=30,
            font=ctk.CTkFont(size=11)
        )
        btn_decay.grid(row=len(AXES_LIST)*2+4, column=0, padx=20, pady=(15, 10))

    def _build_right_panel(self):
        """Panel z zakładkami akcji."""
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=15, pady=15)
        
        self.tabview = ctk.CTkTabview(self.frame_right)
        self.tabview.pack(fill="both", expand=True)
        
        # Zakładki
        self.tab_analyze = self.tabview.add("NAUKA")
        self.tab_compose = self.tabview.add("KOMPOZYCJA")
        self.tab_logs = self.tabview.add("LOG")
        
        self._setup_analyze_tab()
        self._setup_compose_tab()
        self._setup_logs_tab()

    def _setup_analyze_tab(self):
        """Zakładka nauki/analizy."""
        frame = ctk.CTkFrame(self.tab_analyze, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.entry_artist = ctk.CTkEntry(
            frame, 
            placeholder_text="Artysta (np. Chopin, Metallica)",
            height=35
        )
        self.entry_artist.pack(pady=8, fill="x")
        
        self.entry_title = ctk.CTkEntry(
            frame, 
            placeholder_text="Tytul utworu / Opis zdarzenia",
            height=35
        )
        self.entry_title.pack(pady=8, fill="x")
        
        self.entry_features = ctk.CTkEntry(
            frame, 
            placeholder_text="Cechy (np. FUGA LAMENTOSO PRESTO)",
            height=35
        )
        self.entry_features.pack(pady=8, fill="x")
        
        # Przyciski
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        btn_teach = ctk.CTkButton(
            btn_frame, 
            text="[T] NAUCZ (trwaly wplyw)", 
            command=lambda: self._send_analyze('full'),
            fg_color="#9b59b6",
            width=180
        )
        btn_teach.pack(side="left", padx=8)
        
        btn_sim = ctk.CTkButton(
            btn_frame, 
            text="[E] SYMULUJ (0.1x)", 
            command=lambda: self._send_analyze('sim'),
            fg_color="transparent", 
            border_width=2,
            width=150
        )
        btn_sim.pack(side="left", padx=8)
        
        # Info
        info = ctk.CTkLabel(
            frame, 
            text="[E] Emocje wygasaja z czasem\n[T] Affections pozostaja jako pamieci gleboka",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        info.pack(pady=20)

    def _setup_compose_tab(self):
        """Zakładka kompozycji."""
        frame = ctk.CTkFrame(self.tab_compose, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        lbl = ctk.CTkLabel(
            frame, 
            text="Wybierz gatunek:", 
            font=ctk.CTkFont(size=14)
        )
        lbl.pack(pady=15)
        
        self.genre_var = ctk.StringVar(value="BLUES")
        genres = list_genres()
        
        self.combo_genre = ctk.CTkComboBox(
            frame, 
            values=genres, 
            variable=self.genre_var,
            width=220
        )
        self.combo_genre.pack(pady=10)
        
        # NOWOŚĆ: Wybór instrumentu
        lbl_instr = ctk.CTkLabel(
            frame,
            text="Instrument (opcjonalnie):",
            font=ctk.CTkFont(size=12)
        )
        lbl_instr.pack(pady=(15, 5))
        
        instruments = ["Auto"] + list_instrument_names()
        self.instrument_var = ctk.StringVar(value="Auto")
        
        self.combo_instrument = ctk.CTkComboBox(
            frame,
            values=instruments,
            variable=self.instrument_var,
            width=220
        )
        self.combo_instrument.pack(pady=5)
        
        btn_compose = ctk.CTkButton(
            frame, 
            text="KOMPONUJ", 
            height=45, 
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._send_compose,
            fg_color="#9b59b6",
            width=200
        )
        btn_compose.pack(pady=25)

        btn_play = ctk.CTkButton(
            frame,
            text="Odtwórz MIDI",
            fg_color="#1abc9c",
            command=self._play_last_midi,
            width=200
        )
        btn_play.pack(pady=5)
        
        btn_report = ctk.CTkButton(
            frame, 
            text="Generuj raport wizualny", 
            fg_color="#e67e22",
            command=self._send_report,
            width=200
        )
        btn_report.pack(pady=10)

    def _setup_logs_tab(self):
        """Zakładka logów."""
        self.textbox_log = ctk.CTkTextbox(
            self.tab_logs, 
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.textbox_log.pack(fill="both", expand=True, padx=10, pady=10)
        self.textbox_log.insert("0.0", "=== EriAmo v5.9 Log ===\n")
        self.textbox_log.insert("end", "[E] efemeryczne (wygasaja)\n")
        self.textbox_log.insert("end", "[T] trwale (pamiec gleboka)\n\n")

    # === PETLA GUI ===
    
    def _start_gui_loop(self):
        """Uruchamia pętlę sprawdzającą odpowiedzi."""
        self._process_responses()
        self._gui_loop_id = self.after(150, self._start_gui_loop)

    def _process_responses(self):
        """Przetwarza odpowiedzi z wątku roboczego."""
        try:
            for _ in range(10):  # Max 10 wiadomości na raz
                msg = self.resp_queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass

    def _handle_message(self, msg):
        """Obsługuje pojedynczą wiadomość."""
        status = msg.get('status', '')
        
        if status == "UPDATE_VECTORS":
            self._update_vectors(msg['data'])
        
        elif status == "LOG":
            self._log(f"[INFO] {msg['msg']}")
        
        elif status == "SUCCESS":
            self._log(f"[OK] {msg['msg']}")
            data = msg.get('data') or {}
            if data.get('midi'):
                self.last_midi = data['midi']
                self._log(f"   MIDI: {data['midi']}")
            if data.get('txt'):
                self._log(f"   Plik: {data['txt']}")
            self._play_windows_midi(data)
        
        elif status == "REPORT_READY":
            self._log("[RAPORT] Gotowy")
            paths = msg.get('paths', {})
            if paths.get('basic'):
                self._log(f"   {paths['basic']}")
                # Otwórz w przeglądarce
                try:
                    import webbrowser
                    webbrowser.open(Path(paths['basic']).resolve().as_uri())
                except Exception:
                    pass
        
        elif status == "ERROR":
            self._log(f"[BLAD] {msg['msg']}")

    def _update_vectors(self, data):
        """Aktualizuje paski wektorów."""
        for axis, val in data.items():
            if axis in self.vector_bars:
                # Normalizacja -30..30 -> 0..1
                norm = 0.5 + (val / 60.0)
                norm = max(0.0, min(1.0, norm))
                self.vector_bars[axis].set(norm)
                
                prefix = "[E]" if axis in EPHEMERAL_AXES else "[T]"
                self.vector_labels[axis].configure(
                    text=f"{prefix} {axis.upper()}: {val:+.1f}"
                )

    def _log(self, text):
        """Dodaje tekst do logu."""
        self.textbox_log.insert("end", f"{text}\n")
        self.textbox_log.see("end")

    # === WYSYLANIE KOMEND ===
    
    def _send_analyze(self, mode):
        """Wysyła komendę analizy."""
        title = self.entry_title.get().strip()
        if not title:
            self._log("BLAD: Podaj tytul!")
            return
        
        artist = self.entry_artist.get().strip()
        feats = self.entry_features.get().strip().split()
        
        self.cmd_queue.put({
            'type': 'ANALYZE',
            'title': title,
            'artist': artist,
            'features': feats,
            'mode': mode
        })
        self._log(f"Wyslano: {title}...")

    def _play_windows_midi(self, paths):
        """Gra WAV kompozycji, a gdy go nie ma — MIDI."""
        if not paths:
            return
        wav = paths.get("wav")
        if wav and os.path.isfile(wav):
            try:
                from midi_windows import play_wav
                played = play_wav(wav)
                self._log(f"[AUDIO] Odtwarzam WAV: {played}")
            except Exception as exc:
                self._log(f"[AUDIO] {exc}")
                if paths.get("midi"):
                    self._play_midi_path(paths["midi"])
            return
        if paths.get("midi"):
            self._play_midi_path(paths["midi"])

    def _play_last_midi(self):
        path = getattr(self, "last_midi", None)
        if not path:
            try:
                from amocore_v59 import under_home
                from midi_windows import newest_midi
                path = newest_midi(under_home("compositions"))
            except Exception as exc:
                self._log(f"[MIDI] {exc}")
                return
        self._play_midi_path(path)

    def _play_midi_path(self, path):
        try:
            from midi_windows import play_midi, playback_label
            played = play_midi(path)
            self.last_midi = played
            self._log(f"[MIDI] Odtwarzam przez {playback_label()}: {played}")
        except Exception as exc:
            self._log(f"[MIDI] {exc}")

    def _send_compose(self):
        """Wysyła komendę kompozycji."""
        genre = self.genre_var.get()
        instrument = self.instrument_var.get()
        
        # "Auto" oznacza brak wybranego instrumentu
        if instrument == "Auto":
            instrument = None
        
        self.cmd_queue.put({
            'type': 'COMPOSE', 
            'genre': genre,
            'instrument': instrument
        })
        
        msg = f"Komponuje: {genre}"
        if instrument:
            msg += f" ({instrument})"
        self._log(msg + "...")

    def _send_report(self):
        """Wysyła komendę raportu."""
        self.cmd_queue.put({'type': 'REPORT'})
        self._log("Generuje raport...")

    def _send_decay(self):
        """Wysyła komendę wygaszania."""
        self.cmd_queue.put({'type': 'DECAY', 'cycles': 1})
        self._log("Wygaszanie emocji...")

    # === ZAMYKANIE ===
    
    def on_closing(self):
        """Bezpieczne zamknięcie aplikacji."""
        # Zatrzymaj pętlę GUI
        if self._gui_loop_id:
            self.after_cancel(self._gui_loop_id)
        
        # Zatrzymaj wątek roboczy
        self.cmd_queue.put({'type': 'STOP'})
        self.brain.join(timeout=2.0)
        self.session.shutdown()
        
        # Zamknij okno
        self.destroy()


def main():
    """Punkt wejścia."""
    app = EriAmoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_closing()


if __name__ == "__main__":
    main()
