from bs4 import BeautifulSoup

html_doc = """
<main-content>
    Line 1 of content.
    Line 2 of content.
    <span>This is a span within the content.</span>
    Line 3 of content.
</main-content>
"""

# 1. Parse the HTML content
soup = BeautifulSoup(html_doc, 'html.parser')

# 2. Find the specific tag you want to extract from
content_tag = soup.find('main-content')

if content_tag:
    # 3. Get all the text content within the tag
    full_text = content_tag.get_text()

    # 4. Split the text into a list of lines using splitlines()
    # This method automatically handles various newline characters (\n, \r, \r\n)
    lines = full_text.splitlines()

    # 5. Iterate through the lines, stripping any leading/trailing whitespace
    for line in lines:
        stripped_line = line.strip()
        if stripped_line: # Only print non-empty lines
            print(stripped_line)
else:
    print("Tag not found.")