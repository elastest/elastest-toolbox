def getKeyFromYmlMapEntry(mapEntry):
    crudMapEntry = ''
    if '-' in mapEntry:
        crudMapEntry = mapEntry.split('-')[1].strip()
    else:
        crudMapEntry = mapEntry
    return crudMapEntry.split(':')[0]
