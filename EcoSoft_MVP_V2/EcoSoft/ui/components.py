# ui/components.py
# Paleta y widgets base fiel al mockup React de EcoSoft

import tkinter as tk

# ─────────────────────────────────────────────────────────────────────────────
#  PALETA DE COLORES  (extraída del mockup React)
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg_app":       "#F9FAFB",
    "bg_white":     "#FFFFFF",
    "bg_gray50":    "#F9FAFB",
    "bg_gray100":   "#F3F4F6",
    "bg_gray200":   "#E5E7EB",

    "green_50":     "#ECFDF5",
    "green_100":    "#D1FAE5",
    "green_200":    "#A7F3D0",
    "green_600":    "#059669",
    "green_700":    "#047857",
    "green_900":    "#064E3B",

    "red_50":       "#FEF2F2",
    "red_100":      "#FEE2E2",
    "red_600":      "#DC2626",
    "red_700":      "#B91C1C",

    "amber_50":     "#FFFBEB",
    "amber_100":    "#FEF3C7",
    "amber_600":    "#D97706",
    "amber_900":    "#92400E",

    "blue_50":      "#EFF6FF",
    "blue_100":     "#DBEAFE",
    "blue_600":     "#2563EB",

    "purple_50":    "#F5F3FF",
    "purple_600":   "#7C3AED",

    "text_900":     "#111827",
    "text_700":     "#374151",
    "text_600":     "#4B5563",
    "text_500":     "#6B7280",
    "text_400":     "#9CA3AF",
    "text_white":   "#FFFFFF",

    "border_200":   "#E5E7EB",
    "border_300":   "#D1D5DB",
}

FF = "Segoe UI"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def lbl(parent, text, size=9, bold=False, fg=None, bg=None,
        anchor="w", wrap=0) -> tk.Label:
    kw = dict(
        text=text,
        font=(FF, size, "bold" if bold else "normal"),
        fg=fg or C["text_900"],
        bg=bg or C["bg_white"],
        anchor=anchor,
    )
    if wrap:
        kw["wraplength"] = wrap
        kw["justify"] = "left"
    return tk.Label(parent, **kw)


def btn(parent, text, cmd, bg=None, fg=None, size=9,
        px=14, py=5) -> tk.Button:
    bg = bg or C["green_600"]
    fg = fg or C["text_white"]
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg,
        activebackground=bg, activeforeground=fg,
        font=(FF, size, "bold"),
        relief="flat", bd=0, cursor="hand2",
        padx=px, pady=py,
    )


def hsep(parent, bg=None) -> tk.Frame:
    return tk.Frame(parent, bg=bg or C["border_200"], height=1)


# ─── Card ────────────────────────────────────────────────────────────────────

class Card(tk.Frame):
    """Panel blanco con borde gris, replica de las cards del mockup."""

    def __init__(self, parent, title="", right_widget_factory=None, **kw):
        super().__init__(
            parent,
            bg=C["bg_white"],
            highlightbackground=C["border_200"],
            highlightthickness=1,
            **kw,
        )
        if title:
            hdr = tk.Frame(self, bg=C["bg_white"])
            hdr.pack(fill="x")
            lbl(hdr, title, size=10, bold=True,
                bg=C["bg_white"]).pack(side="left", padx=16, pady=12)
            if right_widget_factory:
                right_widget_factory(hdr).pack(side="right", padx=16, pady=8)
            hsep(self).pack(fill="x")

    def body(self) -> tk.Frame:
        f = tk.Frame(self, bg=C["bg_white"])
        f.pack(fill="both", expand=True, padx=16, pady=12)
        return f


# ─── StatCard (Dashboard) ────────────────────────────────────────────────────

class StatCard(tk.Frame):
    COLOR_MAP = {
        "green":  (C["green_50"],  C["green_600"]),
        "blue":   (C["blue_50"],   C["blue_600"]),
        "purple": (C["purple_50"], C["purple_600"]),
        "red":    (C["red_50"],    C["red_600"]),
        "amber":  (C["amber_50"],  C["amber_600"]),
    }

    def __init__(self, parent, title, value, subtitle,
                 icon_char, trend_text, trend_up, color="green", **kw):
        super().__init__(
            parent,
            bg=C["bg_white"],
            highlightbackground=C["border_200"],
            highlightthickness=1,
            **kw,
        )
        ibg, ifg = self.COLOR_MAP.get(color, self.COLOR_MAP["green"])

        # Icono
        ico_f = tk.Frame(self, bg=ibg, width=40, height=40)
        ico_f.pack(anchor="nw", padx=16, pady=(16, 6))
        ico_f.pack_propagate(False)
        tk.Label(ico_f, text=icon_char, bg=ibg, fg=ifg,
                 font=(FF, 15)).place(relx=.5, rely=.5, anchor="center")

        # Título gris
        lbl(self, title, size=9, fg=C["text_500"],
            bg=C["bg_white"]).pack(anchor="w", padx=16)

        # Valor principal
        row = tk.Frame(self, bg=C["bg_white"])
        row.pack(anchor="w", padx=16, pady=(2, 0))
        lbl(row, value, size=24, bold=True,
            bg=C["bg_white"]).pack(side="left")
        lbl(row, f"  {subtitle}", size=9, fg=C["text_500"],
            bg=C["bg_white"]).pack(side="left", pady=(8, 0))

        # Tendencia
        tfg = C["green_600"] if trend_up else C["text_500"]
        lbl(self, ("↑ " if trend_up else "") + trend_text,
            size=8, fg=tfg, bg=C["bg_white"]).pack(
            anchor="w", padx=16, pady=(2, 16))


