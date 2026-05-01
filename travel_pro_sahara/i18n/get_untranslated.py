import polib
po = polib.pofile('fr.po')
untranslated = [e.msgid for e in po if not e.msgstr and e.msgid]
with open('untranslated.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(untranslated))
