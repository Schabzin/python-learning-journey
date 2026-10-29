from urllib.parse import quote
from qr import make_qr
from vcard import make_vcard

MODULE_MM = 0.5


def print_width_mm(version, border=4):
    squares = 17 + 4 * version + 2 * border
    return squares * MODULE_MM


full = make_vcard("Sechaba Mofokeng", "+27732239762",
                  email="info@separaka.co.za",
                  company="Separaka Holdings (Pty) Ltd",
                  website="https://separaka.co.za")
light = make_vcard("Sechaba Mofokeng", "+27732239762", email="info@separaka.co.za")
chat = "https://wa.me/27732239762?text=" + quote("Hi Sechaba, I saw your sheet (LB1).")

for name, text in [("full card", full), ("light card", light), ("chat link", chat)]:
    version = make_qr(text, f"{name.replace(' ', '_')}_qr.png")
    squares = 17 + 4 * version
    print(f"{name}: {len(text)} chars -> version {version} ({squares}x{squares}), "
          f"print at least {print_width_mm(version)} mm wide")