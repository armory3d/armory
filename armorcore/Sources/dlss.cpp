// NVIDIA DLSS Super Resolution for the Vulkan build of Krom (via the NGX SDK in armorcore/dlss).
//
// Flow: dlss_request_extensions() before kinc_init, dlss_init() after it; then per frame the JS side
// asks for the render size of a quality mode (dlss_configure) and calls dlss_evaluate() with the
// jittered low-resolution color, depth and motion vectors and the full-resolution output target.
// Render targets in the Vulkan backend live in VK_IMAGE_LAYOUT_GENERAL, which NGX accepts as is.

#ifdef WITH_DLSS

#include "dlss.h"

#include <kinc/graphics4/rendertarget.h>
#include <kinc/log.h>

#include <vulkan/vulkan.h>

#include <nvsdk_ngx_vk.h>
#include <nvsdk_ngx_helpers.h>
#include <nvsdk_ngx_helpers_vk.h>

#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <string>

extern "C" {
void kinc_vulkan_request_instance_extensions(const char **extensions, int count);
void kinc_vulkan_request_device_extensions(const char **extensions, int count);
void kinc_vulkan_get_handles(VkInstance *instance, VkPhysicalDevice *physical_device, VkDevice *device, VkQueue *queue);
VkCommandBuffer kinc_vulkan_begin_external_commands(void);
void kinc_vulkan_end_external_commands(void);
void kinc_vulkan_render_target_get_image(kinc_g5_render_target_t *target, bool depth, VkImage *image, VkImageView *view, VkFormat *format);
}

namespace {
	// Project identification for custom engines (no NVIDIA-issued application id)
	const char *project_id = "1e82895f-f98b-4044-9669-616e715f4ed7";

	bool initialized = false;
	bool available = false;
	VkDevice device = VK_NULL_HANDLE;
	NVSDK_NGX_Parameter *parameters = nullptr;
	NVSDK_NGX_Handle *feature = nullptr;

	// Settings the current feature was created with; a change recreates it
	int feature_quality = -1;
	int feature_render_width = 0, feature_render_height = 0;
	int feature_output_width = 0, feature_output_height = 0;
	int feature_flags = 0;

	std::wstring executable_directory() {
		char path[PATH_MAX];
		ssize_t length = readlink("/proc/self/exe", path, sizeof(path) - 1);
		if (length <= 0) {
			return L".";
		}
		path[length] = 0;
		char *slash = strrchr(path, '/');
		if (slash != nullptr) {
			*slash = 0;
		}
		return std::wstring(path, path + strlen(path));
	}

	NVSDK_NGX_PerfQuality_Value to_ngx_quality(int quality) {
		// Matches Armory's upscale modes: 0 Native AA, 1 Quality, 2 Balanced, 3 Performance, 4 Ultra Performance
		switch (quality) {
		case 0:
			return NVSDK_NGX_PerfQuality_Value_DLAA;
		case 1:
			return NVSDK_NGX_PerfQuality_Value_MaxQuality;
		case 2:
			return NVSDK_NGX_PerfQuality_Value_Balanced;
		case 3:
			return NVSDK_NGX_PerfQuality_Value_MaxPerf;
		default:
			return NVSDK_NGX_PerfQuality_Value_UltraPerformance;
		}
	}

	NVSDK_NGX_Resource_VK make_resource(kinc_g4_render_target_t *target, bool depth, bool read_write) {
		VkImage image;
		VkImageView view;
		VkFormat format;
		kinc_vulkan_render_target_get_image(&target->impl._renderTarget, depth, &image, &view, &format);
		bool is_depth = depth || format == VK_FORMAT_D16_UNORM || format == VK_FORMAT_D32_SFLOAT;
		VkImageSubresourceRange range = {(VkImageAspectFlags)(is_depth ? VK_IMAGE_ASPECT_DEPTH_BIT : VK_IMAGE_ASPECT_COLOR_BIT), 0, 1, 0, 1};
		return NVSDK_NGX_Create_ImageView_Resource_VK(view, image, range, format, target->width, target->height, read_write);
	}

