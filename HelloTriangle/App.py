#!/usr/bin/python3

"""
vulkan app to draw a 2D HelloTriangle.
"""
__author__ = 'sunbearc22'
__version__ = "0.1.0"
__license__ = "MIT"

# Python3 modules
import logging

# API
from vulkan import vkDeviceWaitIdle

# Application Modules
import sdl2window as sw
import vulkanbase as vb

###############################################################################
# Global variables
###############################################################################
TITLE = 'HelloTriangle'
WIDTH = 400
HEIGHT = 400
LOGFORMAT = '%(asctime)s [%(process)d] %(name)s %(module)s.%(funcName)-33s'\
            '+%(lineno)-5s: %(levelname)-8s %(message)s'

logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
#logging.basicConfig(level=logging.INFO, format=LOGFORMAT)

class VulkanApp(object):

    def __init__(self):
        self.vulkan_window = None
        
        self._initWindow()
        self._initVulkan(self.vulkan_window);
        self._mainLoop();

    def _initWindow(self):
        self.vulkan_window = sw.SetWindow(title=TITLE, w=WIDTH, h=HEIGHT)

    def _initVulkan(self, window):
        self.vulkan_base = vb.Setup(window)
        print("self.vulkan_base =", self.vulkan_base)

    def _mainLoop(self):
        # Main loop
        running = True
        logging.info('Executing Draw Loop.')
        while running:
            events = sw.sdl2.ext.get_events()
            self.vulkan_base._drawFrame()
            for event in events:
                if event.type == sw.sdl2.SDL_QUIT:
                    logging.info('Exit event triggered: Leaving Draw Loop.')
                    running = False
                    vkDeviceWaitIdle( self.vulkan_base.logical_device )
                    logging.info('All outstanding queue operations for all'
                                 ' queues in Logical Device have ceased.')
                    break

def main():
    app = VulkanApp()
    app.vulkan_base.cleanup()
    app.vulkan_window.destroy()
    print("app =", app)
    

if __name__ == "__main__":
    main()
    print("main =", main)
