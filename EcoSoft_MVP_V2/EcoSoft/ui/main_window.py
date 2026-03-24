# ui/main_window.py
# Ventana principal de EcoSoft — con editor interactivo, logo y dashboard real
#
# MEJORAS v2:
#   1. Logo SVG generado con Canvas (reemplazable por imagen real)
#   2. Editor de código interactivo (tk.Text) — carga archivo O permite escribir
#   3. Dashboard muestra datos REALES del último análisis realizado
#
# Layout:
#   ┌──────────────────────────────────────────────────────────┐
#   │  TOP MENU BAR  (logo canvas + EcoSoft + menús)          │
#   ├────────────┬─────────────────────────────────────────────┤
#   │            │  Dashboard (datos reales del análisis)      │
#   │  SIDEBAR   │  ─ o ─                                      │
#   │            │  Code Analysis (editor + resultados)        │
#   └────────────┴─────────────────────────────────────────────┘

import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont

from core.analyzer import Analyzer
from models.analysis_result import AnalysisResult
from ui.components import (
    C, FF,
    lbl, btn, hsep,
    Card, StatCard, EnergyIndicator, OptimizationCard,
    ActivityRow, ScoreBadge, SuggestionItem,
)


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("dashboard",       "⊞",  "Dashboard"),
    ("analysis",        "⟨⟩", "Code Analysis"),
    ("recommendations", "💡", "Optimization"),
    ("reports",         "▤",  "Reports"),
    ("projects",        "📁", "Project Manager"),
    ("settings",        "⚙",  "Settings"),
    ("help",            "?",  "Help"),
]

MENU_ITEMS = ["File", "Analysis", "Reports", "Tools", "Settings", "Help"]

# Texto de ejemplo mostrado al abrir el editor por primera vez
PLACEHOLDER_CODE = """\
# ── Escribe o pega tu código Python aquí ──────────────────────────
# También puedes abrir un archivo con el botón "Open File"
#
# Ejemplo con patrones de alto consumo:

def bubble_sort(arr):
    for i in range(len(arr)):          # bucle externo
        for j in range(len(arr) - 1):  # bucle anidado ← costoso
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)        # recursividad ← costoso

cuadrados = [x**2 for x in range(100)] # list comprehension
"""


# ─────────────────────────────────────────────────────────────────────────────
#  LOGO  (dibujado con Canvas — reemplazable por PhotoImage)
# ─────────────────────────────────────────────────────────────────────────────

def build_logo_canvas(parent, size=30) -> tk.Canvas:
    """
    Dibuja un logo vectorial de EcoSoft usando Canvas de Tkinter.
    Para usar una imagen real, reemplaza esta función por:

        img = tk.PhotoImage(file="assets/logo.png")
        lbl = tk.Label(parent, image=img, bg=C["bg_white"])
        lbl.image = img   # <-- evitar que el GC destruya la imagen
        return lbl

    El logo dibujado consiste en:
      • Círculo verde oscuro de fondo
      • Hoja blanca estilizada con curvas de bezier (simuladas con polígono)
      • Punto de brillo blanco arriba-derecha
    """
    c = tk.Canvas(parent, width=size, height=size,
                  bg=C["bg_white"], highlightthickness=0, bd=0)

    # Fondo circular verde
    m = 2  # margen
    c.create_oval(m, m, size - m, size - m,
                  fill=C["green_600"], outline=C["green_700"], width=1)

    # Hoja estilizada (polígono blanco)
    cx, cy = size / 2, size / 2
    s = size * 0.32
    leaf = [
        cx,       cy - s,        # punta superior
        cx + s,   cy,            # punta derecha
        cx + s * 0.4, cy + s,    # base-derecha
        cx - s * 0.4, cy + s,    # base-izquierda
        cx - s,   cy,            # punta izquierda
    ]
    c.create_polygon(leaf, fill="white", outline="", smooth=True)

    # Vena central de la hoja
    c.create_line(cx, cy - s * 0.7, cx, cy + s * 0.7,
                  fill=C["green_600"], width=1)

    # Brillo
    br = size * 0.12
    c.create_oval(cx + s * 0.25, cy - s * 0.6,
                  cx + s * 0.25 + br, cy - s * 0.6 + br,
                  fill="white", outline="")
    return c


