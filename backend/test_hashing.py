import bcrypt
from passlib.context import CryptContext

try:
    print(f"Bcrypt version: {bcrypt.__version__}")
except AttributeError:
    print("Bcrypt version: Unknown (no __version__)")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "password123"
hashed = pwd_context.hash(password)
print(f"Hashed: {hashed}")

verify = pwd_context.verify(password, hashed)
print(f"Verify: {verify}")
