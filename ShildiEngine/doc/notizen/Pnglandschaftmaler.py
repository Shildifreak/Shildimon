import PIL.Image, PIL.ImageTk
from xturtle import*

fd(0)

bild = PIL.Image.new("RGB",(150,150))

verzeichnis = "/home/joram/Shildiwelt/data/Objekte/Landschaftssegmente/"

Teile = [(( 50, 50), "haustuere.png"),
         ((100,100), "hauseckeuntenlinks.png"),
         ((  0,  0), "hausdachlinks.png"),
         ]

for xy, form in Teile:
    bild.paste(PIL.Image.open(verzeichnis+form), xy)


myshape = Shape("image", PIL.ImageTk.PhotoImage(bild))

addshape("myshape", myshape)
shape("myshape")