	void release_feature() {
		if (feature != nullptr) {
			vkDeviceWaitIdle(device);
			NVSDK_NGX_VULKAN_ReleaseFeature(feature);
			feature = nullptr;
		}
	}
}

void dlss_request_extensions() {
	unsigned int instance_count = 0, device_count = 0;
	const char **instance_extensions = nullptr;
	const char **device_extensions = nullptr;
	// Deprecated in favor of the per-feature queries, but it needs no VkInstance, which we don't have yet
	NVSDK_NGX_Result result = NVSDK_NGX_VULKAN_RequiredExtensions(&instance_count, &instance_extensions, &device_count, &device_extensions);
	if (NVSDK_NGX_FAILED(result)) {
		kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: could not query required Vulkan extensions (0x%x)", (unsigned)result);
		return;
	}
	kinc_vulkan_request_instance_extensions(instance_extensions, (int)instance_count);
	kinc_vulkan_request_device_extensions(device_extensions, (int)device_count);
}

bool dlss_init() {
	if (initialized) {
		return available;
	}
	initialized = true;

	VkInstance instance;
	VkPhysicalDevice physical_device;
	VkQueue queue;
	kinc_vulkan_get_handles(&instance, &physical_device, &device, &queue);

	std::wstring directory = executable_directory();
	const wchar_t *paths[] = {directory.c_str()};
	NVSDK_NGX_FeatureCommonInfo info = {};
	info.PathListInfo.Path = paths;
	info.PathListInfo.Length = 1;
	info.LoggingInfo.MinimumLoggingLevel = NVSDK_NGX_LOGGING_LEVEL_OFF;

	NVSDK_NGX_Result result = NVSDK_NGX_VULKAN_Init_with_ProjectID(project_id, NVSDK_NGX_ENGINE_TYPE_CUSTOM, "Armory", L"/tmp", instance, physical_device,
	                                                               device, vkGetInstanceProcAddr, vkGetDeviceProcAddr, &info);
	if (NVSDK_NGX_FAILED(result)) {
		kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: NGX init failed (0x%x)", (unsigned)result);
		return false;
	}

	result = NVSDK_NGX_VULKAN_GetCapabilityParameters(&parameters);
	if (NVSDK_NGX_FAILED(result) || parameters == nullptr) {
		kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: no NGX capability parameters (0x%x)", (unsigned)result);
		return false;
	}

	int needs_driver = 0;
	if (NVSDK_NGX_SUCCEED(parameters->Get(NVSDK_NGX_Parameter_SuperSampling_NeedsUpdatedDriver, &needs_driver)) && needs_driver) {
		kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: needs a newer NVIDIA driver");
		return false;
	}
	int supported = 0;
	result = parameters->Get(NVSDK_NGX_Parameter_SuperSampling_Available, &supported);
	if (NVSDK_NGX_FAILED(result) || !supported) {
		int feature_result = 0;
		parameters->Get(NVSDK_NGX_Parameter_SuperSampling_FeatureInitResult, &feature_result);
		kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: not available on this system (0x%x)", (unsigned)feature_result);
		return false;
	}

	available = true;
	kinc_log(KINC_LOG_LEVEL_INFO, "DLSS: available");
	return true;
}

bool dlss_available() {
	return available;
}

bool dlss_render_size(int quality, int output_width, int output_height, int *render_width, int *render_height) {
	if (!available) {
		return false;
	}
	unsigned int optimal_width = 0, optimal_height = 0, max_width, max_height, min_width, min_height;
	float sharpness = 0.0f;
	NVSDK_NGX_Result result = NGX_DLSS_GET_OPTIMAL_SETTINGS(parameters, output_width, output_height, to_ngx_quality(quality), &optimal_width, &optimal_height,
	                                                        &max_width, &max_height, &min_width, &min_height, &sharpness);
	if (NVSDK_NGX_FAILED(result) || optimal_width == 0 || optimal_height == 0) {
		return false;
	}
	*render_width = (int)optimal_width;
	*render_height = (int)optimal_height;
	return true;
}

