#!/usr/bin/python3

"""
vulkan app to draw a 3D image
"""
__author__ = 'sunbearc22'
__version__ = "0.1.0"
__license__ = "MIT"

# Python3 modules
import logging

# API
from vulkan import vkDeviceWaitIdle
import sdl2


# Application Modules
import sdl2window_v3_recreateSwapChain as sw
import vulkanbase_v3_recreateSwapChain as vb

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

    def __init__(self):
        self.vulkan_window = None
        
        self._initWindow()
        self._initVulkan(self.vulkan_window);
        self._mainLoop();

    def _initWindow(self):
        self.vulkan_window = sw.SetWindow(title=TITLE, w=WIDTH, h=HEIGHT,
                                          flags=FLAGS)

    def _initVulkan(self, window):
        self.vulkan_base = vb.Setup(window, debug=True)
        print("self.vulkan_base =", self.vulkan_base)

    def _mainLoop(self):
        # Main loop
        running = True
        logging.info('Executing Draw Loop.')
        while running:
            events = sw.sdl2.ext.get_events()
            self.vulkan_base._drawFrame()
            for event in events:
                if event.type == sw.sdl2.SDL_WINDOWEVENT_RESIZED:
                    newWidth,newHeight = window.getWindowSize() 
                    self.vulkan_window = sw.SetWindow(title=TITLE, w=newWidth, h=newHeight,
                                          flags=FLAGS) 
                    #sw.sdl2.SDL_Log("Window %d resized to %dx%d",
                    #                self.vulkan_window.windowID,
                    #                self.vulkan_window.data1,
                    #                self.vulkan_window.data2)
                    
                if event.type == sw.sdl2.SDL_QUIT:
                    logging.info('Leaving Draw Loop: a sdl2 event was detected.')
                    running = False
                    vkDeviceWaitIdle( self.vulkan_base.logical_device )
                    logging.info('Checked all outstanding queue operations for all'
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
