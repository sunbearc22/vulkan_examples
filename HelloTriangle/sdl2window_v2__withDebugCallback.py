#!/bin/env python3

''' Create & Destroy Window for Vulkan App using SDL2.

Class & Functions:
- SetWindow
  - _create
  - _info
  - _getVulkanSurfaceExtension
  - getWindowSize
  - getDrawableSize
  - destroy 
'''
__author__ = 'sunbearc22'
__version__ = "0.1.0"
__license__ = "MIT"

# Python3 modules
import logging
import ctypes

# Windowing module
import sdl2
import sdl2.ext

#LOGFORMAT = '%(asctime)s [%(process)d] %(name)s %(module)s.%(funcName)-33s +%(lineno)-5s: %(levelname)-8s %(message)s'
LOGFORMAT = '%(asctime)s %(module)-15s.%(funcName)-30s +%(lineno)-5s: %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
#logging.basicConfig(level=logging.INFO, format=LOGFORMAT)

class SetWindow:
    """ Class to create, destroy and manage sdl2 window.

    Input Parameters: 
     title - title
     x     - x position, use sdl2.SDL_WINDOWPOS_CENTERED, or
                             sdl2.SDL_WINDOWPOS_UNDEFINED
     y     - y position, use sdl2.SDL_WINDOWPOS_CENTERED, or
                             sdl2.SDL_WINDOWPOS_UNDEFINED
     w     - width, in pixel
     h     - height, in pixel
     flags - may be any of sdl2.SDL_WindowFlags OR'd together
             -see http://wiki.libsdl.org/SDL_Init#Remarks
       0                             -default
       SDL_WINDOW_FULLSCREEN         -fullscreen window
       SDL_WINDOW_FULLSCREEN_DESKTOP -fullscreen window at the current desktop
                                      resolution
       SDL_WINDOW_HIDDEN             -window is not visible
       SDL_WINDOW_BORDERLESS         -no window decoration
       SDL_WINDOW_RESIZABLE          -window can be resized
       SDL_WINDOW_MINIMIZED          -window is minimized
       SDL_WINDOW_MAXIMIZED          -window is maximized
       SDL_WINDOW_INPUT_GRABBED      -window has grabbed input focus
       SDL_WINDOW_ALLOW_HIGHDPI      -window should be created in high-DPI mode
                                      if supported (>= SDL 2.0.1)  
    """
    
    
    def __init__(self, title="SDL2 Window", x=sdl2.SDL_WINDOWPOS_UNDEFINED,
                 y=sdl2.SDL_WINDOWPOS_UNDEFINED, w=400, h=400, flag=0):
        """Initialisation"""
        self.title = title
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.flag = flag
        logging.info('SDL2 Window parameters initialised')

        self.window = None # sdl2 window.
        self.info = None   # sdl2 window struct with version and subsystem info.
        self.vsurface_extension = None  # Vulkan surface extension

        self._create()
        self._info()
        self.display_server_protocol = self._getSurfaceExtension()


    def _create(self):
        '''Create SDL2 Window'''

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            logging.error('SDL2 library with video flag fail to initialise')
            exit()
        logging.info('SDL2 library with video flag initialised.')

        self.window = sdl2.SDL_CreateWindow( self.title.encode('ascii'),
                                             self.x, self.y,
                                             self.w, self.h,
                                             self.flag)
        if not self.window: 
            logging.error('Fail to create SDL2 window.')
            exit()
        logging.info('Created SDL2 Window: {}.'.format(self.title))


    def _info(self):
        '''Get SDL2 version and system's Display Server type'''

        self.info = sdl2.SDL_SysWMinfo()
        logging.info('Initialise variable for SDL2 version and subsystem info.')

        sdl2.SDL_VERSION(self.info.version) 
        logging.info('- version = {0}.{1}.{2}'.format(
            self.info.version.major,
            self.info.version.minor,
            self.info.version.patch))

        if sdl2.SDL_GetWindowWMInfo(self.window, ctypes.byref(self.info)) != 1:
            logging.error('sdl2.SDL_GetWindowWMInfo failed: Could not get '
                          'window subsystem.')
            exit()
        logging.info('- subsystem = {0}'.format(self.info.subsystem))
 

    def _getSurfaceExtension(self):
        '''Get Vulkan surface extension for system's display-server-protocol.'''
        if  self.info.subsystem == sdl2.SDL_SYSWM_WINDOWS:
            logging.info('- subsystem is Microsoft Windows ==>'
                         ' VK_KHR_win32_surface')
            return 'VK_KHR_win32_surface'
        elif self.info.subsystem == sdl2.SDL_SYSWM_X11:
            logging.info('- subsystem is X Window System ==>'
                        ' VK_KHR_xlib_surface')
            return 'VK_KHR_xlib_surface'
            #logging.info('- subsystem is X Window System ==>'
            #              ' VK_KHR_xcb_surface')
            #return 'VK_KHR_xcb_surface'
        elif self.info.subsystem == sdl2.SDL_SYSWM_COCOA:
            logging.info('- subsystem is Apple Mac OS X ==>'
                         ' VK_MVK_macos_surface')
            return 'VK_MVK_macos_surface'
        elif self.info.subsystem == sdl2.SDL_SYSWM_UNIKIT:
            logging.info('- subsystem is Apple iOS ==> VK_MVK_ios_surface')
            return 'VK_MVK_ios_surface'
        elif sdl2.SDL_VERSION_ATLEAST(2, 0, 2):
            if self.info.subsystem == sdl2.SDL_SYSWM_WAYLAND:
                logging.info('- subsystem is Wayland (>= SDL 2.0.2) ==>'
                             ' VK_KHR_wayland_surface')
                return 'VK_KHR_wayland_surface'
            elif self.info.subsystem == sdl2.SDL_SYSWM_MIR:
                logging.info('- subsystem is Mir (>= SDL 2.0.2) ==>'
                             ' VK_KHR_mir_surface')
                return 'VK_KHR_mir_surface'
        elif sdl2.SDL_VERSION_ATLEAST(2, 0, 4):
            if self.info.subsystem == sdl2.SDL_SYSWM_ANDROID:
                logging.info('- subsystem is Android (>= SDL 2.0.4) ==>'
                             ' VK_KHR_android_surface')
                return 'VK_KHR_android_surface'
        elif sdl2.SDL_VERSION_ATLEAST(2, 0, 5):
            if self.info.subsystem == sdl2.SDL_SYSWM_VIVANTE:
                logging.info('- subsystem is Vivante (>= SDL 2.0.5) ==>'
                             ' VK_MN_vi_surface')
                return 'VK_MN_vi_surface'
        else:
            logging.error('Window manager not compatible with SDL2. Exit.')
            exit()


    def getWindowSize(self):
        '''Get SDL2 Window width & height '''
        w = ctypes.c_int() # Represents the C signed int datatype
        h = ctypes.c_int()
        sdl2.SDL_GetWindowSize( self.window, w, h )
        logging.info('sdlWindowsize = {}'.format([w.value, h.value]))
        return w, h


    def getDrawableSize(self):
        '''Get SDL2 Window drawable space width & height '''
        dw = ctypes.c_int()
        dh = ctypes.c_int()
        sdl2.SDL_GL_GetDrawableSize( self.window, dw, dh )
        logging.info('sdlGetDrawableSize = {}'.format([dw.value, dh.value]) )
        return dw, dh


    def destroy(self):
        '''Destroy and quit SDL2 window'''
        sdl2.SDL_DestroyWindow(self.window) # Close and destroy SDL2 window
        sdl2.SDL_Quit() # Clean up SDL2
        logging.info('Destroyed SDL2 window and quited SDL2')


def main():
    window = SetWindow(title="Test Window", w=800, h=200)
    print('window.title = ', window.title)
    w,h = window.getWindowSize()
    print('w, h = ', w, h)
    dw,dh = window.getDrawableSize()
    print('dw, dh = ', dw, dw)
    sdl2.SDL_Delay(6000) # in milliseconds
    window.destroy()

if __name__ == '__main__':
    main()
