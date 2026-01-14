from bs4 import BeautifulSoup

html_doc = """
<div class="example">
Lorem ipsum dolor sit amet. <br>
<a>text inside a_tag</a> consectetur adipiscing elit. <br>
Vivamus nec <a class="someLink" href="example.com">arcu</a> erat. <br>
</div>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# Replace <br> tags with '\n'
for br in soup.find_all('br'):
    br.replace_with('\n')

# Now, get the text of the div
text = soup.get_text(separator="\n", strip=True)
print(text)