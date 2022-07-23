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
        
def getScreenSaverState():
    return xbmc.getCondVisibility("System.ScreenSaverActive")  

class Observer():
    def __init__(self, cmdStart, cmdStop, functionGetCurrentState):
        self.cmdStart = cmdStart
        self.cmdStop = cmdStop
        self.hysteresisCounter = 0
        self.functionGetCurrentState = functionGetCurrentState
        self.lastState = self.functionGetCurrentState()        
    
    def check(self):
        currentState = self.functionGetCurrentState()            
        if self.lastPlayingState != currentState:
            self.hysteresisCounter += 1
            _log("Change in state found. LastSate="  + str(self.lastState) + " Current State " + str(currentState), True)
            _log("Hysteresis counter = " + str(self.hysteresisCounter) + " Target Hysteresis: " + str(hysteresis), True)
            if self.hysteresisCounter >= hysteresis:
                self.lastState = self.functionGetCurrentState()
                if currentState:
                    runCommand(self.cmdStart, "Start Playing/Screensaver")                        
                else:
                    runCommand(self.cmdStop,"Stop Playing/Screensaver")
            else:
                #wait until hysteresis is completed
                pass
        else:
            self.hysteresisCounter = 0                
            #wait until state changes                
            pass  

class service:
    def __init__(self):
        monitor = xbmc.Monitor()                
        _log ( "started ... (" + str(__version__) + ")" )                
        
        wait(15) # wait 15s before start to let Kodi finish the intro-movie
        
        playingObserver = Observer(reactionCmdStartPlaying, reactionCmdStopPlaying, xbmc.Player().isPlaying)
        screensaverObserver = Observer(reactionCmdScreenSaverOn, reactionCmdScreenSaverOff, getScreenSaverState)        
        
        while not monitor.abortRequested():
            playingObserver.check()    
            screensaverObserver.check()
            monitor.waitForAbort(check_time)

service()