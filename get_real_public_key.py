from py_vapid import Vapid
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64

vapid = Vapid.from_file("private_key.pem")
raw_public_key = vapid.public_key.public_bytes(
    encoding=Encoding.X962,
    format=PublicFormat.UncompressedPoint
)
application_server_key = base64.urlsafe_b64encode(raw_public_key).decode("utf-8").rstrip("=")
print(application_server_key)