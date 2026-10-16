# visualizer_v59.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Maciek (maciej615)
# EriAmo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
import html as html_lib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import base64
from io import BytesIO
from datetime import datetime
from amocore_v59 import AXES_LIST, EPHEMERAL_AXES, under_home

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAIL = True
except ImportError:
    PLOTLY_AVAIL = False
    print("[VIS] Plotly niedostępny - używam matplotlib")


class SoulVisualizerV59:
    """Wizualizator stanu i historii duszy."""

    @property
    def DATA_PATH(self) -> str:
        return under_home("data", "soul_history.csv")

    @property
    def REPORT_DIR(self) -> str:
        return under_home("reports")
    
    def __init__(self):
        os.makedirs(self.REPORT_DIR, exist_ok=True)
        
        # Paleta kolorów dla osi
        self.colors = {
            'logika': '#3498db',      # Niebieski
            'emocje': '#e74c3c',      # Czerwony (efemeryczna)
            'affections': '#9b59b6',  # Fioletowy (trwała!)
            'wiedza': '#f39c12',      # Pomarańczowy
            'czas': '#1abc9c',        # Turkusowy (efemeryczna)
            'kreacja': '#e67e22',     # Ciemny pomarańcz
            'byt': '#34495e',         # Szary
            'przestrzen': '#16a085',  # Morski
            'improwizacja': '#27ae60'  # Zielony
        }

    def _load_data(self) -> pd.DataFrame:
        """Wczytuje dane historyczne."""
        if not os.path.exists(self.DATA_PATH):
            return pd.DataFrame()
        return pd.read_csv(self.DATA_PATH)

    # ============= RAPORT PODSTAWOWY =============
    def create_basic_report(self) -> str:
        """Generuje raport HTML z wykresem radarowym."""
        df = self._load_data()
        if df.empty:
            print("[RAPORT] Brak danych")
            return None
        
        last = df.iloc[-1]
        vec = [last[f"S_{a}"] for a in AXES_LIST]
        safe_description = html_lib.escape(str(last['description']))
        safe_timestamp = html_lib.escape(str(last['timestamp']))
        safe_emotion = html_lib.escape(str(last['emotion_msg']))
        safe_cosine = html_lib.escape(str(last['cos_alpha']))

        finite = [float(value) for value in vec if np.isfinite(value)]
        span = max((abs(value) for value in finite), default=25.0)
        span = max(span, 1.0)
        displayed = [(float(value) / span + 1.0) / 2.0 for value in vec]

        angles = np.linspace(0, 2*np.pi, len(AXES_LIST), endpoint=False).tolist()
        values = displayed + [displayed[0]]
        angles += [angles[0]]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

        ax.fill(angles, values, alpha=0.25, color='#9b59b6')
        ax.plot(angles, values, 'o-', linewidth=2, color='#9b59b6')
        
        # Oznacz osie efemeryczne na czerwono
        labels = []
        for axis in AXES_LIST:
            if axis in EPHEMERAL_AXES:
                labels.append(f"{axis.upper()}\n(efemeryczna)")
            else:
                labels.append(axis.upper())
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=10)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels([f"{-span:.0f}", "0", f"{span:.0f}"])
        ax.set_title(f"Stan Duszy EriAmo v5.9\n{last['description']}", size=14, pad=20)
        ax.grid(True)
        
        # Encode to base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        # HTML
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>EriAmo Soul Report v5.9</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .content {{ 
            background: rgba(255,255,255,0.05); 
            padding: 30px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
        }}
        .metric {{ 
            display: inline-block; 
            margin: 10px; 
            padding: 20px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 10px; 
            min-width: 150px;
            text-align: center;
        }}
        .metric.ephemeral {{ 
            border: 2px solid #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }}
        .metric.persistent {{ 
            border: 2px solid #9b59b6;
            background: rgba(155, 89, 182, 0.1);
        }}
        .metric-label {{ font-size: 12px; color: #aaa; text-transform: uppercase; }}
        .metric-value {{ font-size: 28px; font-weight: bold; margin-top: 5px; }}
        .legend {{ 
            margin: 20px 0; 
            padding: 15px; 
            background: rgba(0,0,0,0.2); 
            border-radius: 10px; 
        }}
        img {{ max-width: 100%; border-radius: 10px; }}
        h1, h2, h3 {{ margin: 0 0 15px 0; }}
        .ephemeral-tag {{ color: #e74c3c; font-size: 10px; }}
        .persistent-tag {{ color: #9b59b6; font-size: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 EriAmo Soul Report v5.9</h1>
        <p>Ontologiczna Pamięć Muzyki z Wygaszaniem Emocji</p>
    </div>
    
    <div class="content">
        <h2>Aktualny Stan Duszy</h2>
        <p><strong>Zdarzenie:</strong> {safe_description}</p>
        <p><strong>Czas:</strong> {safe_timestamp}</p>
        <p><strong>Interpretacja:</strong> {safe_emotion}</p>
        <p><strong>Geometria:</strong> cos(α) = {safe_cosine}</p>
        
        <div class="legend">
            <span class="ephemeral-tag">■ EFEMERYCZNE</span> - wygasają z czasem (emocje, czas) | 
            <span class="persistent-tag">■ TRWAŁE</span> - pamięć głęboka (affections, wiedza, logika...)
        </div>
        
        <h3>Metryki Duszy</h3>
        <div>
            {"".join([
                f'<div class="metric {"ephemeral" if ax in EPHEMERAL_AXES else "persistent"}">'
                f'<div class="metric-label">{ax}</div>'
                f'<div class="metric-value">{vec[i]:+.1f}</div>'
                f'</div>'
                for i, ax in enumerate(AXES_LIST)
            ])}
        </div>
        
        <h3>Wykres Radarowy</h3>
        <img src="data:image/png;base64,{img_b64}" alt="Soul Radar">
        
        <hr style="margin: 40px 0; border-color: #444;">
        <p style="text-align: center; color: #666; font-size: 12px;">
            Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            EriAmo v5.9 - Wygaszanie Emocji / Trwałość Affections
        </p>
    </div>
</body>
</html>"""
        
        path = f"{self.REPORT_DIR}/report_basic.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"[RAPORT] Zapisano: {path}")
        return path

    # ============= TRAJEKTORIA 3D =============
    def create_3d_trajectory(self, axes=['logika', 'emocje', 'affections']) -> str:
        """Wizualizuje trajektorię w przestrzeni 3D."""
        df = self._load_data()
        if len(df) < 3:
            print("[3D] Za mało danych")
            return None
        
        x = df[f"S_{axes[0]}"].values
        y = df[f"S_{axes[1]}"].values
        z = df[f"S_{axes[2]}"].values
        
        if PLOTLY_AVAIL:
            fig = go.Figure(data=[go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines+markers',
                marker=dict(
                    size=6,
                    color=np.arange(len(df)),
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Czas")
                ),
                line=dict(color='rgba(100,100,200,0.6)', width=3),
                text=[html_lib.escape(f"#{row['id_event']}: {str(row['description'])[:30]}") for _, row in df.iterrows()],
                hoverinfo='text'
            )])
            
            fig.update_layout(
                title=f"Trajektoria Duszy: {axes[0]} × {axes[1]} × {axes[2]}",
                scene=dict(
                    xaxis_title=f"{axes[0].upper()} {'(efem.)' if axes[0] in EPHEMERAL_AXES else ''}",
                    yaxis_title=f"{axes[1].upper()} {'(efem.)' if axes[1] in EPHEMERAL_AXES else ''}",
                    zaxis_title=f"{axes[2].upper()} {'(efem.)' if axes[2] in EPHEMERAL_AXES else ''}",
                ),
                width=1000, height=700,
                template='plotly_dark'
            )
            
            path = f"{self.REPORT_DIR}/trajectory_3d.html"
            fig.write_html(path)
        else:
            # Matplotlib 3D
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(x, y, z, 'b-', alpha=0.6)
            ax.scatter(x, y, z, c=np.arange(len(df)), cmap='viridis', s=50)
            ax.set_xlabel(axes[0])
            ax.set_ylabel(axes[1])
            ax.set_zlabel(axes[2])
            ax.set_title("Trajektoria Duszy 3D")
            
            path = f"{self.REPORT_DIR}/trajectory_3d.png"
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
        
        print(f"[3D] Zapisano: {path}")
        return path

    # ============= EWOLUCJA CZASOWA =============
    def create_timeline_evolution(self) -> str:
        """Wykres ewolucji wszystkich osi w czasie."""
        df = self._load_data()
        if df.empty:
            return None
        
        if PLOTLY_AVAIL:
            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=[f"{ax.upper()} {'🔻' if ax in EPHEMERAL_AXES else '💎'}" 
                               for ax in AXES_LIST]
            )
            
            for idx, axis in enumerate(AXES_LIST):
                row = idx // 3 + 1
                col = idx % 3 + 1
                
                # Styl linii: przerywana dla efemerycznych
                dash = 'dot' if axis in EPHEMERAL_AXES else 'solid'
                
                fig.add_trace(
                    go.Scatter(
                        x=df['id_event'],
                        y=df[f'S_{axis}'],
                        mode='lines+markers',
                        name=axis,
                        line=dict(color=self.colors.get(axis, "#95a5a6"), width=2, dash=dash),
                        marker=dict(size=4)
                    ),
                    row=row, col=col
                )
                
                # Linia zerowa
                fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                             opacity=0.3, row=row, col=col)
            
            fig.update_layout(
                title_text="Ewolucja Osi Duszy w Czasie<br><sub>🔻 efemeryczne (wygasają) | 💎 trwałe (pamięć)</sub>",
                height=900, width=1400,
                template='plotly_white',
                showlegend=False
            )
            
            path = f"{self.REPORT_DIR}/timeline_evolution.html"
            fig.write_html(path)
        else:
            fig, axes_plt = plt.subplots(3, 3, figsize=(16, 12))
            fig.suptitle('Ewolucja Osi Duszy w Czasie', fontsize=16)
            
            for idx, axis in enumerate(AXES_LIST):
                ax = axes_plt[idx // 3, idx % 3]
                style = '--' if axis in EPHEMERAL_AXES else '-'
                ax.plot(df['id_event'], df[f'S_{axis}'], 
                       color=self.colors.get(axis, "#95a5a6"), linewidth=2, 
                       linestyle=style, marker='o', markersize=3)
                ax.set_title(f"{axis.upper()} {'(efem.)' if axis in EPHEMERAL_AXES else ''}")
                ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            path = f"{self.REPORT_DIR}/timeline_evolution.png"
            plt.savefig(path, dpi=150)
            plt.close()
        
        print(f"[TIMELINE] Zapisano: {path}")
        return path

    # ============= MAPA EMOCJONALNA =============
    def create_emotional_map(self) -> str:
        """Mapa w przestrzeni emocje × affections."""
        df = self._load_data()
        if df.empty:
            return None
        
        if PLOTLY_AVAIL:
            fig = go.Figure(data=go.Scatter(
                x=df['S_emocje'],
                y=df['S_affections'],
                mode='markers+text',
                marker=dict(
                    size=14,
                    color=df['cos_alpha'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="cos(α)"),
                    line=dict(width=1, color='white')
                ),
                text=[f"#{i}" for i in df['id_event']],
                textposition="top center",
                textfont=dict(size=9),
                hovertemplate=(
                    '<b>Event %{text}</b><br>'
                    'Emocje: %{x:.2f} (efemeryczne)<br>'
                    'Affections: %{y:.2f} (trwałe)<br>'
                    '<extra></extra>'
                )
            ))
            
            # Kwadranty
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Etykiety kwadrantów
            annotations = [
                dict(x=12, y=12, text="Radość<br>+ Głęboki zachwyt", font=dict(color="green")),
                dict(x=-12, y=12, text="Smutek chwilowy<br>+ Głębokie ciepło", font=dict(color="blue")),
                dict(x=-12, y=-12, text="Smutek<br>+ Głęboka trauma", font=dict(color="red")),
                dict(x=12, y=-12, text="Radość chwilowa<br>+ Głęboki niepokój", font=dict(color="orange")),
            ]
            for ann in annotations:
                fig.add_annotation(**ann, showarrow=False, opacity=0.6, font_size=10)
            
            fig.update_layout(
                title="Mapa Emocjonalna Duszy<br><sub>X: Emocje (efemeryczne) | Y: Affections (trwałe)</sub>",
                xaxis_title="EMOCJE (wygasają) →",
                yaxis_title="AFFECTIONS (pamięć głęboka) →",
                width=900, height=700,
                template='plotly_white'
            )
            
            path = f"{self.REPORT_DIR}/emotional_map.html"
            fig.write_html(path)
        else:
            fig, ax = plt.subplots(figsize=(10, 8))
            scatter = ax.scatter(
                df['S_emocje'], df['S_affections'],
                c=df['cos_alpha'], cmap='RdYlGn', s=100,
                edgecolors='black', linewidth=1
            )
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
            ax.axvline(x=0, color='k', linestyle='--', alpha=0.3)
            ax.set_xlabel('Emocje (efemeryczne)')
            ax.set_ylabel('Affections (trwałe)')
            ax.set_title('Mapa Emocjonalna Duszy')
            plt.colorbar(scatter, label='cos(α)')
            
            path = f"{self.REPORT_DIR}/emotional_map.png"
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
        
        print(f"[MAPA] Zapisano: {path}")
        return path

    # ============= PEŁNY RAPORT =============
    def create_complete_report(self) -> dict:
        """Generuje wszystkie wizualizacje."""
        print("\n" + "="*60)
        print("🎨 GENEROWANIE RAPORTU WIZUALIZACJI v5.9")
        print("="*60)
        
        paths = {
            'basic': self.create_basic_report(),
            '3d': self.create_3d_trajectory(),
            'timeline': self.create_timeline_evolution(),
            'emotional': self.create_emotional_map()
        }
        
        print("\n" + "-"*60)
        print("✅ RAPORT WYGENEROWANY")
        for name, path in paths.items():
            if path:
                print(f"  {name.upper()}: {path}")
        print("="*60 + "\n")
        
        return paths

    # ============= LISTA KOMPOZYCJI =============
    def _composition_name(self, filename: str) -> dict:
        """Skleja tokeny nazwy aż do znacznika YYYYMMDD i odcina znany gatunek."""
        stem = filename[:-4] if filename.lower().endswith(".mid") else filename
        tokens = stem.split("_")
        date_at = next(
            (index for index, token in enumerate(tokens) if len(token) == 8 and token.isdigit()),
            None,
        )
        head = tokens[:date_at] if date_at is not None else tokens
        name = "_".join(head) if head else "?"
        from genre_definitions import list_genres
        genre = name
        variant = ""
        for candidate in sorted(list_genres(), key=len, reverse=True):
            if name == candidate or name.startswith(candidate + "_"):
                genre = candidate
                variant = name[len(candidate):].strip("_")
                break
        return {"genre": genre, "variant": variant}

    def list_compositions(self) -> list:
        """Wyświetla listę kompozycji."""
        comp_dir = under_home("compositions")
        if not os.path.exists(comp_dir):
            print("Brak katalogu kompozycji.")
            return []
        
        files = [f for f in os.listdir(comp_dir) if f.endswith('.mid')]
        if not files:
            print("Brak kompozycji.")
            return []
        
        print("\n" + "="*60)
        print("🎵 LISTA KOMPOZYCJI ERIAMO")
        print("="*60)
        
        for i, f in enumerate(files, 1):
            label = self._composition_name(f)
            print(f"{i}. {f}")
            print(f"   Gatunek: {label['genre']}")
            if label["variant"]:
                print(f"   Wariant: {label['variant']}")
            print(f"   Ścieżka: {os.path.join(comp_dir, f)}")
            print("-"*60)
        
        return files
