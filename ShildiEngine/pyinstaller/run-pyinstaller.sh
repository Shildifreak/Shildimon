pyinstaller \
   --windowed \
   --onefile \
   --distpath .. \
   --paths ..:../modules \
   --hidden-import pygameIO \
   ../ShildiEngine.py