
from tkinter import ttk


def configStyle(root):

    # Tema visual
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # Colores
    BG = "#F3F6FA"
    SURFACE = "#FFFFFF"
    TEXT = "#1E293B"
    MUTED = "#64748B"
    PRIMARY = "#2563EB"
    PRIMARY_ACTIVE = "#1D4ED8"
    BORDER = "#DCE3ED"

    root.configure(bg=BG)

    # Contenedores
    style.configure(
        "App.TFrame",
        background=BG,
    )

    style.configure(
        "Card.TLabelframe",
        background=SURFACE,
        bordercolor=BORDER,
        relief="solid",
        borderwidth=1,
    )

    style.configure(
        "Card.TLabelframe.Label",
        background=SURFACE,
        foreground=TEXT,
        font=("Segoe UI", 10, "bold"),
    )

    # Textos
    style.configure(
        "App.TLabel",
        background=SURFACE,
        foreground=TEXT,
        font=("Segoe UI", 10),
    )

    style.configure(
        "Muted.TLabel",
        background=SURFACE,
        foreground=MUTED,
        font=("Segoe UI", 9),
    )

    # Campos de entrada
    style.configure(
        "App.TEntry",
        padding=7,
        fieldbackground="#FFFFFF",
        foreground=TEXT,
        bordercolor=BORDER,
    )

    # Botón principal
    style.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 9),
        background=PRIMARY,
        foreground="#FFFFFF",
        borderwidth=0,
    )

    style.map(
        "Primary.TButton",
        background=[
            ("disabled", "#A8B7D0"),
            ("pressed", PRIMARY_ACTIVE),
            ("active", PRIMARY_ACTIVE),
        ],
        foreground=[
            ("disabled", "#F1F5F9"),
            ("!disabled", "#FFFFFF"),
        ],
    )

    # Botón secundario
    style.configure(
        "Secondary.TButton",
        font=("Segoe UI", 9),
        padding=(10, 8),
        background="#E8EFFD",
        foreground=PRIMARY,
        borderwidth=0,
    )

    style.map(
        "Secondary.TButton",
        background=[
            ("pressed", "#D5E2FC"),
            ("active", "#D5E2FC"),
        ],
    )
