from bs4 import BeautifulSoup, NavigableString, Tag

html_content = """
<h1>Title 1</h1>
<p>This is the first paragraph.</p>
<div>This is a div.</div>
<h2>Subtitle A</h2>
<h1>Title 2</h1>
<p>This is the second paragraph.</p>
<span>Some span content</span>
<h2>Subtitle B</h2>
"""

soup = BeautifulSoup(html_content, 'html.parser')

start_tag = soup.find("h1", string="Title 1")
end_tag = soup.find("h1", string="Title 2")

tags_between = []
current_element = start_tag.next_sibling

while current_element and current_element != end_tag:
    # Check if the element is an actual tag and not just a newline or whitespace
    if isinstance(current_element, Tag):
        tags_between.append(current_element)
    # You can also collect NavigableString if you want raw text
    # elif isinstance(current_element, NavigableString) and current_element.strip():
    #     tags_between.append(current_element.strip())

    current_element = current_element.next_sibling

# Print the found tags
for tag in tags_between:
    print(f"Found tag: <{tag.name}> with text: '{tag.get_text(strip=True)}'")

# Example of extracting just the text:
all_text = ' '.join(tag.get_text(strip=True) for tag in tags_between)
print(f"\nAll text combined: '{all_text}'")
