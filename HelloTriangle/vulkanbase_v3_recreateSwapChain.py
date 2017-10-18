#!/bin/env python3

'''
Module to setup vulkan API.

Amended on: 2017-10-17
Amendments: 1. Introduced logic for debugging and associated callback functions.  
'''

# Python3 modules
import logging
import os
import ctypes

from vulkan import *
import vtools as vts
 
__author__ = 'sunbear.c22'
__version__ = '0.1.0'
__license__ = 'MIT'


enableValidationLayers = True


class Setup(object):

    def __init__(self, window, debug=False):
        self.window = window
        self.debug = debug

        if self.debug:
            self.instance_extensions = ['VK_KHR_surface', 'VK_EXT_debug_report']
            self.instance_layers = ['VK_LAYER_LUNARG_standard_validation']
        else:
            self.instance_extensions = ['VK_KHR_surface'] #declares the VkSurfaceKHR object, and provides a function for destroying VkSurfaceKHR objects.
            self.instance_layers = []
            
        self.instance = None
        self.fnp = {}
        self.callback = None
        self.surface = None
        self.physical_device = None
        self.physical_device_features = None
        self.physical_device_properties = None
        self.queue_families_graphics_index = -1
        self.queue_families_present_index = -1
        self.logical_device_extensions = ['VK_KHR_swapchain']
        self.logical_device_layers = self.instance_layers
        self.logical_device = None
        self.graphics_queue = None
        self.present_queue = None
        self.swapchain = None
        self.swapchain_images = None
        self.swapchain_imageViews = []
        self.swapchain_imageExtent = None
        self.swapchain_imageFormat = None
        self.render_pass = None
        self.pipeline_layout = None
        self.graphics_pipeline = None
        self.swapchain_framebuffers = []
        self.command_pool = None
        self.command_buffers = None
        self.semaphore_image_available = None
        self.semaphore_image_drawn = None            
        
        self._createInstance()
        self._getFnp()
        self._setupDebugCallback()
        self._setupSurface()
        self._selectPhysicalDevice()
        self._getGraphicsPresentQueueFamily()
        self._setLogicalDeviceExtensions()
        self._createLogicalDevice()
        self._getGraphicsPresentQueue()
        self._createSwapChain()
        self._createImageviews()
        self._createRenderPass()
        self._createGraphicsPipeline()
        self._createFramebuffers()
        self._createCommandPool()
        self._createCommandBuffer()
        self._createSemaphores()

    def _printlist(self, inputlist, msg):
        print('{0:3} {1}:'.format(len(inputlist), msg))
        for item in inputlist:
            print('{0:3}{1}'.format('', item))


    def _logdebuglist(self, inputlist, msg):
        logging.debug('Detected {0} {1}:'.format(len(inputlist), msg))
        for item in inputlist:
            logging.debug('{0}- {1}'.format(' ', item))
        

    def _setInstanceExtensions(self):
        '''Define required Vulkan Instance Extensions to initialise Vulkan
           Instance.'''

        #1.Get available instance extensions in Vulkan.
        available_extensions = [e.extensionName for e in
                                vkEnumerateInstanceExtensionProperties(None)]
        if self.debug:
            self._logdebuglist(available_extensions, 'available instance extensions')

        #2.Add system's display-server-protocol to required instance extensions
        self.instance_extensions.append(self.window.display_server_protocol)

        #3.Check that required instance extensions are available in Vulkan
        if not all(e in available_extensions for e in self.instance_extensions):
            logging.error('Required instance extensions are not all available in Vulkan')
            exit()
        else:
            logging.info('Set Vulkan Instance Extensions = {0}'.format(self.instance_extensions))


    def _checkInstanceLayers(self):
        '''Define required Vulkan Layer Extensions to initialise Vulkan Instance.'''

        #1.List layer extensions available in Vulkan.
        available_layers = [l.layerName for l in
                            vkEnumerateInstanceLayerProperties()]
        if self.debug:
            self._logdebuglist(available_layers, 'available layers')

        #2.Check that required layer extensions are available in Vulkan.
        if not all(e in available_layers for e in self.instance_layers):
            logging.error('Required Vulkan layers are not all available.')
            return False
            exit()
        else:
            logging.info('All required Vulkan Layer Extensions are available.')
            return True

        
    def _createInstance(self):
        '''Create Vulkan Instance for Vulkan App.'''

        appInfo = VkApplicationInfo(
            sType = VK_STRUCTURE_TYPE_APPLICATION_INFO, #indicates the type of the structure
            pApplicationName = self.window.title,
            applicationVersion = VK_MAKE_VERSION(1, 0, 0),
            pEngineName = self.window.title, 
            engineVersion = VK_MAKE_VERSION(1, 0, 0),
            apiVersion = VK_MAKE_VERSION(1, 0, 0))
        logging.info('Initialised Vulkan Loader/Library')

        self._setInstanceExtensions()
        layersChecked = self._checkInstanceLayers()

        if self.debug and layersChecked:
            createInfo = VkInstanceCreateInfo(
                sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
                flags = 0,
                pApplicationInfo = appInfo,
                enabledLayerCount = len(self.instance_layers),
                ppEnabledLayerNames = self.instance_layers,
                enabledExtensionCount = len(self.instance_extensions),
                ppEnabledExtensionNames = self.instance_extensions )
            logging.info('Created Vulkan Instance Create Info with Layers {}'\
                          .format(self.instance_layers))
        else:
            createInfo = VkInstanceCreateInfo(
                sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
                flags = 0,
                pApplicationInfo = appInfo,
                enabledLayerCount = 0,
                ppEnabledLayerNames = None,
                enabledExtensionCount = len(self.instance_extensions),
                ppEnabledExtensionNames = self.instance_extensions )
            logging.info('Created Vulkan Instance Create Info w/o Layers')
           
        try:
            self.instance = vkCreateInstance(createInfo, None)
            logging.info('Created Vulkan Instance.')
        except VkError:
            logging.error('Vulkan Instance fail to create.')
            exit()


    def _getFnp(self):
        '''Create a dictionary of function pointers (fnp) to unexposed Vulkan \n
           functions that are needed for this class.
           
        Note: A Vulkan instance is need to used this function.
        '''

        def add_Fnp(name, instance):
            '''Function to get function pointer to unexposed Vulkan function'''
            try:
                self.fnp[name] = vkGetInstanceProcAddr(instance, name)
                #logging.info('Created function pointer self.fnp[{0}]'.format(name))
            except ImportError:
                logging.error("Can't get function pointer to {}".format(name))
                exit

        unexposed_functions = [
            'vkDestroySurfaceKHR', #Destroy a VkSurfaceKHR object 
            'vkGetPhysicalDeviceSurfaceSupportKHR', #Determine if a queue family of a physical device supports presentation to a surface object
            'vkGetPhysicalDeviceSurfaceFormatsKHR', #Query the supported swapchain format-color space pairs for a surface (swapchain)
            'vkGetPhysicalDeviceSurfaceCapabilitiesKHR', #Query the basic capabilities of a surface object (swapchain)
            'vkGetPhysicalDeviceSurfacePresentModesKHR', #Query the supported presentation modes for a surface (swapchain)
            'vkCreateSwapchainKHR',
            'vkDestroySwapchainKHR',
            'vkGetSwapchainImagesKHR',
            'vkAcquireNextImageKHR',
            'vkQueuePresentKHR'
            ]
        if self.debug:
            unexposed_functions.extend( [ 'vkCreateDebugReportCallbackEXT',
                                          'vkDestroyDebugReportCallbackEXT' ] )

        logging.info('Created function pointers to unexposed functions:')
        for name in unexposed_functions:
            add_Fnp(name, self.instance)
            logging.info(" - self.fnp['{0}']".format(name))


    def _setupDebugCallback(self):
        '''Enable a Debug Callback system that prints out Vulkan's feedback on 
           when error and warning events occur.'''
        
        # Debug mode off
        if not self.debug:
            return

        # Debug mode on
        createInfo = VkDebugReportCallbackCreateInfoEXT(
            sType = VK_STRUCTURE_TYPE_DEBUG_REPORT_CALLBACK_CREATE_INFO_EXT,
            flags = VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT | VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT | VK_DEBUG_REPORT_INFORMATION_BIT_EXT | VK_DEBUG_REPORT_DEBUG_BIT_EXT,
            #flags = VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT,
            pfnCallback = self._debugCallback )
        
        self.callback = self.fnp['vkCreateDebugReportCallbackEXT'](
            self.instance, createInfo, None)

        if not self.callback:
            raise Exception("failed to set up debug callback!")


    def _debugCallback(*args):
        ''' Printing Debug Callback

        args[0] = flags       VkDebugReportFlagsEXT 
        args[1] = objType     VkDebugReportObjectTypeEXT 
        args[2] = obj         uint64_t 
        args[3] = location    size_t 
        args[4] = code        int32_t 
        args[5] = layerPrefix const char* 
        args[6] = msg         const char* 
        args[7] = userData    void* 
        '''
        #print('DEBUG: {0}  {1}  {2}  {3}  {4}  {5}  {6}  {7}'.format(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]))
        print('  Validation Layer: {0:50}  {1}'.format(
            vts.VkDebugReportObjectTypeEXT[ args[1] ],  args[7] ) )
        return VK_FALSE


    def _setupSurface(self):
        '''Makes the initialised Vulkan surface to be display-platform specific
           (i.e. display-server-protocol specific).'''

        info = self.window.info
        
        #1.Function Pointer to function that will make Vulkan surface to be 
        #  display-server-protocol specific.
        def create_surface(name, surface_createInfo):
            f = vkGetInstanceProcAddr(self.instance, name)
            return f(self.instance, surface_createInfo, None)
        
        #2.Functions to setup the Vulkan surface according to
        #  display-server-protocol.
        def _surface_xlib():
            logging.info('Created Xlib surface function.')
            surface_createInfo = VkXlibSurfaceCreateInfoKHR(
                sType = VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR,
                flags = 0,
                dpy = info.info.x11.display,
                window = info.info.x11.window)
            return create_surface('vkCreateXlibSurfaceKHR', surface_createInfo)

        def _surface_xcb():
            logging.info('Created Xcb surface function')
            surface_createInfo = VkXcbSurfaceCreateInfoKHR(
                sType = VK_STRUCTURE_TYPE_XCB_SURFACE_CREATE_INFO_KHR,
                flags = 0,
                connection = info.info.x11.display,
                window = info.info.x11.window)
            return create_surface('vkCreateXcbSurfaceKHR', surface_createInfo)

        def _surface_wayland():
            logging.info('Created Wayland surface function')
            surface_createInfo = VkWaylandSurfaceCreateInfoKHR(
                sType = VK_STRUCTURE_TYPE_WAYLAND_SURFACE_CREATE_INFO_KHR,
                flags = 0,
                display = info.info.wl.display,
                surface = info.info.surface)
            return create_surface('vkCreateWaylandSurfaceKHR',
                                  surface_createInfo)

        def _surface_mir():
            logging.info('Created Mir surface function')
            surface_createInfo = VkMirSurfaceCreateInfoKHR(
                sType = VK_STRUCTURE_TYPE_MIR_SURFACE_CREATE_INFO_KHR,
                flags = 0,
                connection = info.info.mir.connection,
                mirSurface = info.info.mir.surface)
            return create_surface('vkCreateMirSurfaceKHR', surface_createInfo)

        def _surface_win32():
            logging.info('Created Win32 surface function')
            surface_createInfo = VkWin32SurfaceCreateInfoKHR(
                sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
                flags = 0,
                hinstance = info.win.hinstance,
                hwdn = info.info.win.window)
            return create_surface('vkCreateWin32SurfaceKHR', surface_createInfo)

        #3.Dictionary to map system's display-server-protocol to function to
        #  setup display-server-protocol specific Vulkan surface.
        surface_mapping = { 'VK_KHR_xlib_surface': _surface_xlib,
                            'VK_KHR_xcb_surface': _surface_xcb,
                            'VK_KHR_mir_surface': _surface_mir,
                            'VK_KHR_wayland_surface': _surface_wayland,
                            'VK_KHR_win32_surface': _surface_win32 }

        #4.Setup Vulkan surface based on system's display-server-protocol.
        try:
            self.surface = surface_mapping[self.window.display_server_protocol]()
            logging.info('Created Vulkan Surface for {0} protocol.'.format(
                self.window.display_server_protocol))
        except VkError:
            logging.error('Vulkan Surface fail to create.')
            exit()
        

    def _selectPhysicalDevice(self):
        '''Select physical device, e.g. GPU, CPU or OTHERS, to use.

         Criteria
         1. Larger GPU memory size is better, an indication of a faster GPU.
         2. Discrete GPU is preferred over Integrated GPU as it is typically faster.
         Note: All GPU has a queue family that suuport graphic operation
               (i.e. VkDrawCmd*) so there is not need to search for a physical
               device with VkQueueFlagBits= VK_QUEUE_GRAPHICS_BIT.
         '''

        #1.Enumerate physical devices in system.'
        try:
            physical_devices = vkEnumeratePhysicalDevices(
                instance = self.instance)
            name = [ vkGetPhysicalDeviceProperties(physical_device).deviceName
                       for x, physical_device in enumerate(physical_devices) ]
            logging.info('Detected physical device(s): {}.'.format(name))            
        except VkError:
            logging.error('Physical device(s) detection failed.')
            exit()

        #2.Select physical device based on selection criteria
        physical_devices_features = {
            physical_device : vkGetPhysicalDeviceFeatures(physical_device)
            for physical_device in physical_devices} #Needed by VkDeviceCreateInfo
        physical_devices_properties = {
            physical_device : vkGetPhysicalDeviceProperties(physical_device)
            for physical_device in physical_devices}
        physical_devices_memories = {
            physical_device : vkGetPhysicalDeviceMemoryProperties(physical_device)
                  for physical_device in physical_devices}

        selected_index = 0
        best_score = 0
        for i, physical_device in enumerate(physical_devices):
            score = 0

            #Larger local GPU memory size is faster
            for memoryHeap in physical_devices_memories[physical_device].memoryHeaps:
                heapsize = memoryHeap.size
                heapflag = memoryHeap.flags
                if heapflag & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT and \
                   heapsize >> 0:
                    if self.debug:
                        logging.debug('heapsize MB = {0}'.format(int(heapsize*1.E-6)))
                    score += int(heapsize*1.E-6)

            #Discrete GPU is typically faster
            #logging.debug('properties[{0}].deviceType = {1}'.format(
            #    i, properties[i].deviceType))
            if physical_devices_properties[physical_device].deviceType == \
               VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
                score += 1000
                if self.debug:
                    logging.debug('A VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU')
            logging.info('{0} score = {1}'.format(name[i], score))
            if score > best_score:
                best_score = score
                selected_physical_device = physical_device
                selected_index = i

        #Fastest physical device is not selected.
        if best_score == 0:
            self.physical_device = physical_devices[0]
            self.physical_device_properties = physical_devices_properties[0]
            self.physical_device_features = physical_devices_features[0]
            logging.info('{0} has been selected'.format(name[0]))
        #Fastest physical device is selected.
        else:
            self.physical_device = selected_physical_device
            self.physical_device_properties = physical_devices_properties[
                selected_physical_device]
            self.physical_device_features = physical_devices_features[
                selected_physical_device]
            logging.info('{0} has been selected'.format(name[selected_index]))


    def _getGraphicsPresentQueueFamily(self):
        '''Identify a physical device's queue-family that supports graphics
           operations and supports the present operations.

           Notes:
           1. Graphics operations refer to any VkDrawCmd* commands.
           2. "Present" operation refers to getting one of the swapchain image
              onto the screen (i.e. surface) for viewing.
           3. For a present operation to take place, a Vulkan App needs to put 
              a present request onto one of the GPU's queues, using the
              vkQueuePresentKHR() function. This means the queue referenced by
              this function must be able to support present requests, or
              graphics and present requests. And because the queue is part of a
              queuefamily, and this queuefamily constitutes the logical device,
              this also means that the logical device must be able to support
              present requests, or graphics and present requests. 
           4. In short, as a prelude to making a swapchain and a logical device,
              we need a function to get the index of the queue_families that 
              supports graphics operations and present operations. Hence, this 
              function is created. It needs to be called before logical device
              and swapchain creation, and after physical device is selected.'''

        #1. Get queue families in selected physical_device.
        queue_families = vkGetPhysicalDeviceQueueFamilyProperties(
            self.physical_device)
        logging.info('It has {} queue_families:'.format(len(queue_families)))

        #2. Find which queue in queue_families supports graphics operations and
        #   presentation to surface.')
        for i, queue_family in enumerate(queue_families):
            # Graphics operations check
            if queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT:
                self.queue_families_graphics_index = i
            # Present operations check
            # Returns VK_TRUE to indicate support, and VK_FALSE otherwise.
            support_present = self.fnp['vkGetPhysicalDeviceSurfaceSupportKHR'](
                self.physical_device, i, self.surface)
            if support_present & VK_TRUE:
                    self.queue_families_present_index = i
        logging.info('Queue_families[{}] supports Vulkan graphics '
                     'operations, i.e. VkDrawCmd*.'.format(
                         self.queue_families_graphics_index))
        logging.info('Queue_families[{}] supports presentation to '
                     'Vulkan surface.'.format(self.queue_families_present_index))


    def _setLogicalDeviceExtensions(self):
        '''Define the device extensions to be used to create the Logical Device.

        Notes:
        - This function ensures the device extension(s) (e.g. swapchain extension)
          declared in __init__ is availabe, as the device extension(s) will be use 
          to create the logical device.'''
        
        available_logical_device_extensions = vkEnumerateDeviceExtensionProperties(
            physicalDevice=self.physical_device, pLayerName=None)
        extensionsNames = [e.extensionName for e in
                          available_logical_device_extensions]
        if self.debug:
            self._logdebuglist(extensionsNames, 'available logical device extension')
      
        logging.info('Required {0} logical device extension(s): {1}'.format(
            len(self.logical_device_extensions), self.logical_device_extensions))        

        if not all(e in extensionsNames for e in self.logical_device_extensions):
            logging.error('Required Logical Device Extensions are not all '
                          'detactable.')
            exit()
        else:
            logging.info('Set Logical Device Extension(s) = {0}'.format(
                self.logical_device_extensions))


    def _createLogicalDevice(self):
        '''Create Logical Device'''

        #1. Create Logical Device Queue Create Info.
        queue_priorities = [1.0]
        queue_family_indices = {self.queue_families_graphics_index,
                                self.queue_families_present_index}
        # Note: queue_family_indices is a set; when it's items value are equal,
        #       set keeps only one of them. 
        logical_device_queues_createInfo = [ VkDeviceQueueCreateInfo(
            sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            flags = 0,
            queueFamilyIndex = i,
            queueCount = 1,
            pQueuePriorities = queue_priorities)
                        for i in queue_family_indices ]
        logging.info('Created logical_device_queues_createInfo.')
        
        #2. Create Logical Device Create Info.
        logical_device_createInfo = VkDeviceCreateInfo(
            sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            flags = 0,
            queueCreateInfoCount = len(logical_device_queues_createInfo),
            pQueueCreateInfos = logical_device_queues_createInfo,
            enabledLayerCount = len(self.logical_device_layers), # Note: device_layers == instance_layer
            ppEnabledLayerNames = self.logical_device_layers,    # Note: device_layers == instance_layer
            enabledExtensionCount = len(self.logical_device_extensions), # Note: self.device_extensions != instance_extensions
            ppEnabledExtensionNames = self.logical_device_extensions,    # Note: self.device_extensions != instance_extensions
            pEnabledFeatures = self.physical_device_features )
        logging.info('Created logical_device_createInfo.')
        
        #3. Create logical_device
        try:
            self.logical_device = vkCreateDevice(
                self.physical_device, logical_device_createInfo, None)
            logging.info('Created logical_device.')
        except VkError:
            logging.error('Logical_device fail to create.')
            exit()

    def _getGraphicsPresentQueue(self):
        '''Get the logical device's queue-handle(s) for graphics and present
           operations.

        Notes:
        - A queue-handle is the identity of a queue in a queue-family.
        - A queue-family constitutes the logical device.'''
        
        #1. Get graphics queue-handle 
        self.graphics_queue = vkGetDeviceQueue(
            device = self.logical_device,
            queueFamilyIndex = self.queue_families_graphics_index,
            queueIndex = 0 )
        logging.info('Retrieved graphics_queue handle of logical device.')

        #2. Get present queue-handle.
        self.present_queue = vkGetDeviceQueue(
            device = self.logical_device,
            queueFamilyIndex = self.queue_families_present_index,
            queueIndex = 0 )
        logging.info('Retrieved present_queue handle of logical device.')


    def _createSwapChain(self):
        '''Create Swapchain object

           - the general purpose of the swapchain is to synchronize the\n
             presentation of images with the refresh rate of the screen.\n

           - the swapchain is a list of image buffers that the GPU draws into\n
             and also uses to present the drawn image to the screen.\n

           - to use the swapchain, we need to ensure the Vulkan swapchain \n
             device extension 'VK_KHR_swapchain' is available as we have to use\n
             it. Function _setLogicalDeviceExtensions() does this.\n

           - next, we have to update the VkSwapchainCreateInfoKHR struture with\n
             appropriate swapchain parameter values.

           - To get the best possible swapchain, the following settings have
             been recommended in
             https://vulkan-tutorial.com/Drawing_a_triangle/Presentation/Swap_chain
             and
             https://vulkan.lunarg.com/doc/sdk/1.0.61.1/linux/tutorial/html/05-init_swapchain.html:

             Surface Capabilities settings:
             - minImageCount, extent, preTransform, compositeAlpha

             Format settings:
             1. format.format and colorSpace values
             
             Present mode setting:
             1. The preferred order to set the swapchain present mode is
                VK_PRESENT_MODE_IMMEDIATE_KHR
                VK_PRESENT_MODE_MAILBOX_KHR
                VK_PRESENT_MODE_FIFO_KHR
                VK_PRESENT_MODE_FIFO_RELAXED_KHR
        '''
        
        #### SETTING ASSOCIATED TO SURFACE CAPABILITES #### 
        # Swapchain will use a Double Buffer configuration to draw and present 
        # images, i.e. acquire a buffer to draw an image, while another buffer
        # holding a drawn image is used to present the drawn image to the 
        # surface. As such, swapchain's imagecount must equal the minImageCount,
        # which has a value of 2.
        surface_capabilities = self.fnp[
            'vkGetPhysicalDeviceSurfaceCapabilitiesKHR'](
                physicalDevice=self.physical_device, surface=self.surface)

        #C1. Set swapchain's ImageCount.
        # Swapchain will use a Double Buffer configuration to draw and present 
        # images, i.e. acquire a buffer to draw an image, while another buffer
        # having a drawn image is used to present the drawn image to the 
        # surface. As such, swapchain's imagecount is equal to the surface
        # capabilities minImageCount, which has a value of 2.
        if self.debug:
            capabilitiesName = [x for x in vts.convert_to_python(surface_capabilities)]
            logging.debug('Surface capabilities are:')
            for x in capabilitiesName:
                y = getattr(surface_capabilities,x)
                logging.debug(' - {0:23} = {1} '.format(x,y))
        sc_minImageCount = surface_capabilities.minImageCount
        logging.info('Swapchain will use Double Buffer Configuration.') 
        logging.info('Set swapchain minImageCount = {}'.format(
            sc_minImageCount))

        #C2. Set swapchain's extent, i.e. size (in pixel).
        # The swap extent is the resolution of the swapchain images. If the 
        # display-server protocol allows the swap extent to differ from the
        # surface extent, then we pick the resolution that best matches the 
        # surface, i.e. within the surface minImageExtent and maxImageExtent 
        # bounds. If not, the swap extent must be exactly similar to the
        # surface current extent; this scenario is most common. The criterion
        # for the former is indicated by setting the width and height in
        # currentExtent to a special value: the maximum value of uint32_t,
        # i.e. UINT32_MAX.
        if self.debug:
            capabilitiesName2 = ['currentExtent','minImageExtent','maxImageExtent']
            parts = ['width', 'height']
            logging.debug('Surface extent capabilities:')
            for x in capabilitiesName2:
                y = getattr(surface_capabilities,x)
                for z in parts:
                    logging.debug(' - {0}.{1} = {2} '.format(x,z,getattr(y,z)))

        uint32_max = 0xFFFFFFFF
        if surface_capabilities.currentExtent.width != uint32_max:
            logging.info('Swapchain size must exactly match the surface size.')
            #sc_imageExtent = surface_capabilities.currentExtent # wrong Vulkan syntax used
            sc_imageExtent = VkExtent2D(
                width = surface_capabilities.currentExtent.width,
                height = surface_capabilities.currentExtent.height)

        else:

            #added: To get up-to-date window size during window resizing.
            w,h = self.window.getWindowSize()
            actual_extent = VkExtent2D( width = w, height = h)

            logging.info('Swapchain size does not need to match surface size.')
            sc_imageExtent.width = max(
                surface_capabilities.minImageExtent.width,
                min( surface_capabilities.maxImageExtent.width,
                     actual_extent.width ) ) #changed to actual extent
            sc_imageExtent.height = max(
                surface_capabilities.minImageExtent.height,
                min( surface_capabilities.maxImageExtent.height,
                     actual_extent.height ) ) #changed to actual extent
        logging.info('Picked surface extent.width = {}'.format(sc_imageExtent.width))
        logging.info('Picked surface extent.height = {}'.format(sc_imageExtent.height))

        #C3 Set swapchain's preTransform.
        if self.debug:
            logging.debug('preTransform VkSurfaceTransformFlagBitsKHR values and meaning.')
            logging.debug('0x00000002 = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR')
            logging.debug('0x00000002 = VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR')
            logging.debug('0x00000004 = VK_SURFACE_TRANSFORM_ROTATE_180_BIT_KHR')
            logging.debug('0x00000008 = VK_SURFACE_TRANSFORM_ROTATE_270_BIT_KHR')
            logging.debug('0x00000010 = VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_BIT_KHR')
            logging.debug('0x00000020 = VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_90_BIT_KHR')
            logging.debug('0x00000040 = VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_180_BIT_KHR')
            logging.debug('0x00000080 = VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_270_BIT_KHR')
            logging.debug('0x00000100 = VK_SURFACE_TRANSFORM_INHERIT_BIT_KHR')

        if surface_capabilities.supportedTransforms & \
           VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR:
            sc_preTransform = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR
        else:
            sc_preTransform = surface_capabilities.currentTransform
        logging.info('Set swapchain preTransform = {}'.format(sc_preTransform))

        #C4. Set swapchain's compositeAlpha.
        # Find a supported composite alpha mode - one of these is guaranteed to be set
        if self.debug:
            logging.debug('CompositeAlpha VkCompositeAlphaFlagBitsKHR values and meaning.')
            logging.debug(' - 0x00000001 = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR')
            logging.debug(' - 0x00000002 = VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR')
            logging.debug(' - 0x00000004 = VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR')
            logging.debug(' - 0x00000008 = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR')

        sc_compositeAlpha = surface_capabilities.supportedCompositeAlpha
        logging.info('surface CompositeAlpha = {}'.format(
            surface_capabilities.supportedCompositeAlpha) )
        logging.info('Set swapchain CompositeAlpha to match surface = {}'.format(
            sc_compositeAlpha))

        #### SETTING ASSOCIATED TO FORMAT SETTINGS #### 
        # Set swapchain image format to match surface format (or at least be
        # compatible). This is done by first getting the surface format,
        # followed by checking them and then using them as the swapchain's
        # image format.
        # 
        # Notes:
        # 1. surface_format is a VkSurfaceFormatKHR structure with 2 parameters: 
        #    - format:- is a enum VkFormat that tells the how RGBA are store in
        #               bytes nd bits.
        #             - Spec has listed its values with associated meaning in
        #               https://www.khronos.org/registry/vulkan/specs/1.0-extensions/html/vkspec.html#VkFormat
        #             - if it has a value of VK_FORMAT_UNDEFINED (i.e. 0), this 
        #               means a surface has no preferred format. In 
        #               this case, we can use any VkFormat and VkColorSpaceKHR
        #               value combinations valid for the surface. Here, combination
        #               VK_FORMAT_B8G8R8A8_UNORM and VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
        #               are used.   
        #             - if not, we either use either the same combination if it is
        #               available or the 1st combination of the surface. 
        #    - colorSpace:- is a enum VkColorSpaceKHR specifying supported color
        #                   spaces of a presentation engine.
        # 2. The size of surface_formats represents literally how many different
        #    format/colorspace pairs that can be used for the surface.
        def _pickSurfaceFormat(formats):
            '''Algorithm to set swapchain's surface format's format and colorSpace values '''
            
            if len(formats)==1 and formats[0].format==VK_FORMAT_UNDEFINED:
                logging.info('Surface format is undefined.')
                logging.info(' Set SwapchainImageFormat.format = VK_FORMAT_B8G8R8A8_UNORM')
                logging.info(' Set SwapchainImageFormat.colorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR')
                return VkSurfaceFormatKHR(VK_FORMAT_B8G8R8A8_UNORM, 0)

            for f in formats:
                if f.format == VK_FORMAT_B8G8R8A8_UNORM and \
                   f.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR:
                    logging.info('Surface format is defined. Use available format combination')
                    return f

            logging.info('Use 1st detected surface format combination.')
            return formats[0] # Last scenario: settle with using first surface format  
        
        #Get surface's formats.
        surface_formats = self.fnp['vkGetPhysicalDeviceSurfaceFormatsKHR'](
            physicalDevice = self.physical_device, surface = self.surface )

        if self.debug:
            logging.debug('Detected {} surface format combinations:'.format(
                len(surface_formats)))
            for f in surface_formats:
                for x in vts.convert_to_python(surface_formats):
                    logging.debug(' .{0} = {1}'.format(x,getattr(f,x)))
            logging.debug('VkColorSpaceKHR values and captions:')
            logging.debug('         0 = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR')
            logging.debug('1000104001 = VK_COLOR_SPACE_DISPLAY_P3_NONLINEAR_EXT')
            logging.debug('1000104002 = VK_COLOR_SPACE_EXTENDED_SRGB_LINEAR_EXT')
            logging.debug('1000104003 = VK_COLOR_SPACE_DCI_P3_LINEAR_EXT')
            logging.debug('1000104004 = VK_COLOR_SPACE_DCI_P3_NONLINEAR_EXT') 
            logging.debug('1000104005 = VK_COLOR_SPACE_BT709_LINEAR_EXT')  
            logging.debug('1000104006 = VK_COLOR_SPACE_BT709_NONLINEAR_EXT')
            logging.debug('1000104007 = VK_COLOR_SPACE_BT2020_LINEAR_EXT')
            logging.debug('1000104008 = VK_COLOR_SPACE_HDR10_ST2084_EXT')
            logging.debug('1000104009 = VK_COLOR_SPACE_DOLBYVISION_EXT')
            logging.debug('1000104010 = VK_COLOR_SPACE_HDR10_HLG_EXT')
            logging.debug('1000104011 = VK_COLOR_SPACE_ADOBERGB_LINEAR_EXT')
            logging.debug('1000104012 = VK_COLOR_SPACE_ADOBERGB_NONLINEAR_EXT')
            logging.debug('1000104013 = VK_COLOR_SPACE_PASS_THROUGH_EXT')
            logging.debug('1000104014 = VK_COLOR_SPACE_EXTENDED_SRGB_NONLINEAR_EXT')

        #Set swapchain image_formats.
        try:
            surfaceFormat = _pickSurfaceFormat(surface_formats)
            logging.info('Picked surfaceFormat:')
            logging.info('       surfaceFormat.format: {}'.format(
                surfaceFormat.format))
            logging.info('       surfaceFormat.colorSpace: {}'.format(
                surfaceFormat.colorSpace))
        except:
            logging.error('Swapchain image_format faill to set')
            exit()
            
        #### SETTING ASSOCIATED TO PRESENT MODE #### 
        # The preferred order to set the swapchain present mode is
        # - VK_PRESENT_MODE_IMMEDIATE_KHR
        # - VK_PRESENT_MODE_MAILBOX_KHR
        # - VK_PRESENT_MODE_FIFO_KHR
        # - VK_PRESENT_MODE_FIFO_RELAXED_KHR
        surface_presentModes = self.fnp[
            'vkGetPhysicalDeviceSurfacePresentModesKHR'](
            physicalDevice=self.physical_device, surface=self.surface)

        if self.debug:
            self._logdebuglist(surface_presentModes, 'Surface presentModes')
            logging.debug('VkPresentModeKHR values and captions:')
            logging.debug('  0 = VK_PRESENT_MODE_IMMEDIATE_KHR')
            logging.debug('  1 = VK_PRESENT_MODE_MAILBOX_KHR')
            logging.debug('  2 = VK_PRESENT_MODE_FIFO_KHR  (This mode is guaranteed'\
                          ' to be available)')
            logging.debug('  3 = VK_PRESENT_MODE_FIFO_RELAXED_KHR')
            logging.debug('Detected {} swapchain present_modes'.format(
                len(surface_presentModes)))

        def _get_surface_present_mode(availablePresentModes):
            '''Logic to set present mode'''
            bestMode = VK_PRESENT_MODE_FIFO_KHR
            for p in availablePresentModes:
                if p == VK_PRESENT_MODE_MAILBOX_KHR:
                    return p
                elif p == VK_PRESENT_MODE_IMMEDIATE_KHR:
                    bestMode = p
            # The FIFO present mode is guaranteed by VULKAN spec to be supported
            return bestMode;

        sc_presentMode = _get_surface_present_mode(surface_presentModes)
        logging.info('Set swapchain presentMode = {}'.format(sc_presentMode))


        ### OTHERS ###

        #O1. Set the swapchain ImageSharingMode, QueueFamilyIndexCount and
        #     pQueueFamilyIndices
        # Notes:
        # 1. For logical devices where the graphics queue family and the
        #    presentation queue are one in the same, VK_SHARING_MODE_EXCLUSIVE
        #    should be used. It specifies that access to any range or image
        #    subresource of the object will be exclusive to a single queue 
        #    family at a time.
        # 2. If the graphics queue family and the presentation queue family
        #    are different, the VK_SHARING_MODE_CONCURRENT should be used.
        #    It specifies that concurrent access to any range or image 
        #    subresource of the object from multiple queue families is supported.
        
        sc_imageSharingMode = VK_SHARING_MODE_EXCLUSIVE
        sc_queueFamilyIndexCount = 0
        sc_pQueueFamilyIndices = None

        if self.queue_families_graphics_index != self.queue_families_present_index:
            sc_imageSharingMode = VK_SHARING_MODE_CONCURRENT
            sc_queueFamilyIndexCount = 2
            sc_pQueueFamilyIndices = [queue_family_graphics_index,
                                                  queue_family_present_index]
        logging.info('Set swapchain ImageSharingMode = {}'.format(
            sc_imageSharingMode))
        logging.info('Set swapchain QueueFamilyIndexCount = {}'.format(
            sc_queueFamilyIndexCount))
        logging.info('Set swapchain QueueFamilyIndices = {}'.format(
            sc_pQueueFamilyIndices))


        ### CREATE SWAPCHAIN ###

        #1. Create VkSwapchainCreateInfoKHR.
        createInfo = VkSwapchainCreateInfoKHR (
            sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            pNext = None,
            flags = 0,
            surface = self.surface,
            # is the surface that the swapchain will present images to.
            minImageCount = sc_minImageCount,
            # min. no. of presentable images the application needs
            #imageFormat = self.swapchain_imageFormat.format,
            imageFormat = surfaceFormat.format,
            # is a VkFormat that is valid for swapchains on the specified surface.
            #imageColorSpace = self.swapchain_imageFormat.colorSpace,
            imageColorSpace = surfaceFormat.colorSpace,
            # is a VkColorSpaceKHR that is valid for swapchains on the specified surface.
            imageExtent = sc_imageExtent,
            # is the size (in pixels) of the swapchain.
            imageArrayLayers = 1,
            # is number of views in a multiview/stereo surface. For non-stereoscopic-3D
            # applications, this value is 1.
            imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            # is a bitmask of VkImageUsageFlagBits, indicating how the application will
            # use the swapchain’s presentable images.
            imageSharingMode = sc_imageSharingMode,
            # is the sharing mode used for the images of the swapchain
            queueFamilyIndexCount = sc_queueFamilyIndexCount,
            # is the number of queue families having access to the images of the
            # swapchain in case imageSharingMode is VK_SHARING_MODE_CONCURRENT.
            pQueueFamilyIndices = sc_pQueueFamilyIndices,
            # is an array of queue family indices having access to the images of the
            # swapchain in case imageSharingMode is VK_SHARING_MODE_CONCURRENT.
            preTransform = sc_preTransform,
            # is a bitmask of VkSurfaceTransformFlagBitsKHR, describing the transform,
            # relative to the presentation engine’s natural orientation, applied to the
            # image content prior to presentation. If it does not match the
            # currentTransform value returned by
            # vkGetPhysicalDeviceSurfaceCapabilitiesKHR, the presentation engine will
            # transform the image content as part of the presentation operation.
            compositeAlpha = sc_compositeAlpha,
            # is a bitmask of VkCompositeAlphaFlagBitsKHR, indicating the alpha
            # compositing mode to use when this surface is composited together with
            # other surfaces on certain window systems.
            presentMode = sc_presentMode,
            # is the presentation mode the swapchain will use. A swapchain’s present
            # mode determines how incoming present requests will be processed and
            # queued internally.
            clipped = VK_TRUE,
            # indicates whether the Vulkan implementation is allowed to discard
            # rendering operations that affect regions of the surface which are not
            # visible.
            oldSwapchain = self.swapchain
            # if not VK_NULL_HANDLE, specifies the swapchain that will be replaced by
            # the new swapchain being created.
            )

        #2. Create Swapchain.
        try:
            self.swapchain = self.fnp['vkCreateSwapchainKHR'](
                self.logical_device, createInfo, None)
            logging.info('Created Swapchain.')
        except VkError:
            logging.error('Swapchain failed to create')

        #3. Get Swapchain Images, i.e. an array of presentable images in swapchain.
        self.swapchain_images = self.fnp['vkGetSwapchainImagesKHR'](
            self.logical_device, self.swapchain)
        logging.info('Gotten swapchain images.')

        self.swapchain_imageFormat = surfaceFormat.format
        self.swapchain_imageExtent = sc_imageExtent
        logging.info('set swapchain imageFormat: {}'.format(self.swapchain_imageFormat))
        logging.info('Set swapchain extent.width = {}'.format(self.swapchain_imageExtent.width))
        logging.info('Set swapchain extent.height = {}'.format(self.swapchain_imageExtent.height))


    def _createImageviews(self):
        ''' Get Swapchain Images and Imageviews. '''
        
        # Notes:
        #  - A "view" is essentially additional information attached to a
        #    resource that describes how that resource is used.
        #  - An view of an image i.e. "Imageview" is essentially the additional
        #    information on how to create/see the swapchain image, e.g.
        #    - how to access the image,
        #    - which part of the image to access,
        #    - if it should be treated as a 2D texture depth texture without any
        #      mipmapping levels
        #  - Here, the view used is suited for 2D framebuffering.

        # Component specifies a remapping of color components (or of depth or 
        # stencil components after they have been converted into color 
        # components). Allows us to swizzle the color channels around if need. 
        # To use the default color mapping, use VK_COMPONENT_SWIZZLE_IDENTITY.
        swapchain_image_components = VkComponentMapping(
            r = VK_COMPONENT_SWIZZLE_IDENTITY,
            g = VK_COMPONENT_SWIZZLE_IDENTITY,
            b = VK_COMPONENT_SWIZZLE_IDENTITY,
            a = VK_COMPONENT_SWIZZLE_IDENTITY
            )
        logging.info('Set swapchain_image_components.')

        # subresourceRange describes what the image's purpose is and which part
        # of the image should be accessed. Our images will be used as color
        # targets without any mipmapping levels or multiple layers.
        swapchain_image_subresourceRange = VkImageSubresourceRange(
            aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
            baseMipLevel = 0,
            levelCount = 1,
            baseArrayLayer = 0,
            layerCount = 1
            )
        logging.info('Set swapchain_image_subresourceRange.')

        #2. Create a view of each swapchain image and store in an array.
        try:
            for i, image in enumerate(self.swapchain_images):

                # Create swapchain imageview createInfo
                createInfo = VkImageViewCreateInfo(
                    sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                    pNext = None,
                    flags = 0,
                    image = image,
                    # the current VkImage on which the view will be created.
                    viewType = VK_IMAGE_VIEW_TYPE_2D,
                    #treat images as 1D, 2D or 3D textures or cube maps.
                    format = self.swapchain_imageFormat,
                    components = swapchain_image_components,
                    subresourceRange = swapchain_image_subresourceRange
                    )
                logging.info('Created swapchain image {} view createinfo.'.format(i))

                # Create swapchain imageviews
                self.swapchain_imageViews.append(
                    vkCreateImageView( self.logical_device, createInfo, None))
                logging.info('Created Swapchain Image View [{}].'.format(i))

            logging.info('- The image views are now only sufficient to be used ')
            logging.info("  as textures. To make them as render targets, we need")
            logging.info("  to first set up the graphics pipeline and framebuffer.") 

        except VkError:
            logging.error('Swapchain imageview(s) failed to create.')
                

    def _createRenderPass(self):
        ''' Create Render Pass.

        Notes:
        1. Render pass represents a collection of attachments, subpasses, and\n'
           dependencies between the subpasses, and describes how the attachments\n
           are used over the course of the subpasses.'''

        #1. Describe attachment description
        #   - Describes the properties of an attachment including its format,
        #     sample count, and how its contents are treated at the beginning and
        #     end of each render pass instance.
        color_attachement = VkAttachmentDescription(
            flags = 0,
            format = self.swapchain_imageFormat,
            # format match swapchain images format
            samples = VK_SAMPLE_COUNT_1_BIT,
            # no multisampling
            loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
            # clear framebuffer to black before draw new frame
            storeOp = VK_ATTACHMENT_STORE_OP_STORE,
            # store operation so that we can see the rendered triangle on the screen
            stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            # means don't care    
            stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
            # means don't care
            initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
            # means don't care what previous layout the image was in
            finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)
            # present to swapchain after rendering
        logging.info('Created render pass color_attachement')

        #2. Describe attachment reference.
        #   - use one subpass to create color buffer.
        color_attachement_reference = VkAttachmentReference(
            attachment=0,
            # 0 means reference 1st index of attachment description array.
            layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL)
            # is a VkImageLayout value specifying the layout the attachment uses during
            # the subpass.
        logging.info('Created render pass color attachement reference.')

        #3. Describe subpass.
        subpass = VkSubpassDescription(
            flags = 0,
            pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
            # explicitly declare this is a graphic pipeline
            inputAttachmentCount = 0,
            pInputAttachments = None,
            pResolveAttachments = None,
            pDepthStencilAttachment = None,
            preserveAttachmentCount = 0,
            pPreserveAttachments = None,
            colorAttachmentCount = 1,
            pColorAttachments=[color_attachement_reference])
        logging.info('Created render pass subpass.')

        #4. Describe subpass dependency.
        # Subpasses in a render pass automatically take care of image layout
        # transitions. These transitions are controlled by subpass dependencies, which
        # specify memory and execution dependencies between subpasses. We have only a
        # single subpass right now, but the operations right before and right after this
        # subpass also count as implicit "subpasses".
        # There are two built-in dependencies that take care of the transition at the
        # start of the render pass and at the end of the render pass, but the former
        # does not occur at the right time. It assumes that the transition occurs at the
        # start of the pipeline, but we haven't acquired the image yet at that point!
        # There are two ways to deal with this problem. We could change the waitStages
        # for the imageAvailableSemaphore to VK_PIPELINE_STAGE_TOP_OF_PIPELINE_BIT to
        # ensure that the render passes don't begin until the image is available, or we
        # can make the render pass wait for the
        # VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT stage. I've decided to go with
        # the second option here, because it's a good excuse to have a look at subpass
        # dependencies and how they work.
        subpass_dependency = VkSubpassDependency(
            srcSubpass = VK_SUBPASS_EXTERNAL,
            dstSubpass = 0,
            # above two fields specify the indices of the dependency and the dependent
            # subpass. The special value VK_SUBPASS_EXTERNAL refers to the implicit
            # subpass before or after the render pass depending on whether it is
            # specified in srcSubpass or dstSubpass. The index 0 refers to our subpass,
            # which is the first and only one. The dstSubpass must always be higher
            # than srcSubpass to prevent cycles in the dependency graph.
            srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            srcAccessMask = 0,
            # above two fields specify the operations to wait on and the stages in which
            # these operations occur. We need to wait for the swap chain to finish
            # reading from the image before we can access it. This can be accomplished
            # by waiting on the color attachment output stage itself.  
            dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
            # The operations that should wait on this are in the color attachment stage
            # and involve the reading and writing of the color attachment. These
            # settings will prevent the transition from happening until it's actually
            # necessary (and allowed): when we want to start writing colors to it.
            dependencyFlags = 0)
        logging.info('Created render pass subpass dependency.')

        #5. Create render pass createinfo.')
        render_pass_createInfo = VkRenderPassCreateInfo(
            flags=0,
            sType=VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount=1,
            pAttachments=[color_attachement],
            subpassCount=1,
            pSubpasses=[subpass],
            dependencyCount=1,
            pDependencies=[subpass_dependency])
        logging.info('Created render pass createInfo.')

        #6. Create render pass.
        try:
            self.render_pass = vkCreateRenderPass(self.logical_device,
                                                  render_pass_createInfo, None)
            logging.info('Created render pass.')
        except VkError:
            logging.error('Render pass failed to create.')


    def _ShaderModuleCreateInfo(self, shader, shadertype):
        shader_module_createInfo = VkShaderModuleCreateInfo(
            sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            flags = 0,
            codeSize = len(shader),
            pCode = shader)
        logging.info('Created {} shader module create info.'.format(shadertype))
        return shader_module_createInfo


    def _createGraphicsPipeline(self):
        ''' Method to load the Spir-V vertex and fragment shaders, create the 
        shader modules and create the shader stages.

        Notes:
        - For this method to work, the vertex and fragment shaders need to be
          created first.
        - Variable name within this function can be kept local, except
          pipeline_shader_stage array/list.
        '''
       
        #1. Create the vertex and fragment shaders as described in:
        #   https://vulkan-tutorial.com/Drawing_a_triangle/Graphics_pipeline_basics/Shader_modules')

        #2. Load the Spir-V Vertex and Fragment Shaders.
        path = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(path, "vert.spv"), 'rb') as f:
            vert_shader_spirv = f.read()
        with open(os.path.join(path, "frag.spv"), 'rb' ) as f:
            frag_shader_spirv = f.read()

        #3. CreateInfo on Vertex and Fragment Shader Modules.
        ''' These modules are simply wrappers around the Spir-V bytecode buffers.'''
        vert_shader_module = self._ShaderModuleCreateInfo(vert_shader_spirv,
                                                          'vertex')
        frag_shader_module = self._ShaderModuleCreateInfo(frag_shader_spirv,
                                                          'fragment')

        try:
            vert_shader_module = vkCreateShaderModule(self.logical_device,
                                                      vert_shader_module, None)
            logging.info('Created vertex shader module.')
            frag_shader_module = vkCreateShaderModule(self.logical_device,
                                                      frag_shader_module, None)
            logging.info('Created fragment shader module.')
        except VkError:
            logging.error('Vertex and/or Fragment Shader Modules fail to create.')

        #4. Create the info to create the Vertex and Fragment shader stages.
        vert_shader_stage = VkPipelineShaderStageCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            pNext = None,
            flags = 0,
            stage = VK_SHADER_STAGE_VERTEX_BIT,
            module = vert_shader_module,
            pName = 'main',
            pSpecializationInfo = None)
        logging.info('Created pipeline vertex shader stage create info.')

        frag_shader_stage = VkPipelineShaderStageCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            pNext = None,
            flags = 0,
            stage = VK_SHADER_STAGE_FRAGMENT_BIT,
            module = frag_shader_module,
            pName = 'main',
            pSpecializationInfo = None)
        logging.info('Created pipeline fragment shader stage create info.')

        pipeline_shader_stages = [vert_shader_stage,frag_shader_stage]


        # SETUP FIXED FUNCTIONS IN GRAPHICS PIPELINE .

        #5. Describes the format of the vertex data that will be passed to the
        #   vertex shader. Because we are hard coding the vertex data directly
        #   in the vertex shader, we have no vertex data to load so parameters
        #   with "Count" has zero value.
        vertex_input = VkPipelineVertexInputStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
            flags = 0,
            vertexBindingDescriptionCount = 0,
            pVertexBindingDescriptions = None, # optional
            vertexAttributeDescriptionCount = 0,
            pVertexAttributeDescriptions = None) # optional

        #6. Describe what kind of geometry will be drawn from the vertices and
        #   if primitive restart should be enabled.
        input_assembly = VkPipelineInputAssemblyStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
            flags = 0,
            topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable = VK_FALSE)

        #7. - A viewport describes the region of the framebuffer that the output
        #     will be rendered to. Here, the viewport size equals swapchain image
        #     extent size.
        #   - A scissor rectangle definse in which regions pixels will actually 
        #     be stored. Any pixels outside the scissor rectangles will be 
        #     discarded by the rasterizer. They function like a filter.
        #   - Using multiple requires enabling a GPU feature in logical device.
        viewport = VkViewport(
            x = 0.,
            y = 0.,
            width = float(self.swapchain_imageExtent.width),
            height = float(self.swapchain_imageExtent.height),
            minDepth = 0.,
            maxDepth = 1.)
        
        scissor_offset = VkOffset2D(x=0, y=0)
        scissor = VkRect2D( offset = scissor_offset,
                            extent = self.swapchain_imageExtent )

        viewport_state = VkPipelineViewportStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
            flags = 0,
            viewportCount = 1,
            pViewports = [viewport],
            scissorCount = 1,
            pScissors=[scissor] )

        #8. - The rasterizer takes the geometry that is shaped by the vertices
        #     from the vertex shader and turns it into fragments to be colored by
        #     the fragment shader. It also performs depth testing, face culling
        #     and the scissor test, and it can be configured to output fragments
        #     that fill entire polygons or just the edges (wireframe rendering).
        rasterizer = VkPipelineRasterizationStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
            flags = 0,
            depthClampEnable = VK_FALSE,
            rasterizerDiscardEnable = VK_FALSE,
            polygonMode = VK_POLYGON_MODE_FILL,
            lineWidth = 1.0,
            cullMode = VK_CULL_MODE_BACK_BIT,
            frontFace = VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable = VK_FALSE,
            depthBiasConstantFactor = 0.,
            depthBiasClamp = 0.,
            depthBiasSlopeFactor = 0.)

        #9. Multisampling is one of the ways to perform anti-aliasing. It works
        #   by combining the fragment shader results of multiple polygons that
        #   rasterize to the same pixel. This mainly occurs along edges, which
        #   is also where the most noticeable aliasing artifacts occur. Because
        #   it doesn't need to run the fragment shader multiple times if only
        #   one polygon maps to a pixel, it is significantly less expensive than
        #   simply rendering to a higher resolution and then downscaling.
        #   Enabling it requires enabling a GPU feature. Not used here.
        multisample = VkPipelineMultisampleStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
            flags = 0,
            sampleShadingEnable = VK_FALSE,
            rasterizationSamples = VK_SAMPLE_COUNT_1_BIT,
            minSampleShading = 1,
            pSampleMask = None,
            alphaToCoverageEnable = VK_FALSE,
            alphaToOneEnable = VK_FALSE)

        #10. Colorblending
        #    - After a fragment shader has returned a color, it needs to be
        #      combined with the color that is already in the framebuffer. This
        #      transformation is known as color blending and there are two ways
        #      to do it:
        #       1. Mix the old and new value to produce a final color
        #       2. Combine the old and new value using a bitwise operation
        #    - There are two types of structs to configure color blending.
        #      1. VkPipelineColorBlendAttachmentState contains the configuration
        #         per attached framebuffer.
        #      2. VkPipelineColorBlendStateCreateInfo contains the global color
        #         blending settings.
        #    - In our case we only have one framebuffer:
        color_blend_attachement = VkPipelineColorBlendAttachmentState(
            colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT,
            blendEnable = VK_FALSE,
            srcColorBlendFactor = VK_BLEND_FACTOR_ONE,
            dstColorBlendFactor = VK_BLEND_FACTOR_ZERO,
            colorBlendOp = VK_BLEND_OP_ADD,
            srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE,
            dstAlphaBlendFactor = VK_BLEND_FACTOR_ZERO,
            alphaBlendOp = VK_BLEND_OP_ADD)

        color_blend = VkPipelineColorBlendStateCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
            flags = 0,
            logicOpEnable = VK_FALSE,
            logicOp = VK_LOGIC_OP_COPY,
            attachmentCount = 1,
            pAttachments = [color_blend_attachement],
            blendConstants = [0, 0, 0, 0])

        #11. Dynamic states
        #    - to dynamically change the size of the viewport, line width and blend
        #      constants w/o having to create a new pipelines
        #    - use VkPipelineDynamicStateCreateInfo, or
        #    - use VkPushConstantRange
        push_constant_ranges = VkPushConstantRange(
            stageFlags = 0,
            offset = 0,
            size = 0)

        #12. Create Pipeline Layout Create Info
        pipeline_layout_createInfo = VkPipelineLayoutCreateInfo(
            sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            flags = 0,
            setLayoutCount = 0,
            pSetLayouts = None,
            pushConstantRangeCount = 0,
            pPushConstantRanges = [push_constant_ranges])

        #13. Create Pipeline Layout
        try:
            self.pipeline_layout = vkCreatePipelineLayout(
                self.logical_device, pipeline_layout_createInfo, None)
            logging.info('Created pipeline layout.')
        except VkError:
            logging.error('Pipeline Layout failed to create.')

        #14. Create Pipeline CreateInfo
        pipeline_createInfo = VkGraphicsPipelineCreateInfo(
            sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
            flags = 0,
            stageCount = 2,
            pStages = pipeline_shader_stages,
            pVertexInputState = vertex_input,
            pInputAssemblyState = input_assembly,
            pTessellationState = None,
            pViewportState = viewport_state,
            pRasterizationState = rasterizer,
            pMultisampleState = multisample,
            pDepthStencilState = None,
            pColorBlendState = color_blend,
            pDynamicState = None,
            layout = self.pipeline_layout,
            renderPass = self.render_pass,
            subpass = 0,
            basePipelineHandle = None,
            basePipelineIndex = -1)

        #15. Create Graphics Pipeline
        try:
            self.graphics_pipeline = vkCreateGraphicsPipelines(
                self.logical_device, None, 1, [pipeline_createInfo], None)
            logging.info('Created graphics pipeline.')
        except VkError:
                logging.error('Graphics pipeline failed to create.')
                exit()
                    
        #16. Destroy Vertex and Fragment Shader Modules.
        vkDestroyShaderModule(self.logical_device, frag_shader_module, None)
        logging.info('Destroyed Vulkan Fragment Shader Module.')
        vkDestroyShaderModule(self.logical_device, vert_shader_module, None)
        logging.info('Destroyed Vulkan Vertex Shader Module.')


    def _createFramebuffers (self):
        '''Create framebuffers.

        Notes:
        - Create a framebuffer array
        - Bind each element of swapchain_imageviews array to a framebuffer
          array element.'''
        try:
            for imageview in self.swapchain_imageViews:
                attachments = [imageview] 

                createInfo = VkFramebufferCreateInfo(
                    sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                    flags = 0,
                    renderPass = self.render_pass,
                    attachmentCount = len(attachments),
                    pAttachments = attachments,
                    width = self.swapchain_imageExtent.width,
                    height = self.swapchain_imageExtent.height,
                    layers=1)

                self.swapchain_framebuffers.append(
                    vkCreateFramebuffer(self.logical_device, createInfo, None))
            logging.info('Created {} swapchain framebuffers.'.format(
                len(self.swapchain_framebuffers)))

        except VkError:
                logging.error('Swapchain framebuffers failed to create.')
                exit()


    def _createCommandPool(self):
        ''' Create Vulkan Command Pool. '''
        
        #- We will only record the command pool at the beginning of the
        #  program and then execute them many times in the main loop, so no
        #  flags has to be declared.
        createInfo = VkCommandPoolCreateInfo(
            sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            flags = 0, # Optional
            queueFamilyIndex = self.queue_families_graphics_index)

        try: 
            self.command_pool = vkCreateCommandPool(
                device = self.logical_device,
                pCreateInfo = createInfo,
                pAllocator = None)
            logging.info('Created command pool.')
        except VkError:
            logging.error('Command Pool failed to create.')
            exit()

    def _createCommandBuffer(self):
        ''' Create Vulkan Command Buffer.

        Steps: (1)Create Command Buffer, (2)Record command buffer '''
        
        # Create command buffer
        allocateInfo = VkCommandBufferAllocateInfo(
            sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool = self.command_pool,
            level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount = len(self.swapchain_framebuffers))

        try:
            self.command_buffers = vkAllocateCommandBuffers(
                device = self.logical_device,
                pAllocateInfo = allocateInfo)
            logging.info('Created command buffer.')
        except VkError:
            logging.error('Command Buffer failed to create.')
            exit()

        # Record command buffer
        try:
            for i, command_buffer in enumerate(self.command_buffers):
                command_buffer_begin_createInfo = VkCommandBufferBeginInfo(
                    sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
                    flags = VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT,
                    #specifies how we're going to use the command buffer.
                    pInheritanceInfo = None
                    #only relevant for secondary command buffers
                    )

                vkBeginCommandBuffer( command_buffer,
                                      command_buffer_begin_createInfo )

                # Create render pass
                render_area = VkRect2D( offset = VkOffset2D(x=0,y=0),
                                        extent = self.swapchain_imageExtent )
                # - defines where shader loads and stores will take place.
                #   The pixels outside this region will have undefined values.
                #   It should match the size of the attachments for best performance.

                color = VkClearColorValue( float32 = [0., 0., 0., 1.0] )
                clear_value = VkClearValue( color = color )
                # - clear values to use for VK_ATTACHMENT_LOAD_OP_CLEAR, which 
                #   we used as load operation for the color attachment. Here, 
                #   clear color is black with 100% opacity.
                # - in float32 the SRGB numerical format is used: [R,G,B,A]
                #   where each is an unsigned normalized value (0. to 1.)

                render_pass_begin_createInfo = VkRenderPassBeginInfo(
                    sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
                    renderPass = self.render_pass,
                    renderArea = render_area,
                    framebuffer = self.swapchain_framebuffers[i],
                    clearValueCount = 1,
                    pClearValues = [clear_value] )

                # start render pass
                vkCmdBeginRenderPass( command_buffer,
                                      render_pass_begin_createInfo,
                                      VK_SUBPASS_CONTENTS_INLINE ) # see below comment
                # The render pass commands will be embedded in the primary command buffer
                # itself and no secondary command buffers will be executed.

                # Bind graphics pipeline
                vkCmdBindPipeline( command_buffer,
                                   VK_PIPELINE_BIND_POINT_GRAPHICS,
                                   self.graphics_pipeline )

                # Draw
                vkCmdDraw( command_buffer, 3, 1, 0, 0 )
                #vertexCount: Even though we don't have a vertex buffer, we
                #             technically still have 3 vertices to draw.
                #instanceCount: Used for instanced rendering, use 1 if you're not
                #               doing that.
                #firstVertex: Used as an offset into the vertex buffer, defines the
                #             lowest value of gl_VertexIndex.
                #firstInstance: Used as an offset for instanced rendering, defines
                #               the lowest value of gl_InstanceIndex.

                # End
                vkCmdEndRenderPass(command_buffer)
                vkEndCommandBuffer(command_buffer)

            logging.info('Recorded command buffer.')

        except VkError:
            logging.error('Command Buffer failed to record.')
            exit()


    def _createSemaphores(self):
        ''' Create 2 semaphores to synchronize the drawing and presentation
             of images by vkCmdDraw.

        Need one semaphore to signal that an image has been acquired and is
        ready for drawing, and another semaphore to signal that drawing has
        finished and presentation can happen.'''
        
        createInfo = VkSemaphoreCreateInfo(
            sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO)

        self.semaphore_image_available = vkCreateSemaphore( self.logical_device,
                                                            createInfo, None)

        self.semaphore_image_drawn = vkCreateSemaphore( self.logical_device,
                                                          createInfo, None)

        logging.info('Created Semaphore for image_available.')
        logging.info('Created Semaphore for image_drawn.')


    def _drawFrame(self):
        
        
        #1. Acquire an available presentable image from swapchain to use, and 
        #   retrieve the index of that image
        image_index = self.fnp['vkAcquireNextImageKHR'](
            self.logical_device, self.swapchain, UINT64_MAX,
            self.semaphore_image_available, VK_NULL_HANDLE )
        # Notes:-timeout=UINT64_MAX means this function will not return until
        #        an image is acquired from the presentation engine.
        #       -Other values for timeout will cause the function to return when
        #        an image becomes available, or when the specified number of
        #        nanoseconds have passed (in which case it will return
        #        VK_TIMEOUT). 

        # Added:
        # - Check if image_index's state is out-ofdate due to resizing of
        #   window.
        # - VK_ERROR_OUT_OF_DATE_KHR:
        #    the swapchain has become incompatible with the surface and can no
        #    longer be used for drawing.
        # - VK_SUBOPTIMAL_KHR:
        #    The swapchain can still be used to successfully present to the 
        #    surface, but the surface properties are no longer matched exactly. 
        #    For example, the platform may be simply resizing the image to fit 
        #    the window now.    
        if image_index == VK_ERROR_OUT_OF_DATE_KHR:
            self._recreateSwapChain()
            logging.info("VK_ERROR_OUT_OF_DATE_KHR: Need to recreate swapchain image!")
        elif image_index != VK_SUCCESS and image_index != VK_SUBOPTIMAL_KHR:
            logging.error("Failed to acquire swapchain image!")
        print('image_index = ', image_index)
        #print('image_index == VK_ERROR_OUT_OF_DATE_KHR = ', image_index == VK_ERROR_OUT_OF_DATE_KHR)
        #print('VK_ERROR_OUT_OF_DATE_KHR  = ', VK_ERROR_OUT_OF_DATE_KHR )

            
        #2. Create info to submit command buffer to queue')
        wait_semaphores = [self.semaphore_image_available]
        wait_stages = [VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT]
        signal_semaphores = [self.semaphore_image_drawn]
        submitInfo = VkSubmitInfo(
            sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
            waitSemaphoreCount = 1,
            pWaitSemaphores = wait_semaphores,
            pWaitDstStageMask = wait_stages,
            #- specify which semaphores to wait on before execution begins and
            #  in which stage(s) of the pipeline to wait. 
            commandBufferCount = 1,
            pCommandBuffers = [self.command_buffers[image_index]],
            #- specify which command buffers to actually submit for execution.
            #  As mentioned earlier, we should submit the command buffer that 
            #  binds the swap chain image we just acquired as color attachment.
            signalSemaphoreCount = 1,
            pSignalSemaphores = signal_semaphores)
            #- specify which semaphores to signal once the command buffer(s)
            #   have finished execution. In our case we're using the 
            #   renderFinishedSemaphore for that purpose.

        #3. Submit command buffer to queue
        vkQueueSubmit(self.graphics_queue, 1, submitInfo, None)

        #4. Setup Subpass Dependencies, see Section 8.4')

        #5 Create info to present command buffer result in swapchain')
        #  The last step of drawing a frame is submitting the result back to the
        #  swapchain to have it eventually show up on the screen. Presentation
        #  is configured through a VkPresentInfoKHR structure at the end of the
        #  drawFrame function.
        presentInfo = VkPresentInfoKHR(
            sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
            waitSemaphoreCount = 1,
            pWaitSemaphores = signal_semaphores,
            # above two parameters specify which semaphores to wait on before presentation
            # can happen, just like VkSubmitInfo.
            swapchainCount = 1,
            pSwapchains = [self.swapchain],
            pImageIndices = [image_index])
            # next two parameters specify the swapchains to present images to and the
            # index of the image for each swap chain. This will almost always be a
            # single one.
            #pResults = None) # Optional

        #6. Queue an image for presentation after queueing all rendering commands
        #   and transitioning the image to the correct layout
        result = self.fnp['vkQueuePresentKHR'](self.present_queue, presentInfo)
        print('result = ',result)
        #print('result == VK_ERROR_OUT_OF_DATE_KHR = ', result == VK_ERROR_OUT_OF_DATE_KHR)
        #print('result == VK_SUBOPTIMAL_KHR = ', result == VK_SUBOPTIMAL_KHR)

        # Added: Check if image_index state is out of date due to resizing of
        #        window (same as 'vkAcquireNextImageKHR'.
        if result == VK_ERROR_OUT_OF_DATE_KHR or result == VK_SUBOPTIMAL_KHR:
            logging.error("Needs to recreate swapchain.!")
            self._recreateSwapChain()
        elif result != VK_SUCCESS:
            logging.error("Failed to present swapchain image!")

        vkQueueWaitIdle(self.present_queue)

        


    def cleanup(self):
        '''Destroy Vulkan Object and it's children objects.'''
        
        if self.semaphore_image_drawn:
            vkDestroySemaphore( self.logical_device,
                                self.semaphore_image_drawn, None )
            logging.info('Destroyed Vulkan Semaphore for image_drawn.')

        if self.semaphore_image_available:
            vkDestroySemaphore( self.logical_device,
                                self.semaphore_image_available, None )
            logging.info('Destroyed Vulkan Semaphore for image_available.')

        if self.command_pool:
            vkDestroyCommandPool( self.logical_device, self.command_pool, None )
            logging.info('Destroyed Vulkan Command Pool.')


        vkDeviceWaitIdle(self.logical_device)
        logging.info('All outstanding queue operations for all queues in Logical'
                     ' Device have ceased.')
        if self.logical_device:
            vkDestroyDevice( self.logical_device, None )
            logging.info('Destroyed Vulkan Logical Device.')

        if self.surface:
            self.fnp['vkDestroySurfaceKHR']( self.instance, self.surface, None )
            logging.info('Destroyed Vulkan Surface.')

        if self.callback:
            self.fnp['vkDestroyDebugReportCallbackEXT']( self.instance,
                                                         self.callback, None)

        if self.instance:
            vkDestroyInstance(self.instance, None)
            logging.info('Destroyed Vulkan Instance.')


    def _cleanupSwapChain(self):
        '''Function to destroy the swapchain object and all objects that depend
            on the swapchain or can affect window size.'''

        if self.swapchain_framebuffers:
            for f in self.swapchain_framebuffers:
                vkDestroyFramebuffer( self.logical_device, f, None )
            self.swapchain_framebuffers = []
            logging.info('Destroyed Vulkan Framebuffers.')

        # Free existing command buffers
        if self.command_pool:
            self.command_buffer = vkFreeCommandBuffers(
                self.logical_device, self.command_pool, len(self.command_buffer) )
            
        if self.graphics_pipeline:
            vkDestroyPipeline( self.logical_device,
                               self.graphics_pipeline, None )
            logging.info('Destroyed Vulkan Graphics Pipeline.')

        if self.pipeline_layout:
            vkDestroyPipelineLayout( self.logical_device,
                                     self.pipeline_layout, None )
            logging.info('Destroyed Vulkan Pipeline Layout.')

        if self.render_pass:
            vkDestroyRenderPass( self.logical_device, self.render_pass, None )
            logging.info('Destroyed Vulkan Render Pass.')

        if self.swapchain_imageViews:
            for i in self.swapchain_imageViews:
                vkDestroyImageView( self.logical_device, i, None )
            self.swapchain_imageViews = []
            logging.info('Destroyed Vulkan Swapchain ImageViews.')

        if self.swapchain:
            self.fnp['vkDestroySwapchainKHR']( self.logical_device,
                                               self.swapchain, None )
            logging.info('Destroyed Vulkan Swapchain.')


    def _recreateSwapChain(self):
        '''Function to recreate swapchain and all of the creation functions for
           the objects that depend on the swapchain or the window size.'''
        vkDeviceWaitIdle(device)
        logging.info('All outstanding queue operations for all queues in Logical')

        self._cleanupSwapChain()

        self._createSwapChain()
        self._createImageviews()
        self._createRenderPass()
        self._createGraphicsPipeline()
        self._createFramebuffers()
        #self._createCommandPool()
        self._createCommandBuffer()

