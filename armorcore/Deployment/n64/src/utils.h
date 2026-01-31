// utils.h - Engine utility functions
#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_SAFE_COORD 32000.0f
#define PHYSICS_WORLD_BOUNDS 1000.0f

// Check if float is finite (N64 doesn't have isfinite)
static inline bool float_is_finite(float f) {
    union { float f; uint32_t u; } val;
    val.f = f;
    return (val.u & 0x7F800000) != 0x7F800000;
}

// Check if transform values are safe for fixed-point conversion
static inline bool transform_is_safe(const float* loc, const float* scale) {
    for (int i = 0; i < 3; i++) {
        if (!float_is_finite(loc[i]) || fabsf(loc[i]) > MAX_SAFE_COORD) return false;
        if (!float_is_finite(scale[i]) || fabsf(scale[i]) > MAX_SAFE_COORD) return false;
    }
    return true;
}

// Check if position is within world bounds
static inline bool position_in_bounds(float x, float y, float z) {
    return fabsf(x) <= PHYSICS_WORLD_BOUNDS &&
           fabsf(y) <= PHYSICS_WORLD_BOUNDS &&
           fabsf(z) <= PHYSICS_WORLD_BOUNDS;
}

// String formatting - rotating buffer for multiple calls per frame
#define STR_FMT_BUFFER_SIZE 64
#define STR_FMT_BUFFER_COUNT 4
static char _str_fmt_buffers[STR_FMT_BUFFER_COUNT][STR_FMT_BUFFER_SIZE];
static int _str_fmt_buffer_idx = 0;

static inline char* _str_get_buffer(void) {
    char* buf = _str_fmt_buffers[_str_fmt_buffer_idx];
    _str_fmt_buffer_idx = (_str_fmt_buffer_idx + 1) % STR_FMT_BUFFER_COUNT;
    return buf;
}

#define _str_concat(fmt, ...) ({ \
    char* _buf = _str_get_buffer(); \
    snprintf(_buf, STR_FMT_BUFFER_SIZE, fmt, ##__VA_ARGS__); \
    _buf; \
})

#ifdef __cplusplus
}
#endif
