import bcrypt

password = "kalikeng2026"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed)

is_correct = bcrypt.checkpw(password.encode(), hashed)
print(is_correct)

is_correct = bcrypt.checkpw("wrongpassword".encode(), hashed)
print(is_correct)

password = "kalikeng2026"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed)

password = "kalikeng2026"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed)

is_correct = bcrypt.checkpw(password.encode(), hashed)
print(is_correct)