bool dlss_evaluate(int quality, kinc_g4_render_target_t *color, kinc_g4_render_target_t *depth, kinc_g4_render_target_t *motion,
                   kinc_g4_render_target_t *output, float jitter_x, float jitter_y, float motion_scale_x, float motion_scale_y, bool reset, bool hdr) {
	if (!available) {
		return false;
	}

	VkCommandBuffer commands = kinc_vulkan_begin_external_commands();
	if (commands == VK_NULL_HANDLE) {
		return false;
	}

	int flags = NVSDK_NGX_DLSS_Feature_Flags_MVLowRes | (hdr ? NVSDK_NGX_DLSS_Feature_Flags_IsHDR : 0);
	if (feature == nullptr || quality != feature_quality || color->width != feature_render_width || color->height != feature_render_height ||
	    output->width != feature_output_width || output->height != feature_output_height || flags != feature_flags) {
		release_feature();
		NVSDK_NGX_DLSS_Create_Params create = {};
		create.Feature.InWidth = color->width;
		create.Feature.InHeight = color->height;
		create.Feature.InTargetWidth = output->width;
		create.Feature.InTargetHeight = output->height;
		create.Feature.InPerfQualityValue = to_ngx_quality(quality);
		create.InFeatureCreateFlags = flags;
		NVSDK_NGX_Result result = NGX_VULKAN_CREATE_DLSS_EXT1(device, commands, 1, 1, &feature, parameters, &create);
		if (NVSDK_NGX_FAILED(result)) {
			kinc_log(KINC_LOG_LEVEL_ERROR, "DLSS: feature creation failed (0x%x)", (unsigned)result);
			feature = nullptr;
			kinc_vulkan_end_external_commands();
			return false;
		}
		feature_quality = quality;
		feature_render_width = color->width;
		feature_render_height = color->height;
		feature_output_width = output->width;
		feature_output_height = output->height;
		feature_flags = flags;
		reset = true;
	}

	NVSDK_NGX_Resource_VK color_resource = make_resource(color, false, false);
	NVSDK_NGX_Resource_VK depth_resource = make_resource(depth, true, false);
	NVSDK_NGX_Resource_VK motion_resource = make_resource(motion, false, false);
	NVSDK_NGX_Resource_VK output_resource = make_resource(output, false, true);

	NVSDK_NGX_VK_DLSS_Eval_Params eval = {};
	eval.Feature.pInColor = &color_resource;
	eval.Feature.pInOutput = &output_resource;
	eval.pInDepth = &depth_resource;
	eval.pInMotionVectors = &motion_resource;
	eval.InJitterOffsetX = jitter_x;
	eval.InJitterOffsetY = jitter_y;
	eval.InRenderSubrectDimensions.Width = color->width;
	eval.InRenderSubrectDimensions.Height = color->height;
	eval.InReset = reset ? 1 : 0;
	eval.InMVScaleX = motion_scale_x;
	eval.InMVScaleY = motion_scale_y;
	eval.InPreExposure = 1.0f;
	eval.InExposureScale = 1.0f;

	NVSDK_NGX_Result result = NGX_VULKAN_EVALUATE_DLSS_EXT(commands, feature, parameters, &eval);
	kinc_vulkan_end_external_commands();
	if (NVSDK_NGX_FAILED(result)) {
		static bool reported = false;
		if (!reported) {
			kinc_log(KINC_LOG_LEVEL_ERROR, "DLSS: evaluation failed (0x%x)", (unsigned)result);
			reported = true;
		}
		return false;
	}
	return true;
}

void dlss_shutdown() {
	if (!initialized) {
		return;
	}
	release_feature();
	if (parameters != nullptr) {
		NVSDK_NGX_VULKAN_DestroyParameters(parameters);
		parameters = nullptr;
	}
	if (device != VK_NULL_HANDLE) {
		NVSDK_NGX_VULKAN_Shutdown1(device);
	}
	initialized = false;
	available = false;
}

#endif
