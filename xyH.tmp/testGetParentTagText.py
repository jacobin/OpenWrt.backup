###############################################################################
# https://www.google.com/search?q=python+parent+text+include+child+text
from bs4 import BeautifulSoup

html_data = """
<div class="parent_class">
    Parent text part 1
    <span>Child text</span>
    Parent text part 2
    <p>Another child paragraph</p>
</div>
"""

soup = BeautifulSoup(html_data, 'html.parser')
parent_div = soup.find('div', class_='parent_class')

# Get all text from the parent and its children
all_text2 = parent_div.get_text()
all_text = parent_div.get_text(separator=" ", strip=True)
print(all_text2)
print(all_text)


###############################################################################
html_data = """
<div class="parent_class">
    Parent text part 1
    <span>Child text</span>
    Parent text part 2
    <p>Another </br>child and <br/> para</br>graph</p>
</div>
"""

soup = BeautifulSoup(html_data, 'html.parser')
parent_div = soup.find('div', class_='parent_class')

# Get all text from the parent and its children
all_text2 = parent_div.get_text()
all_text = parent_div.get_text(separator="\n", strip=True)
print(all_text2)
print(all_text)
