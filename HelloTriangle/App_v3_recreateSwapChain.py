#!/usr/bin/python3

"""
vulkan app to draw a 3D image

Amended on: 2017-10-21
Amendments: 1. Corrected py-sdl2 implementation of a resizable window.
            2. Require class VulkanApp to have the d"debug" keyword.  

"""
__author__ = 'sunbearc22'
__version__ = "0.1.0"
__license__ = "MIT"

# Python3 modules
import logging
import ctypes
import sys

# API
from vulkan import vkDeviceWaitIdle
import sdl2
import sdl2.ext


# Application Modules
import sdl2window_v3_recreateSwapChain as sw
import vulkanbase_v3_recreateSwapChain_noSwapDebugPrints as vb

###############################################################################
# Global variables
###############################################################################
TITLE = 'vulkan HelloTriangle - Resizable Window w/ Recreate Swapchain'
WIDTH = 600
HEIGHT = 400
#FLAGS = sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_HIDDEN
FLAGS = sdl2.SDL_WINDOW_RESIZABLE

LOGFORMAT = '%(asctime)s [%(process)d] %(name)s %(module)s.%(funcName)-33s'\
            '+%(lineno)-5s: %(levelname)-8s %(message)s'

logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
#logging.basicConfig(level=logging.INFO, format=LOGFORMAT)

class VulkanApp(object):

    def __init__(self, debug=False):
        self.debug = debug
        self.vulkan_window = None
        
        self._initWindow()
        self._initVulkan();
        self._mainLoop();

    def _initWindow(self):
        self.vulkan_window = sw.SetWindow(title=TITLE, w=WIDTH, h=HEIGHT,
                                          flags=FLAGS)

    def _initVulkan(self):
        self.vulkan_base = vb.Setup(self.vulkan_window, debug=self.debug)
        print("self.vulkan_base =", self.vulkan_base)

    def _mainLoop(self):
        # Main loop
        running = True
        event = sdl2.SDL_Event()
        logging.info('SDL2 Main Loop: Executing.')
        #sdl2.SDL_ShowWindow(self.vulkan_window)

        while running:
            # Poll sdl2 window for currently pending events.
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:        
            
               if event.type == sdl2.SDL_QUIT:
                   logging.info('Leaving SDL2 Main Loop: sdl2.SDL_QUIT.')
                   running = False
                   break

               if event.type == sdl2.SDL_WINDOWEVENT:
                   if event.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
                       newWidth, newHeight = self.vulkan_window.getWindowSize()
                       self.vulkan_base._recreateSwapChain()
                       break

            # Renderer: Present Vulkan images onto sdl2 window.
            self.vulkan_base._drawFrame() 


        vkDeviceWaitIdle( self.vulkan_base.logical_device )
        logging.info('Checked all outstanding queue operations for all'
                    ' queues in Logical Device have ceased.')
        return 0


def main():
    app = VulkanApp(debug=True)
    app.vulkan_base.cleanup1()
    app.vulkan_window.destroy()
    

if __name__ == "__main__":
    sys.exit(main())
