import string
import random


def createPassword(minlength=8, maxlength=8):
    length = random.randint(minlength, maxlength)
    letters = string.ascii_letters+string.digits  # alphanumeric, upper and lowercase
    return ''.join([random.choice(letters) for _ in range(length)])


def getKeyFromYmlMapEntry(mapEntry):
    crudMapEntry = ''
    if '-' in mapEntry:
        crudMapEntry = mapEntry.split('-')[1].strip()
    else:
        crudMapEntry = mapEntry
    return crudMapEntry.split(':')[0]
