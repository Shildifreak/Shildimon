def kastlesen(was):
    kaestcheneigenschaften = {}
    zahlenzuweisung = False
    zahl = 0
    zahlendictionary = {}
    breite = 0
    hoehe = 0
    datei = open(was)
    kaestchenliste = []
    for line in datei:
        #print repr (line)
        if not line.lstrip():
            continue
        if "---" in line:
            zahlenzuweisung = True
        if zahlenzuweisung != True:
            breite = max([len(line.split()),breite])
            hoehe += 1
        kaestchenliste.append(line.split())

    zahlenzuweisung = False
    
    y = -hoehe/2 + 1
    for zeile in kaestchenliste:
        # print ''.join(zeile)
        if zeile != []:
            x = breite/2
            for kaestchen in zeile:
                if "---" in kaestchen:
                    zahlenzuweisung = True
                if kaestchen != ".":
                    if zahlenzuweisung == False:
                        kaestcheneigenschaften[(x,y)] = kaestchen
                    else:
                        if zahl != 0:
                            zahlendictionary[zahl] = kaestchen
                            zahl = 0
                        else:
                            try:
                                zahl = int(kaestchen)
                            except ValueError:
                                pass
                x-=1
            y+=1

    for i in zahlendictionary.keys():
        for (key,value)in kaestcheneigenschaften.items():
            if value == str(i):
                kaestcheneigenschaften[key] = zahlendictionary[i]
    return kaestcheneigenschaften
