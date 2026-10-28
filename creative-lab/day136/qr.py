import cv2
import qrcode
from vcard import make_vcard


def make_qr(text, path, box_size=10, border=4):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    image.save(path)
    return qr.version


def read_qr(path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"No image at {path}")
    text, points, _ = cv2.QRCodeDetector().detectAndDecode(image)
    return text


if __name__ == "__main__":
    card = make_vcard("Sechaba Mofokeng", "+27732239762",
                      email="info@separaka.co.za",
                      company="Separaka Holdings (Pty) Ltd",
                      website="https://separaka.co.za")
    version = make_qr(card, "sechaba_qr.png")
    back = read_qr("sechaba_qr.png")
    print("QR version:", version)
    print("Characters in:", len(card), " out:", len(back))
    print("Round trip OK:", back == card)