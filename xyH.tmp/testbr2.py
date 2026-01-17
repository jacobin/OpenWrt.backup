from bs4 import BeautifulSoup

page = '''<h1 class="para-title">A quick brown fox jumps over</br>the lazy dog
<span>some stuff here</span></h1>'''

soup = BeautifulSoup(page, 'html.parser')
title_box = soup.find('h1', attrs={'class': 'para-title'})
title = title_box.get_text(separator=" ").strip()
print (title)





# 扯直了测试
page = '''<h1 class="para-title">A quick brown fox jumps over</br>the lazy dog<span>some stuff here</span></h1>'''

soup = BeautifulSoup(page, 'html.parser')
title_box = soup.find('h1', attrs={'class': 'para-title'})
title = title_box.get_text(separator=" ").strip()
print (title)
