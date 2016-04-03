# -*- mode: python -*-

block_cipher = None


a = Analysis(['../ShildiEngine.py'],
             pathex=['..', '../modules', '/media/joram/data/joram/Programmierung/Shildimon-versions/ShildiEngine0.2.5/pyinstaller'],
             binaries=None,
             datas=None,
             hiddenimports=['pygameIO'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ShildiEngine',
          debug=False,
          strip=False,
          upx=True,
          console=False )