# ─────────────────────────────────────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.logo = tk.PhotoImage(file="assets/LogoEcoSoft.png").subsample(30, 30)
        self.analyzer = Analyzer()
        self._filepath = ""

        # Último resultado de análisis (compartido entre páginas)
        self._last_result: AnalysisResult | None = None
        # Historial de análisis para "Recent Analysis" del dashboard
        self._history: list[dict] = []

        self._configure_root()
        self._build_topbar()
        self._build_body()
        self._show_page("dashboard")

    # ── Configuración de ventana ──────────────────────────────────────────────

    def _configure_root(self):
        self.root.iconbitmap("assets/LogoEcoSoft.ico")
        self.root.title("EcoSoft — Analizador de Consumo Energético")
        self.root.configure(bg=C["bg_app"])
        W, H = 1150, 740
        self.root.geometry(f"{W}x{H}")
        self.root.minsize(950, 620)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - W) // 2
        y = (self.root.winfo_screenheight() - H) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── Top Menu Bar ──────────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=C["bg_white"],
                   highlightbackground=C["border_200"],
                   highlightthickness=1, height=48)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # ── Logo + nombre ─────────────────────────────────────────
        logo_frame = tk.Frame(bar, bg=C["bg_white"])
        logo_frame.pack(side="left", padx=(14, 4), pady=6)

        # Logo real (imagen)
        logo_label = tk.Label(logo_frame, image=self.logo, bg=C["bg_white"])
        logo_label.pack(side="left")

        # Texto EcoSoft
        tk.Label(
            logo_frame,
            text="EcoSoft",
            bg=C["bg_white"],
            fg=C["text_900"],
            font=(FF, 13, "bold")
        ).pack(side="left", padx=(8, 20))

        # ── Menús planos ──────────────────────────────────────────
        for name in MENU_ITEMS:
            tk.Button(
                bar, text=name,
                bg=C["bg_white"], fg=C["text_700"],
                activebackground=C["bg_gray100"],
                activeforeground=C["text_900"],
                font=(FF, 9), relief="flat", bd=0,
                cursor="hand2", padx=10, pady=14,
            ).pack(side="left")

        # ── Botón tema ────────────────────────────────────────────
        tk.Button(
            bar, text="🌙",
            bg=C["bg_white"], fg=C["text_700"],
            activebackground=C["bg_gray100"],
            font=(FF, 11), relief="flat", bd=0,
            cursor="hand2", padx=8,
        ).pack(side="right", padx=8)
    
    # ── Body: sidebar + área de contenido ────────────────────────────────────

    def _build_body(self):
        body = tk.Frame(self.root, bg=C["bg_app"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        self._content = tk.Frame(body, bg=C["bg_app"])
        self._content.pack(side="left", fill="both", expand=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent):
        sb = tk.Frame(
            parent, bg=C["bg_white"], width=220,
            highlightbackground=C["border_200"],
            highlightthickness=1,
        )
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        nav_area = tk.Frame(sb, bg=C["bg_white"])
        nav_area.pack(fill="x", padx=8, pady=8)

        self._nav_buttons = {}
        for page_id, icon, label in NAV_ITEMS:
            f = tk.Frame(nav_area, bg=C["bg_white"], cursor="hand2")
            f.pack(fill="x", pady=1)
            item_lbl = tk.Label(
                f, text=f"  {icon}  {label}",
                bg=C["bg_white"], fg=C["text_700"],
                font=(FF, 9), anchor="w", cursor="hand2",
            )
            item_lbl.pack(fill="x", padx=4, pady=7)
            for w in (f, item_lbl):
                w.bind("<Button-1>", lambda e, p=page_id: self._show_page(p))
            self._nav_buttons[page_id] = (f, item_lbl)

        # Relleno + separador + eco-card
        tk.Frame(sb, bg=C["bg_white"]).pack(fill="both", expand=True)
        hsep(sb).pack(fill="x", padx=8)

        eco = tk.Frame(sb, bg=C["green_50"],
                       highlightbackground=C["green_200"],
                       highlightthickness=1)
        eco.pack(fill="x", padx=12, pady=12)
        top_eco = tk.Frame(eco, bg=C["green_50"])
        top_eco.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(top_eco, text="🌱", bg=C["green_50"],
                 fg=C["green_600"], font=(FF, 11)).pack(side="left")
        tk.Label(top_eco, text="  Eco Impact",
                 bg=C["green_50"], fg=C["green_900"],
                 font=(FF, 9, "bold")).pack(side="left")

        # Texto de eco-impact: actualizable si hay resultado
        self._eco_impact_lbl = tk.Label(
            eco, text="Analiza código para ver tu impacto",
            bg=C["green_50"], fg=C["green_700"], font=(FF, 8),
            wraplength=180, justify="left")
        self._eco_impact_lbl.pack(anchor="w", padx=10, pady=(0, 8))

    def _set_nav_active(self, page_id: str):
        for pid, (frame, label) in self._nav_buttons.items():
            if pid == page_id:
                frame.configure(bg=C["green_50"])
                label.configure(bg=C["green_50"], fg=C["green_700"],
                                 font=(FF, 9, "bold"))
            else:
                frame.configure(bg=C["bg_white"])
                label.configure(bg=C["bg_white"], fg=C["text_700"],
                                 font=(FF, 9, "normal"))

    # ── Router de páginas ─────────────────────────────────────────────────────

    def _show_page(self, page_id: str):
        self._set_nav_active(page_id)
        for w in self._content.winfo_children():
            w.destroy()
        if page_id == "dashboard":
            self._render_dashboard()
        elif page_id == "analysis":
            self._render_analysis()
        else:
            self._render_placeholder(page_id)

    # ─────────────────────────────────────────────────────────────────────────
    #  DASHBOARD  — datos REALES del último análisis
    # ─────────────────────────────────────────────────────────────────────────

    def _render_dashboard(self):
        """
        Dashboard con información real del último análisis.
        Si aún no se ha analizado nada, muestra el estado vacío con CTA.
        """
        outer = tk.Frame(self._content, bg=C["bg_app"])
        outer.pack(fill="both", expand=True)

        # Canvas scrollable
        canvas = tk.Canvas(outer, bg=C["bg_app"],
                           highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        page = tk.Frame(canvas, bg=C["bg_app"])
        cw = canvas.create_window((0, 0), window=page, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cw, width=e.width))
        page.bind("<Configure>",
                  lambda e: canvas.configure(
                      scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            -1 if e.delta > 0 else 1, "units"))

        inner = tk.Frame(page, bg=C["bg_app"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        r = self._last_result   # puede ser None

        # ── Header ────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=C["bg_app"])
        hdr.pack(fill="x", pady=(0, 18))
        tf = tk.Frame(hdr, bg=C["bg_app"])
        tf.pack(side="left")
        lbl(tf, "Dashboard", size=18, bold=True,
            bg=C["bg_app"]).pack(anchor="w")
        lbl(tf, "Monitor your code's environmental impact",
            size=9, fg=C["text_500"], bg=C["bg_app"]).pack(anchor="w")
        bf = tk.Frame(hdr, bg=C["bg_app"])
        bf.pack(side="right")
        btn(bf, "+ New Analysis",
            cmd=lambda: self._show_page("analysis"),
            bg=C["green_600"], px=12, py=6).pack(side="left", padx=(0, 6))

        # ── Cuando NO hay análisis aún ────────────────────────────
        if r is None:
            empty = Card(inner)
            empty.pack(fill="x", pady=(0, 18))
            eb = empty.body()
            lbl(eb, "🌿", size=32, bg=C["bg_white"],
                anchor="center").pack(pady=(20, 6))
            lbl(eb, "Aún no has analizado ningún archivo.",
                size=11, bold=True, bg=C["bg_white"],
                anchor="center").pack()
            lbl(eb, 'Ve a "Code Analysis" y analiza tu primer archivo .py\n'
                    'para ver aquí las métricas energéticas reales.',
                size=9, fg=C["text_500"], bg=C["bg_white"],
                anchor="center", wrap=440).pack(pady=(4, 20))
            btn(eb, "Ir al editor →",
                cmd=lambda: self._show_page("analysis"),
                bg=C["green_600"], px=18, py=8).pack(pady=(0, 20))
            return

        # ── 3 StatCards con datos reales ──────────────────────────
        # Calculamos eficiencia: 100 - score (normalizado a 100)
        raw_score = r.energy_score
        efficiency = max(0, 100 - int(raw_score * 2))  # heurística visual
        sustainability = max(0, 100 - int(raw_score * 1.5))

        stats_row = tk.Frame(inner, bg=C["bg_app"])
        stats_row.pack(fill="x", pady=(0, 18))
        for col in range(3):
            stats_row.columnconfigure(col, weight=1)

        cards_data = [
            ("Sustainability Score", str(sustainability), "out of 100", "🌱",
             f"Clasificación: {r.classification}", r.classification == "Bajo", "green"),
            ("Energy Efficiency",    f"{efficiency}%",   "optimized",  "⚡",
             f"Score: {raw_score:.0f} pts",
             r.classification != "Alto", "blue"),
            ("Patrones detectados",  str(sum(r.metrics.values())), "totales", "⊙",
             f"Archivo: {r.filename}",  False, "purple"),
        ]
        for col, (title, val, sub, icon, trend, up, color) in enumerate(cards_data):
            StatCard(stats_row, title, val, sub, icon, trend, up, color).grid(
                row=0, column=col, sticky="nsew",
                padx=(0, 14 if col < 2 else 0),
            )

        # ── 2 columnas: Métricas reales | Recomendaciones ─────────
        two_col = tk.Frame(inner, bg=C["bg_app"])
        two_col.pack(fill="x", pady=(0, 18))
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # Columna izquierda — métricas como barras de progreso
        left_card = Card(two_col, "📊  Métricas del Análisis")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lb = left_card.body()

        metric_display = [
            ("loops",        "Bucles simples",      100, "good"),
            ("nested_loops", "Bucles anidados",     20,  "warning"),
            ("recursion",    "Recursividad",        30,  "warning"),
            ("large_lists",  "List comprehensions", 50,  "good"),
            ("redundancy",   "Redundancias",        10,  "good"),
        ]
        for key, label, scale, default_status in metric_display:
            count = r.metrics.get(key, 0)
            # Normalizar a 0-100 para la barra visual (escalado al rango típico)
            visual = min(count * scale, 100) if scale else 0
            status = "warning" if count > 0 and key in (
                "nested_loops", "recursion") else "good"
            EnergyIndicator(
                lb, label, visual, f"detectados: {count}", status
            ).pack(fill="x", pady=(0, 10))

        # Columna derecha — recomendaciones como optimization cards
        right_card = Card(two_col, "💡  Optimizaciones Sugeridas")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        rb = right_card.body()

        impact_map = {"⚠": "high", "🔄": "medium", "🔍": "medium", "✅": "low"}
        for reco in r.recommendations:
            # Determinar impacto por el emoji inicial
            first_char = reco[:2].strip()
            impact = impact_map.get(first_char, "medium")
            # Texto limpio sin emoji
            clean = reco[2:].strip() if len(reco) > 2 else reco
            # Truncar para la card
            title_text = clean[:60] + "…" if len(clean) > 60 else clean
            detail = clean[60:120] if len(clean) > 60 else "Ver detalles en análisis"
            OptimizationCard(rb, title_text, impact,
                             r.filename, detail).pack(fill="x", pady=(0, 8))

        # ── Recent Analysis (historial real) ──────────────────────
        ra_card = Card(inner, "🕐  Recent Analysis")
        ra_card.pack(fill="x", pady=(0, 24))
        if self._history:
            for entry in reversed(self._history[-5:]):
                ActivityRow(
                    ra_card,
                    entry["filename"],
                    entry["time"],
                    entry["score"],
                ).pack(fill="x")
        else:
            lbl(ra_card, "  Sin análisis previos en esta sesión.",
                size=9, fg=C["text_400"],
                bg=C["bg_white"]).pack(padx=16, pady=12)

    # ─────────────────────────────────────────────────────────────────────────
    #  CODE ANALYSIS  — editor interactivo + panel de resultados
    # ─────────────────────────────────────────────────────────────────────────

    def _render_analysis(self):
        """
        Vista de análisis con editor Text interactivo.
        El usuario puede:
          • Escribir/pegar código directamente en el editor
          • Cargar un archivo (se muestra en el editor)
          • Analizar lo que sea que esté en el editor
        """
        root_f = tk.Frame(self._content, bg=C["bg_app"])
        root_f.pack(fill="both", expand=True)

        # ── Toolbar ───────────────────────────────────────────────
        toolbar = tk.Frame(root_f, bg=C["bg_white"],
                           highlightbackground=C["border_200"],
                           highlightthickness=1, height=46)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        btn(toolbar, "⬆  Open File",
            cmd=self._on_select_file,
            bg=C["green_600"], py=6, px=12).pack(
            side="left", padx=(12, 6), pady=7)

        btn(toolbar, "🗑  Limpiar",
            cmd=self._on_clear_editor,
            bg=C["bg_gray100"], fg=C["text_700"], py=6, px=12).pack(
            side="left", pady=7)

        # Indicador de archivo
        self._toolbar_name = tk.Label(
            toolbar, text="Editor — escribe o carga un archivo",
            bg=C["bg_white"], fg=C["text_500"], font=(FF, 9))
        self._toolbar_name.pack(side="right", padx=(0, 10))

        self._status_dot = tk.Label(
            toolbar, text="●", bg=C["bg_white"],
            fg=C["bg_gray200"], font=(FF, 8))
        self._status_dot.pack(side="right")

        # ── Editor bar (barra justo encima del editor) ─────────────
        editor_bar = tk.Frame(root_f, bg=C["bg_gray50"],
                              highlightbackground=C["border_200"],
                              highlightthickness=1, height=38)
        editor_bar.pack(fill="x")
        editor_bar.pack_propagate(False)

        lbl(editor_bar, "Code Editor", size=9, bold=True,
            bg=C["bg_gray50"]).pack(side="left", padx=16, pady=9)

        # Contador de líneas (actualizable)
        self._line_count_lbl = tk.Label(
            editor_bar, text="Líneas: 0",
            bg=C["bg_gray50"], fg=C["text_400"], font=(FF, 8))
        self._line_count_lbl.pack(side="left", padx=8)

        self._btn_analyze = btn(
            editor_bar, "▶  Analyze Code",
            cmd=self._on_analyze,
            bg=C["green_600"], py=5, px=12)
        self._btn_analyze.pack(side="right", padx=12, pady=5)

        # ── Split principal: editor izq. | resultados der. ─────────
        split = tk.Frame(root_f, bg=C["bg_app"])
        split.pack(fill="both", expand=True)

        # ── Editor de código (tk.Text con numeración de líneas) ────
        editor_outer = tk.Frame(split, bg="#111827")
        editor_outer.pack(side="left", fill="both", expand=True)

        # Numeración de líneas
        self._line_nums = tk.Text(
            editor_outer,
            width=4, padx=6, pady=8,
            state="disabled",
            bg="#1F2937", fg="#4B5563",
            font=("Courier New", 10),
            relief="flat", bd=0,
            cursor="arrow",
            selectbackground="#1F2937",
        )
        self._line_nums.pack(side="left", fill="y")

        # Editor principal
        self._editor = tk.Text(
            editor_outer,
            bg="#111827", fg="#E5E7EB",
            insertbackground="#10B981",      # cursor verde
            selectbackground="#1E3A5F",
            font=("Courier New", 10),
            relief="flat", bd=0,
            padx=8, pady=8,
            wrap="none",
            undo=True,
        )
        self._editor.pack(side="left", fill="both", expand=True)

        # Scrollbars del editor
        vsb_ed = tk.Scrollbar(editor_outer, orient="vertical",
                              command=self._sync_scroll_y)
        vsb_ed.pack(side="right", fill="y")
        self._editor.configure(yscrollcommand=vsb_ed.set)

        hsb_ed = tk.Scrollbar(root_f, orient="horizontal",
                              command=self._editor.xview)
        hsb_ed.pack(side="bottom", fill="x")
        self._editor.configure(xscrollcommand=hsb_ed.set)

        # Insertar código placeholder y activar highlighting básico
        self._editor.insert("1.0", PLACEHOLDER_CODE)
        self._update_line_numbers()
        self._apply_syntax_colors()

        # Eventos del editor
        self._editor.bind("<KeyRelease>", self._on_editor_change)
        self._editor.bind("<ButtonRelease>", self._on_editor_change)

        # ── Panel de resultados (derecha, 390 px) ──────────────────
        self._results_panel = tk.Frame(
            split, bg=C["bg_white"],
            highlightbackground=C["border_200"],
            highlightthickness=1, width=390,
        )
        self._results_panel.pack(side="right", fill="y")
        self._results_panel.pack_propagate(False)

        rp_hdr = tk.Frame(self._results_panel, bg=C["bg_gray50"],
                          highlightbackground=C["border_200"],
                          highlightthickness=1, height=44)
        rp_hdr.pack(fill="x")
        rp_hdr.pack_propagate(False)
        lbl(rp_hdr, "Analysis Results", size=10, bold=True,
            bg=C["bg_gray50"]).pack(side="left", padx=16, pady=10)

        self._rp_body_outer = tk.Frame(self._results_panel, bg=C["bg_white"])
        self._rp_body_outer.pack(fill="both", expand=True)

        # Si ya hay un resultado previo, mostrarlo; si no, placeholder
        if self._last_result:
            self._render_results(self._last_result)
        else:
            self._show_results_placeholder()

    # ── Sincronización de scroll entre líneas y editor ────────────────────────

    def _sync_scroll_y(self, *args):
        self._editor.yview(*args)
        self._line_nums.yview(*args)

    # ── Actualización de numeración de líneas ─────────────────────────────────

    def _update_line_numbers(self):
        """Regenera el widget de numeración de líneas."""
        content = self._editor.get("1.0", "end-1c")
        lines = content.count("\n") + 1

        self._line_count_lbl.config(text=f"Líneas: {lines}")

        self._line_nums.config(state="normal")
        self._line_nums.delete("1.0", "end")
        nums = "\n".join(str(i) for i in range(1, lines + 1))
        self._line_nums.insert("1.0", nums)
        self._line_nums.config(state="disabled")

        # Sincronizar scroll
        self._line_nums.yview_moveto(self._editor.yview()[0])

    # ── Syntax highlighting básico ────────────────────────────────────────────

    def _apply_syntax_colors(self):
        """
        Coloreado simple de palabras clave Python.
        Usa tags de tk.Text para no depender de librerías externas.
        """
        import re

        # Definir tags
        self._editor.tag_configure("keyword",  foreground="#569CD6")  # azul
        self._editor.tag_configure("builtin",  foreground="#4EC9B0")  # verde-azul
        self._editor.tag_configure("comment",  foreground="#6A9955")  # verde
        self._editor.tag_configure("string",   foreground="#CE9178")  # salmón
        self._editor.tag_configure("number",   foreground="#B5CEA8")  # verde claro
        self._editor.tag_configure("decorator",foreground="#DCDCAA")  # amarillo

        # Borrar tags previos
        for tag in ("keyword", "builtin", "comment", "string",
                    "number", "decorator"):
            self._editor.tag_remove(tag, "1.0", "end")

        code = self._editor.get("1.0", "end")

        patterns = [
            ("keyword",   r"\b(def|class|return|if|elif|else|for|while|in|"
                          r"import|from|as|pass|break|continue|try|except|"
                          r"finally|raise|with|yield|lambda|and|or|not|is|"
                          r"None|True|False|async|await|global|nonlocal|del)\b"),
            ("builtin",   r"\b(print|len|range|int|str|float|list|dict|set|"
                          r"tuple|type|isinstance|hasattr|getattr|setattr|"
                          r"enumerate|zip|map|filter|sorted|reversed|sum|"
                          r"min|max|abs|round|open|super|property)\b"),
            ("decorator", r"@\w+"),
            ("number",    r"\b\d+(\.\d+)?\b"),
            ("string",    r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')'),
            ("comment",   r"#[^\n]*"),
        ]

        for tag, pattern in patterns:
            for m in re.finditer(pattern, code):
                start_idx = f"1.0+{m.start()}c"
                end_idx   = f"1.0+{m.end()}c"
                self._editor.tag_add(tag, start_idx, end_idx)

    # ── Evento: cambio en el editor ───────────────────────────────────────────

    def _on_editor_change(self, event=None):
        """Se llama en cada pulsación de tecla dentro del editor."""
        self._update_line_numbers()
        # Re-aplicar coloreado (con debounce implícito por event loop)
        self.root.after(200, self._apply_syntax_colors)

    # ── Placeholder de resultados ─────────────────────────────────────────────

    def _show_results_placeholder(self):
        for w in self._rp_body_outer.winfo_children():
            w.destroy()
        tk.Label(
            self._rp_body_outer,
            text='⟨/⟩\n\nHaz clic en "Analyze Code"\npara comenzar',
            bg=C["bg_white"], fg=C["text_400"],
            font=(FF, 11), justify="center",
        ).place(relx=.5, rely=.4, anchor="center")

    # ── Renderizar resultados en el panel derecho ─────────────────────────────

    def _render_results(self, result: AnalysisResult):
        """Rellena el panel derecho con los resultados reales del análisis."""
        for w in self._rp_body_outer.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self._rp_body_outer, bg=C["bg_white"],
                           highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(self._rp_body_outer, orient="vertical",
                           command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=C["bg_white"])
        cw = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cw, width=e.width))
        body.bind("<Configure>",
                  lambda e: canvas.configure(
                      scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            -1 if e.delta > 0 else 1, "units"))

        content = tk.Frame(body, bg=C["bg_white"])
        content.pack(fill="both", expand=True, padx=16, pady=14)

        # ── Score badge ───────────────────────────────────────────
        ScoreBadge(content, result.energy_score,
                   result.classification).pack(fill="x", pady=(0, 14))

        # ── Performance Impact ────────────────────────────────────
        lbl(content, "📉  Performance Impact", size=9, bold=True,
            bg=C["bg_white"]).pack(anchor="w", pady=(0, 6))

        metric_cards = [
            ("loops",        "Loop Count",          C["green_50"], C["green_600"]),
            ("nested_loops", "Nested Loops",        C["red_50"],   C["red_600"]),
            ("recursion",    "Recursion Calls",     C["amber_50"], C["amber_600"]),
            ("large_lists",  "List Comprehensions", C["blue_50"],  C["blue_600"]),
            ("redundancy",   "Redundant Names",     C["purple_50"],C["purple_600"]),
        ]
        for key, label, _, _ in metric_cards:
            count = result.metrics.get(key, 0)
            level = "good" if count == 0 else ("medium" if count <= 2 else "high")
            lc = {
                "good":   (C["green_50"],  C["green_200"],  C["green_600"]),
                "medium": (C["amber_50"],  C["amber_100"],  C["amber_600"]),
                "high":   (C["red_50"],    C["red_100"],    C["red_600"]),
            }[level]
            cbg, cborder, cfg = lc
            mc = tk.Frame(content, bg=cbg,
                          highlightbackground=cborder, highlightthickness=1)
            mc.pack(fill="x", pady=3)
            top = tk.Frame(mc, bg=cbg)
            top.pack(fill="x", padx=10, pady=(6, 2))
            lbl(top, label, size=9, bold=True, bg=cbg,
                fg=C["text_900"]).pack(side="left")
            dot = tk.Frame(top, bg=cfg, width=8, height=8)
            dot.pack(side="right", padx=(0, 4))
            dot.pack_propagate(False)
            lbl(top, str(count), size=9, bold=True,
                bg=cbg, fg=C["text_900"], anchor="e").pack(side="right")
            desc_map = {0: "Within optimal range",
                        1: "Low — monitor",
                        2: "Moderate impact"}
            lbl(mc, desc_map.get(count, "Can reduce further"),
                size=8, fg=C["text_600"],
                bg=cbg).pack(anchor="w", padx=10, pady=(0, 6))

        # ── Energy Usage Suggestions ──────────────────────────────
        tk.Frame(content, bg=C["border_200"], height=1).pack(
            fill="x", pady=12)
        lbl(content, "ℹ  Energy Usage Suggestions", size=9,
            bold=True, bg=C["bg_white"]).pack(anchor="w", pady=(0, 6))

        for reco in result.recommendations:
            kind = ("success" if "✅" in reco
                    else "warning" if "⚠" in reco
                    else "info")
            SuggestionItem(content, kind, reco).pack(fill="x", pady=3)

        # Nota al pie
        lbl(content,
            "\n* Análisis heurístico con fines educativos (Green IT).",
            size=7, fg=C["text_400"],
            bg=C["bg_white"]).pack(anchor="w", pady=(8, 0))

    # ── PLACEHOLDER para páginas no implementadas ─────────────────────────────

    def _render_placeholder(self, page_id: str):
        label_map = {p: l for p, _, l in NAV_ITEMS}
        name = label_map.get(page_id, page_id)
        f = tk.Frame(self._content, bg=C["bg_app"])
        f.pack(fill="both", expand=True)
        lbl(f, name, size=20, bold=True,
            bg=C["bg_app"]).pack(pady=(80, 8), anchor="center")
        lbl(f, "Esta sección estará disponible en próximas versiones.",
            size=10, fg=C["text_500"],
            bg=C["bg_app"]).pack(anchor="center")

    # ── ACCIONES ──────────────────────────────────────────────────────────────

    def _on_select_file(self):
        """Abre un archivo .py y lo vuelca en el editor."""
        path = filedialog.askopenfilename(
            title="Seleccionar archivo Python",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if not path:
            return
        self._filepath = path
        filename = path.replace("\\", "/").split("/")[-1]

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except Exception as e:
            messagebox.showerror("Error al abrir archivo", str(e))
            return

        # Volcar en el editor
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", code)
        self._update_line_numbers()
        self._apply_syntax_colors()

        # Actualizar indicadores del toolbar
        self._toolbar_name.config(
            text=f"📄 {filename}", fg=C["text_900"])
        self._status_dot.config(fg=C["green_600"])

    def _on_clear_editor(self):
        """Limpia el editor y resetea el estado."""
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", PLACEHOLDER_CODE)
        self._filepath = ""
        self._toolbar_name.config(
            text="Editor — escribe o carga un archivo",
            fg=C["text_500"])
        self._status_dot.config(fg=C["bg_gray200"])
        self._update_line_numbers()
        self._apply_syntax_colors()

    def _on_analyze(self):
        """
        Analiza el contenido ACTUAL del editor.
        Funciona tanto con archivo cargado como con código escrito a mano.
        """
        # Obtener código del editor (ignorar línea vacía final)
        source = self._editor.get("1.0", "end-1c").strip()

        if not source:
            messagebox.showwarning(
                "Editor vacío",
                "Escribe o carga código Python antes de analizar.")
            return

        self._btn_analyze.config(text="Analizando…", state="disabled")
        self.root.update_idletasks()

        # Elegir nombre descriptivo
        if self._filepath:
            filename = self._filepath.replace("\\", "/").split("/")[-1]
            result = self.analyzer.analyze_source(source, filename)
        else:
            result = self.analyzer.analyze_source(source, "<editor>")

        self._btn_analyze.config(text="▶  Analyze Code", state="normal")

        if not result.is_valid():
            messagebox.showerror("Error de análisis", result.error)
            return

        # Guardar como último resultado (lo usa el dashboard)
        self._last_result = result

        # Agregar al historial
        import time as _time
        self._history.append({
            "filename": result.filename,
            "time":     _time.strftime("%H:%M:%S"),
            "score":    int(result.energy_score),
            "cls":      result.classification,
        })

        # Actualizar eco-impact en sidebar
        self._eco_impact_lbl.config(
            text=f"Score: {result.energy_score:.0f} pts\n"
                 f"Clasificación: {result.classification}\n"
                 f"Archivos analizados: {len(self._history)}")

        # Mostrar resultados en panel derecho
        self._render_results(result)

        # Resaltar líneas problemáticas en el editor (marcador visual)
        self._toolbar_name.config(
            text=f"✓ {result.filename}  —  Score: {result.energy_score:.0f} pts",
            fg=C["green_600"])
