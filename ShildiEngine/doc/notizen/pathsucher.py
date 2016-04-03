import os

def lies(path):
    liste=[]
    for datei in os.listdir(path):
        try:
            open(path+datei).close()
        except IOError:
            liste.append((datei,lies(path+datei+"/")))
        else:
            liste.append(datei)
    return liste

print lies("data/Objekte/")
