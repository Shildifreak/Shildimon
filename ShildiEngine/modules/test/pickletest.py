# -*- coding: utf-8 -*-
import pickle

out = open("myFile.pcl","w")


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

pickle.dump(data,out)
out.close()

fin = open("myFile.pcl","r")
print pickle.load(fin)
fin.close()