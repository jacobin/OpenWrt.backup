from bs4 import BeautifulSoup

html_doc = """
<html>
<body>
    <div id="target">
        Here is some <b>important</b> and <i>nested</i> text.
    </div>
    <div>
        Another div with different text.
    </div>
</body>
</html>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# The text to search for
target_text = "Here is some important and nested text."

# Find the first tag where the stripped text content matches the target
found_tag = next((tag for tag in soup.find_all() if tag.get_text(strip=True) == target_text.strip()), None)

if found_tag:
    print(f"Found tag: {found_tag.name}, ID: {found_tag.get('id')}")
else:
    print("Tag not found.")

#from bs4 import BeautifulSoup
#
#html_doc = """
#<html>
#<body>
#    <div id="target">
#        Here is some <b>important</b> and <i>nested</i> text.
#    </div>
#    <div>
#        Another div with different text.
#    </div>
#</body>
#</html>
#"""
#
#soup = BeautifulSoup(html_doc, 'html.parser')
#
## The partial text to search for
#partial_text = "important"
#
## Find all tags that contain the partial text
#matching_tags = []
#for tag in soup.find_all('div'):
#    if partial_text in tag.get_text():
#        matching_tags.append(tag)
#
#print(f"Found {len(matching_tags)} matching tags containing '{partial_text}':")
#for tag in matching_tags:
#    # Print the tag name and its full text for context
#    print(f"- <{tag.name}> (Text: {tag.get_text(strip=True)[:50]}...)")