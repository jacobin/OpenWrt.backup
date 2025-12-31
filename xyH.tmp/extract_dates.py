#import re
#
#def extract_dates(text):
#    patterns = [
#        r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',        # YYYY-MM-DD
#        r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',        # DD/MM/YYYY
#        r'\b([A-Za-z]+) (\d{1,2}), (\d{4})\b',     # Month DD, YYYY
#        r'\b(\d{4})\.(\d{1,2})\.(\d{1,2})\b',      # YYYY.MM.DD
#    ]
#
#    dates = []
#    for pattern in patterns:
#        matches = re.findall(pattern, text)
#        for match in matches:
#            dates.append('-'.join(match))
#    return dates
#
#text = "The conference is on 2023-10-30. Another date is 30/10/2023 and also October 30, 2023. Don't forget about 2023.10.32!"
#
#extracted_dates = extract_dates(text)
#print(extracted_dates)
#
#for adate in extracted_dates:
#    print(adate)
#    if isDate(adate):
#        print("{adate} is date")
#    else:
#        print("{adate} is NOT date")


###############################################################################
# https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
txt='''\
Jan 19, 1990
January 19, 1990
Jan 19,1990
01/19/1990
01/19/90
1990
Jan 1990
January1990
2025-12-29
20251229'''

import datetime as dt

fmts = ('%Y','%b %d, %Y','%b %d, %Y','%B %d, %Y','%B %d %Y','%m/%d/%Y','%m/%d/%y','%b %Y','%B%Y','%b %d,%Y','%Y-%m-%d','%Y%m%d')

parsed=[]
for e in txt.splitlines():
    for fmt in fmts:
        try:
           t = dt.datetime.strptime(e, fmt)
           parsed.append((e, fmt, t))
           break
        except ValueError as err:
           pass

# check that all the cases are handled
success={t[0] for t in parsed}
for e in txt.splitlines():
    if e not in success:
        print(e)

for t in parsed:
    print( '"{:20}" => "{:20}" => {}'.format(*t))

