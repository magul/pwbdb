# -*- coding: utf-8  -*-

from pwbdb import gerrit

for change in gerrit.get_changes():
    print("""   {}
""".format(change))
