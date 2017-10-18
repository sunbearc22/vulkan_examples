
'''Script by @Berserker66 to see attributes of python objects with cffi attributes '''

from vulkan import ffi
 
def __convert_struct_field( s, fields ):
    for field,fieldtype in fields:
        if fieldtype.type.kind == 'primitive':
            yield (field,getattr( s, field ))
        else:
            yield (field, convert_to_python( getattr( s, field ) ))
 
# call this function to expose the attributes of the cffi data
# version 1: Has error
'''
def convert_to_python(s):
    if type(s) == int:
        return s
    ffitype=ffi.typeof(s)
    if ffitype.kind == 'struct':
        return dict(__convert_struct_field( s, ffitype.fields ) )
    elif ffitype.kind == 'array':
        if ffitype.item.kind == 'primitive':
            if ffitype.item.cname == 'char':
                return ffi.string(s)
            else:
                return [ s[i] for i in range(ffitype.length) ]
        else:
            return [ convert_to_python(s[i]) for i in range(ffitype.length) ]
    elif ffitype.kind == 'primitive':
        return int(s)
'''

# call this function to expose the attributes of the cffi data
# version 2: Patched on 2017-10-12
def convert_to_python(s):
    if type(s) == int:
        return s
    ffitype=ffi.typeof(s)
    if ffitype.kind == 'struct':
        return dict(__convert_struct_field( s, ffitype.fields ) )
    elif ffitype.kind == 'array':
        if ffitype.item.kind == 'primitive':
            if ffitype.item.cname == 'char':
                return ffi.string(s)
            else:
                return [ s[i] for i in range(ffitype.length) ]
        else:
            if ffitype.length != None:
                return [ convert_to_python(s[i]) for i in range(ffitype.length) ]
            else:
                return convert_to_python(s[0])
    elif ffitype.kind == 'primitive':
        return int(s)

VkDebugReportObjectTypeEXT = {
    0 : 'VK_DEBUG_REPORT_OBJECT_TYPE_UNKNOWN_EXT',
    1 : 'VK_DEBUG_REPORT_OBJECT_TYPE_INSTANCE_EXT',
    2 : 'VK_DEBUG_REPORT_OBJECT_TYPE_PHYSICAL_DEVICE_EXT',
    3 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DEVICE_EXT',
    4 : 'VK_DEBUG_REPORT_OBJECT_TYPE_QUEUE_EXT',
    5 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SEMAPHORE_EXT',
    6 : 'VK_DEBUG_REPORT_OBJECT_TYPE_COMMAND_BUFFER_EXT',
    7 : 'VK_DEBUG_REPORT_OBJECT_TYPE_FENCE_EXT',
    8 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DEVICE_MEMORY_EXT',
    9 : 'VK_DEBUG_REPORT_OBJECT_TYPE_BUFFER_EXT',
    10 : 'VK_DEBUG_REPORT_OBJECT_TYPE_IMAGE_EXT',
    11 : 'VK_DEBUG_REPORT_OBJECT_TYPE_EVENT_EXT',
    12 : 'VK_DEBUG_REPORT_OBJECT_TYPE_QUERY_POOL_EXT',
    13 : 'VK_DEBUG_REPORT_OBJECT_TYPE_BUFFER_VIEW_EXT',
    14 : 'VK_DEBUG_REPORT_OBJECT_TYPE_IMAGE_VIEW_EXT',
    15 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SHADER_MODULE_EXT',
    16 : 'VK_DEBUG_REPORT_OBJECT_TYPE_PIPELINE_CACHE_EXT',
    17 : 'VK_DEBUG_REPORT_OBJECT_TYPE_PIPELINE_LAYOUT_EXT',
    18 : 'VK_DEBUG_REPORT_OBJECT_TYPE_RENDER_PASS_EXT',
    19 : 'VK_DEBUG_REPORT_OBJECT_TYPE_PIPELINE_EXT',
    20 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DESCRIPTOR_SET_LAYOUT_EXT',
    21 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SAMPLER_EXT',
    22 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DESCRIPTOR_POOL_EXT',
    23 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DESCRIPTOR_SET_EXT',
    24 : 'VK_DEBUG_REPORT_OBJECT_TYPE_FRAMEBUFFER_EXT',
    25 : 'VK_DEBUG_REPORT_OBJECT_TYPE_COMMAND_POOL_EXT',
    26 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SURFACE_KHR_EXT',
    27 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SWAPCHAIN_KHR_EXT',
    28 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DEBUG_REPORT_CALLBACK_EXT_EXT',
    29 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DISPLAY_KHR_EXT',
    30 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DISPLAY_MODE_KHR_EXT',
    31 : 'VK_DEBUG_REPORT_OBJECT_TYPE_OBJECT_TABLE_NVX_EXT',
    32 : 'VK_DEBUG_REPORT_OBJECT_TYPE_INDIRECT_COMMANDS_LAYOUT_NVX_EXT',
    33 : 'VK_DEBUG_REPORT_OBJECT_TYPE_VALIDATION_CACHE_EXT',
    1000085000 : 'VK_DEBUG_REPORT_OBJECT_TYPE_DESCRIPTOR_UPDATE_TEMPLATE_KHR_EXT',
    1000156000 : 'VK_DEBUG_REPORT_OBJECT_TYPE_SAMPLER_YCBCR_CONVERSION_KHR_EXT'
    }

