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
import xbmcaddon
import xbmcvfs
import subprocess

ADDON_ID = 'service.reactions'


def _log(message, show_only_in_debug_mode=False, debug=False):
    if not show_only_in_debug_mode or debug:
        xbmc.log(ADDON_ID + ": " + str(message), level=xbmc.LOGDEBUG)


def run_command(cmd, info="", debug=False):
    if len(cmd) > 0:
        _log("Run command (" + info + "): " + str(cmd), debug=debug)
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            _log("Run command result: " + str(result.stdout), debug=debug)
            if result.stderr:
                _log("Run command stderr: " + str(result.stderr), debug=debug)
        except subprocess.TimeoutExpired:
            _log("Run command timed out after 30s: " + str(cmd), debug=debug)
        except Exception as e:
            _log("Run command exception: " + str(e), debug=debug)


def get_screensaver_state():
    return xbmc.getCondVisibility("System.ScreenSaverActive")


class Observer:
    def __init__(self, cmd_start, cmd_stop, function_get_current_state):
        self.cmd_start = cmd_start
        self.cmd_stop = cmd_stop
        self.hysteresis_counter = 0
        self.function_get_current_state = function_get_current_state
        self.last_state = self.function_get_current_state()

    def check(self, hysteresis, debug=False):
        current_state = self.function_get_current_state()
        if self.last_state != current_state:
            self.hysteresis_counter += 1
            _log("Change in state found. LastState=" + str(self.last_state)
                 + " Current State " + str(current_state), True, debug)
            _log("Hysteresis counter = " + str(self.hysteresis_counter)
                 + " Target Hysteresis: " + str(hysteresis), True, debug)
            if self.hysteresis_counter >= hysteresis:
                self.last_state = current_state
                self.hysteresis_counter = 0
                if current_state:
                    run_command(self.cmd_start, "Start Playing/Screensaver", debug)
                else:
                    run_command(self.cmd_stop, "Stop Playing/Screensaver", debug)
        else:
            self.hysteresis_counter = 0


class ReactionsMonitor(xbmc.Monitor):
    """Custom Monitor that reloads settings when they change in the Kodi GUI."""

    def __init__(self):
        super().__init__()
        self.settings_changed = True  # trigger initial load

    def onSettingsChanged(self):
        self.settings_changed = True


def load_settings():
    """Read all addon settings and return them as a dict."""
    addon = xbmcaddon.Addon(ADDON_ID)
    return {
        'debug': addon.getSettingBool('debug_mode'),
        'check_time': float(addon.getSetting('check_time')),
        'hysteresis': int(addon.getSetting('hysteresis')),
        'reaction_start_playing': addon.getSetting('reactionStartPlaying'),
        'reaction_stop_playing': addon.getSetting('reactionStopPlaying'),
        'reaction_screensaver_on': addon.getSetting('reactionScreenSaverOn'),
        'reaction_screensaver_off': addon.getSetting('reactionScreenSaverOff'),
    }


class Service:
    def __init__(self):
        monitor = ReactionsMonitor()

        addon = xbmcaddon.Addon(ADDON_ID)
        version = addon.getAddonInfo('version')
        _log("started ... (" + str(version) + ")")

        # Wait 15s before start to let Kodi finish the intro-movie
        if monitor.waitForAbort(15):
            return

        settings = load_settings()

        # Keep a persistent Player reference to prevent garbage collection
        player = xbmc.Player()

        playing_observer = Observer(
            settings['reaction_start_playing'],
            settings['reaction_stop_playing'],
            player.isPlaying
        )
        screensaver_observer = Observer(
            settings['reaction_screensaver_on'],
            settings['reaction_screensaver_off'],
            get_screensaver_state
        )

        while not monitor.abortRequested():
            # Reload settings if they were changed in the Kodi GUI
            if monitor.settings_changed:
                monitor.settings_changed = False
                settings = load_settings()
                playing_observer.cmd_start = settings['reaction_start_playing']
                playing_observer.cmd_stop = settings['reaction_stop_playing']
                screensaver_observer.cmd_start = settings['reaction_screensaver_on']
                screensaver_observer.cmd_stop = settings['reaction_screensaver_off']
                _log("Settings (re)loaded", True, settings['debug'])

            playing_observer.check(settings['hysteresis'], settings['debug'])
            screensaver_observer.check(settings['hysteresis'], settings['debug'])
            monitor.waitForAbort(settings['check_time'])


if __name__ == "__main__":
    Service()