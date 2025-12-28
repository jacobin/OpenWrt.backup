from bs4 import BeautifulSoup
import re

html_doc = """
<html>
<body>
  <p>Hello, World!aa<q>a</q>aa</p>
  <p>Hello, World!aaaaa</p>
  <p>Hello, World!bbbbb</p>
  <div>Welcome to web scraping</div>
  <p>Welcome to web scraping with BeautifulSoup.</p>
  <span>Some other text</span>
</body>
</html>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

## Find all <p> tags with the exact text "Hello, World!"
#exact_match = soup.find_all("p", string=re.compile("Hello, World!"))
#print(f"Exact match: {exact_match}")

# Find all <p> tags with the exact text "Hello, World!"
exact_match = soup.find_all("p")
for ele in exact_match:
    if "Hello, World!" in ele.get_text():
        print(f"Exact match: {ele}")

#exact_match = soup.find_all("p")
#print(f"Exact match: {exact_match}")
#
## Find all <div> tags that contain the substring "web scraping" using a regular expression
#substring_match_div = soup.find_all("div", string=re.compile("web scraping"))
#print(f"Substring match in div: {substring_match_div}")
#
## Find all tags that contain the substring "web scraping" using a regular expression (any tag)
#substring_match_any = soup.find_all(string=re.compile("web scraping"))
#print(f"Substring match in any tag: {substring_match_any}")