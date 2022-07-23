# -*- coding: utf-8 -*-

""" Service Kodi Reactions  based on code by haribertlondon, based on enen92, Solo0815

# This program is free software; you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation;
# either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program;
# if not, see <http://www.gnu.org/licenses/>.


"""

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import os

addon_id = 'service.reactions'
selfAddon = xbmcaddon.Addon(addon_id)
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
addonfolder = xbmc.translatePath(selfAddon.getAddonInfo('path'))
__version__ = selfAddon.getAddonInfo('version')

debug=selfAddon.getSetting('debug_mode')
check_time = selfAddon.getSetting('check_time')
hysteresis = int(selfAddon.getSetting('hysteresis'))

reactionStartPlaying = int(selfAddon.getSetting('reactionStartPlaying'))
reactionStopPlaying = selfAddon.getSetting('reactionStopPlaying')
reactionScreenSaverOn = int(selfAddon.getSetting('reactionScreenSaverOn'))
reactionScreenSaverOff = int(selfAddon.getSetting('reactionScreenSaverOff'))

def _log( message ):
    xbmc.log(addon_id + ": " + str(message), level=xbmc.LOGDEBUG)

# wait for abort - xbmc.sleep or time.sleep doesn't work
# and prevents Kodi from exiting
def wait( iTimeToWait ):
    if debug == 'true':
        _log ( "DEBUG: wait for " + str(iTimeToWait) + " sec" )
    if xbmc.Monitor().waitForAbort(int(iTimeToWait)):
        exit()
        
def runCommand(cmd):
    _log("Run command: ", cmd)
    os.system(cmd)
    

class service:
    def __init__(self):
        monitor = xbmc.Monitor()                
        _log ( "started ... (" + str(__version__) + ")" )                

        # wait 15s before start to let Kodi finish the intro-movie
        wait(15)
        
        lastPlayingState = xbmc.Player().isPlaying()
        hysteresisCounter = 0
        while not monitor.abortRequested():
            if lastPlayingState != xbmc.Player().isPlaying():
                hysteresisCounter += 1
                
                if hysteresisCounter >= hysteresis:
                    lastPlayingState = xbmc.Player().isPlaying()
                    if xbmc.Player().isPlaying():
                        runCommand(reactionStartPlaying)                        
                    else:
                        runCommand(reactionStopPlaying)
                else:
                    #wait until hysteresis is completed
                    pass
            else:
                hysteresisCounter = 0                
                #wait until state changes                
                pass
                
            monitor.waitForAbort(check_time)

service()

#idle_time = xbmc.getGlobalIdleTime()
#{"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": { "booleans": ["System.ScreenSaverActive "] }, "id": 1}
#xbmc.executebuiltin('PlayerControl(Stop)')
#xbmc.executebuiltin('SetVolume(%d,showVolumeBar)' % (curVol))
#xbmc.executebuiltin('ActivateScreensaver')
#os.system(cmd)
#{"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": { "booleans": ["System.ScreenSaverActive "] }, "id": 1}
