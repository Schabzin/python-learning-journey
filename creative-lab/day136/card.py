from PIL import Image, ImageDraw, ImageFont
from qr import make_qr, read_qr
from vcard import make_vcard


WIDTH, HEIGHT = 1600, 900
NAVY = "#14213d"
AMBER = "#fca311"
WHITE = "#ffffff"
LEFT = 100
QR_SIZE = 560
QR_X = WIDTH - QR_SIZE - 100


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def draw_card(card_text, lines, path):
    card = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(card)
    draw.rectangle([0, 0, WIDTH, 24], fill=AMBER)

    y = 150
    for text, size, colour in lines:
        font = load_font("arialbd.ttf" if size >= 60 else "arial.ttf", size)
        if draw.textlength(text, font=font) > QR_X - LEFT - 40:
            raise ValueError(f"Too wide for the card: {text}")
        draw.text((LEFT, y), text, font=font, fill=colour)
        y += size + 30

    qr_path = f"{path}.qr.png"
    make_qr(card_text, qr_path, box_size=8)
    qr = Image.open(qr_path).convert("RGB").resize((QR_SIZE, QR_SIZE), Image.NEAREST)
    qr_y = (HEIGHT - QR_SIZE) // 2
    card.paste(qr, (QR_X, qr_y))
    small = load_font("arial.ttf", 30)
    draw.text((QR_X, qr_y + QR_SIZE + 20), "Scan to save my number", font=small, fill=WHITE)
    card.save(path)


if __name__ == "__main__":
    vcard = make_vcard("Sechaba Mofokeng", "+27732239762",
                       email="info@separaka.co.za",
                       company="Separaka Holdings (Pty) Ltd",
                       website="https://separaka.co.za")
    lines = [
        ("Sechaba Mofokeng", 72, WHITE),
        ("Separaka Holdings (Pty) Ltd", 40, AMBER),
        ("Websites, booking tools and systems", 32, WHITE),
        ("073 223 9762 (call / WhatsApp)", 36, WHITE),
        ("info@separaka.co.za", 36, WHITE),
        ("separaka.co.za", 36, WHITE),
    ]
    draw_card(vcard, lines, "sechaba_card.png")
    print("Card QR reads back:", read_qr("sechaba_card.png") == vcard)