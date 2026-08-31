from py_vapid import Vapid
vapid = Vapid()
vapid.generate_keys()
vapid.save_key("private_key.pem")
vapid.save_public_key("public_key.pem")