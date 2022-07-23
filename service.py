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
check_time = float(selfAddon.getSetting('check_time'))
hysteresis = int(selfAddon.getSetting('hysteresis'))

reactionCmdStartPlaying = selfAddon.getSetting('reactionStartPlaying')
reactionCmdStopPlaying = selfAddon.getSetting('reactionStopPlaying')
reactionCmdScreenSaverOn = selfAddon.getSetting('reactionScreenSaverOn')
reactionCmdScreenSaverOff = selfAddon.getSetting('reactionScreenSaverOff')

def _log( message, showOnlyInDebugMode = False ):
    if showOnlyInDebugMode == False or debug:
        xbmc.log(addon_id + ": " + str(message), level=xbmc.LOGDEBUG)

# wait for abort - xbmc.sleep or time.sleep doesn't work
# and prevents Kodi from exiting
def wait( iTimeToWait ):
    _log ( "DEBUG: wait for " + str(iTimeToWait) + " sec", True )
    if xbmc.Monitor().waitForAbort(int(iTimeToWait)):
        exit()
        
def runCommand(cmd, info=""):
    if len(cmd)>0:
        _log("Run command ("+info+"): " + str(cmd))
        #exitcode = os.system(cmd)
        try:
            result = os.popen(cmd).read()
            _log("Run command result: " + str(result))
        except Exception as e:
            _log("Run command exception: " + str(e))
        
    

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
                _log("Change in state found. LastSate="  + str(lastPlayingState) + " Current State " + str(xbmc.Player().isPlaying()), True)
                _log("Hysteresis counter = " + str(hysteresisCounter) + " Target Hysteresis: " + str(hysteresis), True)
                if hysteresisCounter >= hysteresis:
                    lastPlayingState = xbmc.Player().isPlaying()
                    if xbmc.Player().isPlaying():
                        runCommand(reactionCmdStartPlaying, "Start Playing")                        
                    else:
                        runCommand(reactionCmdStopPlaying,"Stop Playing")
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
