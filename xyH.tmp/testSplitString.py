main_string = "Welcome to the Python programming Python world!"
separator = "Python"

# Unpack the tuple or access the first element by index
before_substring, str2, str3 = main_string.partition(separator)
# or simply
# before_substring = main_string.partition(separator)[0]

print('['+before_substring+']')
print('['+str2+']')
print('['+str3+']')
# Output: Welcome to the