import webbrowser

url = "http://sites.google.com/site/shildimon"
downloadurl = url+"/download/Shildimon1.7.tar.bz2"

def openshildisite():
    webbrowser.open(url)

def openshildidownloadsite():
    webbrowser.open(downloadurl)

#openshildidownloadsite()
openshildisite()
