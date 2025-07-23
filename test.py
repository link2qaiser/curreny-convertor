import time
import hmac
import hashlib

# Configuration
secret_key = "7638f012cacbeee70261b81df8f07ff6fb8f3316c79c7f17c1ee30d139139587"
target = "dixeam.com"

# Step 1: Generate current UNIX timestamp
timestamp = str(int(time.time()))

# Step 2: Create message to sign (target + timestamp)
message = f"{target}{timestamp}"

# Step 3: Create HMAC-SHA256 signature (as hex)
signature = hmac.new(
    secret_key.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

# Output headers
print("🕒 x-timestamp:", timestamp)
print("🔐 x-signature:", signature)
