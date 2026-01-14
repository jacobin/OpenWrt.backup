from datetime import datetime, timedelta, date
import os

# 1. Subtract days from the current date and time
now = datetime.now()
days_to_subtract = 7
past_date_time = now - timedelta(days=days_to_subtract)

specFileTimeStamp = os.path.getmtime("/etc/openclash/testYaml.py")
specFileDatetime = datetime.fromtimestamp(specFileTimeStamp)

if specFileDatetime < past_date_time:
    print("aaaaaaaaaaaa")
else:
    print("bbbbbbbbbbbb")
