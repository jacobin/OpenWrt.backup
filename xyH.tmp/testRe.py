import re

text = "Line one\nLine two|   \n\r\nLine four"

# Pattern to find a sequence of exactly two newlines
# Using r'\n{2}' explicitly for Unix-style newlines
#pattern_two_newlines = r'\n{2}'
#pattern_two_newlines = r'|\s*[\\r\\n]{2}'
#pattern_two_newlines = r'[\\n]{2}'

# https://www.google.com/search?q=python+regex+find+2+newline
pattern_two_newlines = r'\|\s*(\r?\n){2}'


# The re.search() method is suitable for finding the first occurrence anywhere in the string
match = re.search(pattern_two_newlines, text)

if match:
    print(f"Found two newlines starting at index: {match.start()}")
    print(f"Matched substring: '{match.group()}'")
else:
    print("No sequence of exactly two newlines found.")