# ─── EnergyIndicator ─────────────────────────────────────────────────────────

class EnergyIndicator(tk.Frame):
    def __init__(self, parent, label, value, unit, status="good", **kw):
        super().__init__(parent, bg=C["bg_white"], **kw)

        top = tk.Frame(self, bg=C["bg_white"])
        top.pack(fill="x")
        lbl(top, label, size=9, bg=C["bg_white"]).pack(side="left")
        r = tk.Frame(top, bg=C["bg_white"])
        r.pack(side="right")
        lbl(r, str(value), size=9, bold=True, bg=C["bg_white"],
            anchor="e").pack(anchor="e")
        lbl(r, unit, size=7, fg=C["text_500"], bg=C["bg_white"],
            anchor="e").pack(anchor="e")

        bar_bg = tk.Frame(self, bg=C["bg_gray200"], height=6)
        bar_bg.pack(fill="x", pady=(3, 0))

        fill_color = C["green_600"] if status == "good" else C["amber_600"]
        pct = min(max(value, 0), 100)

        def _draw():
            w = bar_bg.winfo_width()
            if w < 2:
                bar_bg.after(50, _draw)
                return
            fill_w = int(w * pct / 100)
            tk.Frame(bar_bg, bg=fill_color, height=6,
                     width=fill_w).place(x=0, y=0)
        bar_bg.after(80, _draw)


# ─── OptimizationCard ────────────────────────────────────────────────────────

class OptimizationCard(tk.Frame):
    IMPACT = {
        "high":   (C["red_100"],   C["red_700"],   "⚠"),
        "medium": (C["amber_100"], C["amber_600"],  "⚠"),
        "low":    (C["blue_100"],  C["blue_600"],  "✓"),
    }

    def __init__(self, parent, title, impact, file_path, savings, **kw):
        super().__init__(parent, bg=C["bg_white"], cursor="hand2", **kw)
        ibg, ifg, ichar = self.IMPACT.get(impact, self.IMPACT["low"])

        ico = tk.Frame(self, bg=ibg, width=26, height=26)
        ico.pack(side="left", padx=(0, 10), pady=6)
        ico.pack_propagate(False)
        tk.Label(ico, text=ichar, bg=ibg, fg=ifg,
                 font=(FF, 10, "bold")).place(relx=.5, rely=.5, anchor="center")

        right = tk.Frame(self, bg=C["bg_white"])
        right.pack(side="left", fill="x", expand=True)
        lbl(right, title, size=9, bg=C["bg_white"]).pack(anchor="w")
        meta = tk.Frame(right, bg=C["bg_white"])
        meta.pack(anchor="w")
        lbl(meta, file_path, size=8, fg=C["text_500"],
            bg=C["bg_white"]).pack(side="left")
        lbl(meta, "  •  ", size=8, fg=C["text_500"],
            bg=C["bg_white"]).pack(side="left")
        lbl(meta, savings, size=8, fg=C["green_600"],
            bg=C["bg_white"]).pack(side="left")


# ─── ActivityRow ─────────────────────────────────────────────────────────────

