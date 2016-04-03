# -*- coding: utf-8 -*-
import json

out = open("myFile.json","w")


data = {"size": [1,1],
        "name": "Landschaftsname",
        "music": "bgmusic.mp3",
        0: {
            "action":"23",
            "background":"boden.png",
            "file":"gras.png",
                },
        "0": "test",
        }

json.dump(data,out,indent=2,ensure_ascii=False)
out.close()

fin = open("myFile.json","r")
print json.load(fin)
fin.close()