'''
    @staticmethod
    def _printPhysicalDeviceProperties(properties):
        print('  Properties:')
        print('  -vendorID         : {}'.format(properties.deviceID))
        print('  -deviceName       : {}'.format(properties.deviceName))
        deviceType = properties.deviceType
        if deviceType == 0:
            deviceType_flag = 'VK_PHYSICAL_DEVICE_TYPE_OTHER'
        elif deviceType == 1:
            deviceType_flag = 'VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU'
        elif deviceType == 2:
            deviceType_flag = 'VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU'
        elif deviceType == 3:
            deviceType_flag = 'VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU'
        elif deviceType == 4:
            deviceType_flag = 'VK_PHYSICAL_DEVICE_TYPE_CPU'
        print('  -deviceType       : {}'.format(deviceType_flag))
        apiVersion = properties.apiVersion
        apiVersion_string = '{0}.{1}.{2}'.format(
            VK_VERSION_MAJOR(apiVersion),
            VK_VERSION_MINOR(apiVersion),
            VK_VERSION_PATCH(apiVersion))
        print('  -apiVersion       : {}'.format(apiVersion_string))
        driverVersion = properties.driverVersion
        driverVersion_string = '{0}.{1}.{2}'.format(
            VK_VERSION_MAJOR(driverVersion),
            VK_VERSION_MINOR(driverVersion),
            VK_VERSION_PATCH(driverVersion))
        print('  -driverVersion    : {}'.format(driverVersion_string))
        print('  -pipelineCacheUUID: {}'.format(len(
            properties.pipelineCacheUUID)))
        print('  -sparseProperties :')
        sparseProperties = properties.sparseProperties
        print('    residencyStandard2DBlockShape: {}'.format(sparseProperties.residencyStandard2DBlockShape))
        print('    residencyStandard2DMultisampleBlockShape: {}'.format(sparseProperties.residencyStandard2DMultisampleBlockShape))
        print('    residencyStandard3DBlockShape: {}'.format(sparseProperties.residencyStandard3DBlockShape))
        print('    residencyAlignedMipSize: {}'.format(sparseProperties.residencyAlignedMipSize))
        print('    residencyNonResidentStrict: {}'.format(sparseProperties.residencyNonResidentStrict))
        limits = properties.limits
        print('  -limits           :')
        print('    maxImageDimension1D: {}'.format(limits.maxImageDimension1D))
        print('    maxImageDimension2D: {}'.format(limits.maxImageDimension2D))
        print('    maxImageDimension3D: {}'.format(limits.maxImageDimension3D))
        print('    maxImageDimensionCube: {}'.format(limits.maxImageDimensionCube))
        print('    maxImageArrayLayers: {}'.format(limits.maxImageArrayLayers))
        print('    maxTexelBufferElements: {}'.format(limits.maxTexelBufferElements))
        print('    maxUniformBufferRange: {}'.format(limits.maxUniformBufferRange))
        print('    maxStorageBufferRange: {}'.format(limits.maxStorageBufferRange))
        print('    maxPushConstantsSize: {}'.format(limits.maxPushConstantsSize))
        print('    maxMemoryAllocationCount: {}'.format(limits.maxMemoryAllocationCount))
        print('    maxSamplerAllocationCount: {}'.format(limits.maxSamplerAllocationCount))
        print('    bufferImageGranularity: {}'.format(limits.bufferImageGranularity))
        print('    sparseAddressSpaceSize: {}'.format(limits.sparseAddressSpaceSize))
        print('    maxBoundDescriptorSets: {}'.format(limits.maxBoundDescriptorSets))
        print('    maxPerStageDescriptorSamplers: {}'.format(limits.maxPerStageDescriptorSamplers))
        print('    maxPerStageDescriptorUniformBuffers: {}'.format(limits.maxPerStageDescriptorUniformBuffers))
        print('    maxPerStageDescriptorStorageBuffers: {}'.format(limits.maxPerStageDescriptorStorageBuffers))
        print('    maxPerStageDescriptorSampledImages: {}'.format(limits.maxPerStageDescriptorSampledImages))
        print('    maxPerStageDescriptorStorageImages: {}'.format(limits.maxPerStageDescriptorStorageImages))
        print('    maxPerStageDescriptorInputAttachments: {}'.format(limits.maxPerStageDescriptorInputAttachments))
        print('    maxPerStageResources: {}'.format(limits.maxPerStageResources))
        print('    maxDescriptorSetSamplers: {}'.format(limits.maxDescriptorSetSamplers))
        print('    maxDescriptorSetUniformBuffers: {}'.format(limits.maxDescriptorSetUniformBuffers))
        print('    maxDescriptorSetUniformBuffersDynamic: {}'.format(limits.maxDescriptorSetUniformBuffersDynamic))
        print('    maxDescriptorSetStorageBuffers: {}'.format(limits.maxDescriptorSetStorageBuffers))
        print('    maxDescriptorSetStorageBuffersDynamic: {}'.format(limits.maxDescriptorSetStorageBuffersDynamic))
        print('    maxDescriptorSetSampledImages: {}'.format(limits.maxDescriptorSetSampledImages))
        print('    maxDescriptorSetStorageImages: {}'.format(limits.maxDescriptorSetStorageImages))
        print('    maxDescriptorSetInputAttachments: {}'.format(limits.maxDescriptorSetInputAttachments))
        print('    maxVertexInputAttributes: {}'.format(limits.maxVertexInputAttributes))
        print('    maxVertexInputBindings: {}'.format(limits.maxVertexInputBindings))
        print('    maxVertexInputAttributeOffset: {}'.format(limits.maxVertexInputAttributeOffset))
        print('    maxVertexInputBindingStride: {}'.format(limits.maxVertexInputBindingStride))
        print('    maxVertexOutputComponents: {}'.format(limits.maxVertexOutputComponents))
        print('    maxTessellationGenerationLevel: {}'.format(limits.maxTessellationGenerationLevel))
        print('    maxTessellationPatchSize: {}'.format(limits.maxTessellationPatchSize))
        print('    maxTessellationControlPerVertexInputComponents: {}'.format(limits.maxTessellationControlPerVertexInputComponents))
        print('    maxTessellationControlPerVertexOutputComponents: {}'.format(limits.maxTessellationControlPerVertexOutputComponents))
        print('    maxTessellationControlPerPatchOutputComponents: {}'.format(limits.maxTessellationControlPerPatchOutputComponents))
        print('    maxTessellationControlTotalOutputComponents: {}'.format(limits.maxTessellationControlTotalOutputComponents))
        print('    maxTessellationEvaluationInputComponents: {}'.format(limits.maxTessellationEvaluationInputComponents))
        print('    maxTessellationEvaluationOutputComponents: {}'.format(limits.maxTessellationEvaluationOutputComponents))
        print('    maxGeometryShaderInvocations: {}'.format(limits.maxGeometryShaderInvocations))
        print('    maxGeometryInputComponents: {}'.format(limits.maxGeometryInputComponents))
        print('    maxGeometryOutputComponents: {}'.format(limits.maxGeometryOutputComponents))
        print('    maxGeometryOutputVertices: {}'.format(limits.maxGeometryOutputVertices))
        print('    maxGeometryTotalOutputComponents: {}'.format(limits.maxGeometryTotalOutputComponents))
        print('    maxFragmentInputComponents: {}'.format(limits.maxFragmentInputComponents))
        print('    maxFragmentOutputAttachments: {}'.format(limits.maxFragmentOutputAttachments))
        print('    maxFragmentDualSrcAttachments: {}'.format(limits.maxFragmentDualSrcAttachments))
        print('    maxFragmentCombinedOutputResources: {}'.format(limits.maxFragmentCombinedOutputResources))
        print('    maxComputeSharedMemorySize: {}'.format(limits.maxComputeSharedMemorySize))
        print('    maxComputeWorkGroupCount[3]: {}'.format(limits.maxComputeWorkGroupCount[2]))# 3-1
        print('    maxComputeWorkGroupInvocations: {}'.format(limits.maxComputeWorkGroupInvocations))
        print('    maxComputeWorkGroupSize[3]: {}'.format(limits.maxComputeWorkGroupSize[2]))# 3-1
        print('    subPixelPrecisionBits: {}'.format(limits.subPixelPrecisionBits))
        print('    subTexelPrecisionBits: {}'.format(limits.subTexelPrecisionBits))
        print('    mipmapPrecisionBits: {}'.format(limits.mipmapPrecisionBits))
        print('    maxDrawIndexedIndexValue: {}'.format(limits.maxDrawIndexedIndexValue))
        print('    maxDrawIndirectCount: {}'.format(limits.maxDrawIndirectCount))
        print('    maxSamplerLodBias: {}'.format(limits.maxSamplerLodBias))
        print('    maxSamplerAnisotropy: {}'.format(limits.maxSamplerAnisotropy))
        print('    maxViewports: {}'.format(limits.maxViewports))
        print('    maxViewportDimensions[2]: {}'.format(limits.maxViewportDimensions[1]))# 2-1 
        print('    viewportBoundsRange[2]: {}'.format(limits.viewportBoundsRange[1]))# 2-1
        print('    viewportSubPixelBits: {}'.format(limits.viewportSubPixelBits))
        print('    minMemoryMapAlignment: {}'.format(limits.minMemoryMapAlignment))
        print('    minTexelBufferOffsetAlignment: {}'.format(limits.minTexelBufferOffsetAlignment))
        print('    minUniformBufferOffsetAlignment: {}'.format(limits.minUniformBufferOffsetAlignment))
        print('    minStorageBufferOffsetAlignment: {}'.format(limits.minStorageBufferOffsetAlignment))
        print('    minTexelOffset: {}'.format(limits.minTexelOffset))
        print('    maxTexelOffset: {}'.format(limits.maxTexelOffset))
        print('    minTexelGatherOffset: {}'.format(limits.minTexelGatherOffset))
        print('    maxTexelGatherOffset: {}'.format(limits.maxTexelGatherOffset))
        print('    minInterpolationOffset: {}'.format(limits.minInterpolationOffset))
        print('    maxInterpolationOffset: {}'.format(limits.maxInterpolationOffset))
        print('    subPixelInterpolationOffsetBits: {}'.format(limits.subPixelInterpolationOffsetBits))
        print('    maxFramebufferWidth: {}'.format(limits.maxFramebufferWidth))
        print('    maxFramebufferHeight: {}'.format(limits.maxFramebufferHeight))
        print('    maxFramebufferLayers: {}'.format(limits.maxFramebufferLayers))
        print('    framebufferColorSampleCounts: {}'.format(limits.framebufferColorSampleCounts))
        print('    framebufferDepthSampleCounts: {}'.format(limits.framebufferDepthSampleCounts))
        print('    framebufferStencilSampleCounts: {}'.format(limits.framebufferStencilSampleCounts))
        print('    framebufferNoAttachmentsSampleCounts: {}'.format(limits.framebufferNoAttachmentsSampleCounts))
        print('    maxColorAttachments: {}'.format(limits.maxColorAttachments))
        print('    sampledImageColorSampleCounts: {}'.format(limits.sampledImageColorSampleCounts))
        print('    sampledImageIntegerSampleCounts: {}'.format(limits.sampledImageIntegerSampleCounts))
        print('    sampledImageDepthSampleCounts: {}'.format(limits.sampledImageDepthSampleCounts))
        print('    sampledImageStencilSampleCounts: {}'.format(limits.sampledImageStencilSampleCounts))
        print('    storageImageSampleCounts: {}'.format(limits.storageImageSampleCounts))
        print('    maxSampleMaskWords: {}'.format(limits.maxSampleMaskWords))
        print('    timestampComputeAndGraphics: {}'.format(limits.timestampComputeAndGraphics))
        print('    timestampPeriod: {}'.format(limits.timestampPeriod))
        print('    maxClipDistances: {}'.format(limits.maxClipDistances))
        print('    maxCullDistances: {}'.format(limits.maxCullDistances))
        print('    maxCombinedClipAndCullDistances: {}'.format(limits.maxCombinedClipAndCullDistances))
        print('    discreteQueuePriorities: {}'.format(limits.discreteQueuePriorities))
        print('    pointSizeRange[2]: {}'.format(limits.pointSizeRange[1]))# 2-1
        print('    lineWidthRange[2]: {}'.format(limits.lineWidthRange[1]))# 2-1
        print('    pointSizeGranularity: {}'.format(limits.pointSizeGranularity))
        print('    lineWidthGranularity: {}'.format(limits.lineWidthGranularity))
        print('    strictLines: {}'.format(limits.strictLines))
        print('    standardSampleLocations: {}'.format(limits.standardSampleLocations))
        print('    optimalBufferCopyOffsetAlignment: {}'.format(limits.optimalBufferCopyOffsetAlignment))
        print('    optimalBufferCopyRowPitchAlignment: {}'.format(limits.optimalBufferCopyRowPitchAlignment))
        print('    nonCoherentAtomSize: {}'.format(limits.nonCoherentAtomSize))
        

    @staticmethod
    def _printPhysicalDeviceFeatures(features):
        print('  Features:')
        print('  -robustBufferAccess: {}'.format(features.robustBufferAccess))
        print('  -fullDrawIndexUint32: {}'.format(features.fullDrawIndexUint32))
        print('  -imageCubeArray: {}'.format(features.imageCubeArray))
        print('  -independentBlend: {}'.format(features.independentBlend))
        print('  -geometryShader: {}'.format(features.geometryShader))
        print('  -tessellationShader: {}'.format(features.tessellationShader))
        print('  -sampleRateShading: {}'.format(features.sampleRateShading))
        print('  -dualSrcBlend: {}'.format(features.dualSrcBlend))
        print('  -logicOp: {}'.format(features.logicOp))
        print('  -multiDrawIndirect: {}'.format(features.multiDrawIndirect))
        print('  -drawIndirectFirstInstance: {}'.format(features.drawIndirectFirstInstance))
        print('  -depthClamp: {}'.format(features.depthClamp))
        print('  -depthBiasClamp: {}'.format(features.depthBiasClamp))
        print('  -fillModeNonSolid: {}'.format(features.fillModeNonSolid))
        print('  -depthBounds: {}'.format(features.depthBounds))
        print('  -wideLines: {}'.format(features.wideLines))
        print('  -largePoints: {}'.format(features.largePoints))
        print('  -alphaToOne: {}'.format(features.alphaToOne))
        print('  -multiViewport: {}'.format(features.multiViewport))
        print('  -samplerAnisotropy: {}'.format(features.samplerAnisotropy))
        print('  -textureCompressionETC2: {}'.format(features.textureCompressionETC2))
        print('  -textureCompressionASTC_LDR: {}'.format(features.textureCompressionASTC_LDR))
        print('  -textureCompressionBC: {}'.format(features.textureCompressionBC))
        print('  -occlusionQueryPrecise: {}'.format(features.occlusionQueryPrecise))
        print('  -pipelineStatisticsQuery: {}'.format(features.pipelineStatisticsQuery))
        print('  -vertexPipelineStoresAndAtomics: {}'.format(features.vertexPipelineStoresAndAtomics))
        print('  -fragmentStoresAndAtomics: {}'.format(features.fragmentStoresAndAtomics))
        print('  -shaderTessellationAndGeometryPointSize: {}'.format(features.shaderTessellationAndGeometryPointSize))
        print('  -shaderImageGatherExtended: {}'.format(features.shaderImageGatherExtended))
        print('  -shaderStorageImageExtendedFormats: {}'.format(features.shaderStorageImageExtendedFormats))
        print('  -shaderStorageImageMultisample: {}'.format(features.shaderStorageImageMultisample))
        print('  -shaderStorageImageReadWithoutFormat: {}'.format(features.shaderStorageImageReadWithoutFormat))
        print('  -shaderStorageImageWriteWithoutFormat: {}'.format(features.shaderStorageImageWriteWithoutFormat))
        print('  -shaderUniformBufferArrayDynamicIndexing: {}'.format(features.shaderUniformBufferArrayDynamicIndexing))
        print('  -shaderSampledImageArrayDynamicIndexing: {}'.format(features.shaderSampledImageArrayDynamicIndexing))
        print('  -shaderStorageBufferArrayDynamicIndexing: {}'.format(features.shaderStorageBufferArrayDynamicIndexing))
        print('  -shaderStorageImageArrayDynamicIndexing: {}'.format(features.shaderStorageImageArrayDynamicIndexing))
        print('  -shaderClipDistance: {}'.format(features.shaderClipDistance))
        print('  -shaderCullDistance: {}'.format(features.shaderCullDistance))
        print('  -shaderFloat64: {}'.format(features.shaderFloat64))
        print('  -shaderInt64: {}'.format(features.shaderInt64))
        print('  -shaderInt16: {}'.format(features.shaderInt16))
        print('  -shaderResourceResidency: {}'.format(features.shaderResourceResidency))
        print('  -shaderResourceMinLod: {}'.format(features.shaderResourceMinLod))
        print('  -sparseBinding: {}'.format(features.sparseBinding))
        print('  -sparseResidencyBuffer: {}'.format(features.sparseResidencyBuffer))
        print('  -sparseResidencyImage2D: {}'.format(features.sparseResidencyImage2D))
        print('  -sparseResidencyImage3D: {}'.format(features.sparseResidencyImage3D))
        print('  -sparseResidency2Samples: {}'.format(features.sparseResidency2Samples))
        print('  -sparseResidency4Samples: {}'.format(features.sparseResidency4Samples))
        print('  -sparseResidency8Samples: {}'.format(features.sparseResidency8Samples))
        print('  -sparseResidency16Samples: {}'.format(features.sparseResidency16Samples))
        print('  -sparseResidencyAliased: {}'.format(features.sparseResidencyAliased))
        print('  -variableMultisampleRate: {}'.format(features.variableMultisampleRate))
        print('  -inheritedQueries: {}'.format(features.inheritedQueries))





    @staticmethod
    def _printPhysicalDeviceMemoryProperties(memory):
        print('  Memory:')
        print('  -memoryTypeCount: {}'.format(memory.memoryTypeCount))
        print('  -memoryTypes[VK_MAX_MEMORY_TYPES]:')
        for n, i in enumerate(memory.memoryTypes):
            print('    -{}, propertyFlags: {}, heapIndex: {}'.format(
                n, i.propertyFlags, i.heapIndex))
            if n == memory.memoryTypeCount - 1: break
        print('  -memoryHeapCount: {}'.format(memory.memoryHeapCount))
        print('  -memoryHeaps[VK_MAX_MEMORY_HEAPS]:')
        size = 0
        for n, i in enumerate(memory.memoryHeaps):
            print('    -{}, size: {}, flags: {}'.format(n, i.size, i.flags))
            if i.flags == 1 and i.size:
                size += i.size
            if n == memory.memoryHeapCount - 1: break
        print('GPU memory size = ', size)
            
'''
