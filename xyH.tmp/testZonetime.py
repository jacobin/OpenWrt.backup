from datetime import datetime
from zoneinfo import ZoneInfo

# An aware datetime object (e.g., from a database or external source)
aware_dt = datetime.now(ZoneInfo("America/New_York"))

print(f"aware_dt: {aware_dt}.")

# A naive datetime object (e.g., from datetime.now())
naive_dt = datetime.now()

print(f"naive_dt: {naive_dt}.")

# Localize the naive datetime to the local timezone, then convert to the aware_dt's timezone (or UTC)
aware_naive_dt = naive_dt.astimezone(aware_dt.tzinfo) # or .astimezone(ZoneInfo("UTC"))

if aware_dt < aware_naive_dt:
    print(f"The {aware_naive_dt} is in the future than \nthe {aware_dt}.")