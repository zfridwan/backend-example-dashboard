import os
secret_key = os.urandom(24)  # Generates a 24-byte secret key
print(secret_key.hex())      # Convert to a readable hexadecimal string
