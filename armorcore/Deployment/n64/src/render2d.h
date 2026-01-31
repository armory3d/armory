// render2d.h - 2D rendering for N64 (libdragon rdpq)
#pragma once

#include <libdragon.h>

#ifdef __cplusplus
extern "C" {
#endif

// Screen dimensions
static inline int render2d_get_width(void) { return display_get_width(); }
static inline int render2d_get_height(void) { return display_get_height(); }

// 2D rendering lifecycle (called per frame)
static inline void render2d_begin(void) {}
static inline void render2d_end(void) {}

// Filled rectangle with alpha blending
static inline void render2d_fill_rect(int x0, int y0, int x1, int y1, color_t color) {
    if (color_to_packed32(color) == 0) return;
    rdpq_set_mode_standard();
    rdpq_mode_combiner(RDPQ_COMBINER_FLAT);
    rdpq_mode_blender(RDPQ_BLENDER_MULTIPLY);
    rdpq_set_prim_color(color);
    rdpq_fill_rectangle(x0, y0, x1, y1);
}

#ifdef __cplusplus
}
#endif