class ActivityRow(tk.Frame):
    def __init__(self, parent, project, time_str, score, **kw):
        super().__init__(parent, bg=C["bg_white"], **kw)
        hsep(self).pack(fill="x")

        inner = tk.Frame(self, bg=C["bg_white"])
        inner.pack(fill="x", padx=16, pady=10)

        ico = tk.Frame(inner, bg=C["green_50"], width=32, height=32)
        ico.pack(side="left", padx=(0, 10))
        ico.pack_propagate(False)
        tk.Label(ico, text="✓", bg=C["green_50"], fg=C["green_600"],
                 font=(FF, 11, "bold")).place(relx=.5, rely=.5, anchor="center")

        info = tk.Frame(inner, bg=C["bg_white"])
        info.pack(side="left", fill="x", expand=True)
        lbl(info, project, size=9, bold=True, bg=C["bg_white"]).pack(anchor="w")
        lbl(info, time_str, size=8, fg=C["text_500"],
            bg=C["bg_white"]).pack(anchor="w")

        sf = tk.Frame(inner, bg=C["bg_white"])
        sf.pack(side="right")
        lbl(sf, f"Score: {score}", size=9, bold=True,
            bg=C["bg_white"], anchor="e").pack(anchor="e")
        lbl(sf, "completed", size=8, fg=C["text_500"],
            bg=C["bg_white"], anchor="e").pack(anchor="e")
        lbl(inner, "›", size=14, fg=C["text_400"],
            bg=C["bg_white"]).pack(side="right", padx=(8, 0))


# ─── MetricRow (Analysis panel) ──────────────────────────────────────────────

class MetricRow(tk.Frame):
    def __init__(self, parent, label, count, description, **kw):
        super().__init__(parent, bg=C["bg_white"], **kw)
        dot_color = (C["green_600"] if count == 0
                     else C["amber_600"] if count <= 2
                     else C["red_600"])
        dot = tk.Frame(self, bg=dot_color, width=8, height=8)
        dot.pack(side="left", padx=(0, 8), pady=10)
        dot.pack_propagate(False)
        lbl(self, label, size=9, bold=True, bg=C["bg_white"]).pack(side="left")
        lbl(self, f"  {count}", size=9, fg=C["text_500"],
            bg=C["bg_white"]).pack(side="left")
        lbl(self, f"  — {description}", size=8, fg=C["text_400"],
            bg=C["bg_white"]).pack(side="left")


# ─── ScoreBadge (Analysis panel score card) ──────────────────────────────────

class ScoreBadge(tk.Frame):
    PALETTE = {
        "Bajo":  (C["green_50"], C["green_700"], C["green_200"], "⚡",
                  "Good performance with room for optimization"),
        "Medio": (C["amber_50"], C["amber_900"], C["amber_100"], "🔆",
                  "Moderate consumption — consider optimizations"),
        "Alto":  (C["red_50"],   C["red_700"],   C["red_100"],  "🔥",
                  "High consumption — optimization recommended"),
    }

    def __init__(self, parent, score, classification, **kw):
        bg, fg, border, icon, desc = self.PALETTE.get(
            classification, self.PALETTE["Bajo"])
        super().__init__(
            parent, bg=bg,
            highlightbackground=border, highlightthickness=2,
            **kw,
        )
        # Ícono
        tk.Label(self, text=icon, bg=bg, fg=fg,
                 font=(FF, 24)).pack(side="left", padx=18, pady=14)
        # Info numérica
        info = tk.Frame(self, bg=bg)
        info.pack(side="left", pady=12)
        tk.Label(info, text="Energy Efficiency Score",
                 font=(FF, 9), fg=fg, bg=bg).pack(anchor="w")
        tk.Label(info, text=f"{score:.0f}",
                 font=(FF, 34, "bold"), fg=fg, bg=bg).pack(anchor="w")
        tk.Label(info, text=f"Clasificación: {classification}",
                 font=(FF, 10, "bold"), fg=fg, bg=bg).pack(anchor="w")
        # Descripción
        tk.Label(self, text=desc, font=(FF, 8), fg=fg, bg=bg,
                 wraplength=155, justify="left").pack(
            side="left", padx=(12, 18), pady=14)


# ─── SuggestionItem ──────────────────────────────────────────────────────────

class SuggestionItem(tk.Frame):
    TYPES = {
        "warning": (C["amber_50"], C["amber_600"], C["amber_100"], "⚠"),
        "info":    (C["blue_50"],  C["blue_600"],  C["blue_100"],  "ℹ"),
        "success": (C["green_50"], C["green_600"], C["green_100"], "✓"),
    }

    def __init__(self, parent, kind, message, **kw):
        bg, fg, border, icon = self.TYPES.get(kind, self.TYPES["info"])
        super().__init__(
            parent, bg=bg,
            highlightbackground=border, highlightthickness=1,
            **kw,
        )
        tk.Label(self, text=icon, bg=bg, fg=fg,
                 font=(FF, 11, "bold")).pack(
            side="left", padx=(10, 6), pady=8)
        tk.Label(self, text=message, bg=bg, fg=C["text_700"],
                 font=(FF, 8), wraplength=310, justify="left",
                 anchor="w").pack(
            side="left", fill="x", expand=True, padx=(0, 8), pady=8)
