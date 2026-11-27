#pragma once

#ifdef WITH_DLSS

#include <kinc/graphics4/rendertarget.h>

// Before kinc_init: asks the Vulkan backend for the extensions NGX needs (skipped when unavailable)
void dlss_request_extensions();
// After kinc_init: initializes NGX, returns whether DLSS Super Resolution can be used
bool dlss_init();
bool dlss_available();
// Optimal render resolution of a quality mode (0 Native AA/DLAA, 1 Quality, 2 Balanced, 3 Performance, 4 Ultra Performance)
bool dlss_render_size(int quality, int output_width, int output_height, int *render_width, int *render_height);
// Upscales color (render resolution, jittered) into output (display resolution). Motion vectors are
// multiplied by motion_scale to get render pixels pointing from the current to the previous frame.
bool dlss_evaluate(int quality, kinc_g4_render_target_t *color, kinc_g4_render_target_t *depth, kinc_g4_render_target_t *motion,
                   kinc_g4_render_target_t *output, float jitter_x, float jitter_y, float motion_scale_x, float motion_scale_y, bool reset, bool hdr);
void dlss_shutdown();

#endif
