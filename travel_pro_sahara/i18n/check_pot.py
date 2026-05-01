import polib
import re

def has_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

po = polib.pofile('travel_pro_sahara.pot')
arabic_entries = [entry for entry in po if has_arabic(entry.msgid)]

print(f"Total entries: {len(po)}")
print(f"Arabic entries: {len(arabic_entries)}")
