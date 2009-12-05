import gedit

import ui


class SnapBuffersPlugin(gedit.Plugin):
    _decorators = {}

    def activate(self, window):
        self._decorators[window] = WindowDecorator(self, window)

    def deactivate(self, window):
        deco = self._decorators.pop(window)
        deco.cleanup()
        del deco

    def update_ui(self, window):
        window = self._decorators.get(window)
        # Don't know why yet, but update_ui is called earlier than activate
        if window:
            window.update_ui()


class WindowDecorator(object):
    window = None

    def __init__(self, plugin, window):
        self.window = ui.PluginWindow(plugin, window)

    def update_ui(self):
        pass

    def cleanup(self):
        self.window.cleanup()

