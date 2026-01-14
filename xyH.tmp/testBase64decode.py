import base64

# 1. The Base64-encoded string
encoded_string_b64 = "SGVsbG8sIFdvcmxkIQ=="

# 2. Convert the Base64 string to a bytes-like object if it's not already
# This is necessary as b64decode operates on bytes
encoded_bytes = encoded_string_b64.encode('utf-8')

# 3. Decode the Base64 bytes
decoded_bytes = base64.b64decode(encoded_bytes)

# 4. Convert the decoded bytes back to the original string format (e.g., 'utf-8')
original_string = decoded_bytes.decode('utf-8')

# Print the result
print(original_string)
# Output: Hello, World!