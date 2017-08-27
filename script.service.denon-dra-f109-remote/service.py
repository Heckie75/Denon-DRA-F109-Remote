import xbmc

import logging

class MyPlayer(xbmc.Player):
    
    def __init__(self):
        xbmc.Player.__init__(self)
 
    def onPlayBackStarted(self):
        logging2.basicConfig(filename="/home/heckie/kodi.log", level=logging.DEBUG)
        logging2.info("play!") 

if __name__ == "__main__":
    player = MyPlayer()
    monitor = xbmc.Monitor()
    while True:
        if monitor.waitForAbort(1):
            break
        xbmc.sleep(500)