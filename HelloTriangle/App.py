#!/usr/bin/python3

"""
vulkan app to draw a 3D image
"""
__author__ = 'sunbearc22'
__version__ = "0.1.0"
__license__ = "MIT"

# Python3 modules
import logging

# Application Modules
import sdl2window as sw
import vulkanbase as vb

###############################################################################
# Global variables
###############################################################################
TITLE = 'HelloTriangle'
WIDTH = 800
HEIGHT = 800
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
        #w,h = self.vulkan_window.getWindowSize()
        #dw,dh = self.vulkan_window.getDrawableSize()
        #print('self.vulkan_window.info.subsystem =',
        #      slf.vulkan_window.info.subsystem)
        #self.vulkan_window.destroy()

    def _initVulkan(self, window):
        self.vulkan_base = vb.Setup(window)
        print("self.vulkan_base =", self.vulkan_base)

    def _mainLoop(self):
        # Main loop
        running = True
        
        logging.info('Drawing Loop executing')
        while running:
            events = sw.sdl2.ext.get_events()
            self.vulkan_base._drawFrame()
            for event in events:
                if event.type == sw.sdl2.SDL_QUIT:
                    logging.info('Drawing Loop executing')
                    running = False
                    self.vulkan_base.vkDeviceWaitIdle(
                        self.vulkan_base.logical_device)
                    break

def main():
    app = VulkanApp()
    app.vulkan_base.cleanup()
    app.vulkan_window.destroy()
    print("app =", app)
    

if __name__ == "__main__":
    main()
    print("main =", main)
