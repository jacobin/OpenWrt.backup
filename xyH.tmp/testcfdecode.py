def cfDecodeEmail(encodedString):
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

# Example Usage:
encoded_email = '07633e6231356531642a623232612a336236372a3f3033342a353f3f3633653e3164346632473637342936373e29353433293336'
# This decodes to a specific email address
decoded_email = cfDecodeEmail(encoded_email)
print(decoded_email)