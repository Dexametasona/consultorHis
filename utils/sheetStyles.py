from openpyxl.styles import Border, Font, Alignment, Side


vaccineColors = [
    "2563EB", "0F766E", "7C3AED", "C2410C",
    "BE123C", "4D7C0F", "0369A1", "A16207",
    "6D28D9", "047857", "B91C1C", "4338CA",
]

headerStyle = Font(
    name="Calibri",
    bold=True,
    color="FFFFFF"
)

alignment = Alignment(
    horizontal="center",
    vertical="center",
    wrap_text=True
)

border = Border(
    bottom=Side(style="thin", color="FFFFFF")
)