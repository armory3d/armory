// utils.h - Engine utility functions
#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

// Maximum safe coordinate value for fixed-point conversion (avoid overflow)
#define MAX_SAFE_COORD 32000.0f

// Maximum world bounds for physics (objects beyond this are "off-world")
#define PHYSICS_WORLD_BOUNDS 1000.0f

/**
 * Check if a float is finite (not NaN or Inf).
 * N64/libdragon doesn't provide isfinite(), so we use bit manipulation.
 */
static inline bool float_is_finite(float f) {
    union { float f; uint32_t u; } val;
    val.f = f;
    // NaN and Inf have all exponent bits set (0x7F800000)
    return (val.u & 0x7F800000) != 0x7F800000;
}

/**
 * Check if transform values are safe for fixed-point conversion.
 * Returns false if any value is NaN, Inf, or too large.
 */
static inline bool transform_is_safe(const float* loc, const float* scale) {
    for (int i = 0; i < 3; i++) {
        if (!float_is_finite(loc[i]) || fabsf(loc[i]) > MAX_SAFE_COORD) return false;
        if (!float_is_finite(scale[i]) || fabsf(scale[i]) > MAX_SAFE_COORD) return false;
    }
    return true;
}

/**
 * Check if a position is within world bounds.
 */
static inline bool position_in_bounds(float x, float y, float z) {
    return fabsf(x) <= PHYSICS_WORLD_BOUNDS &&
           fabsf(y) <= PHYSICS_WORLD_BOUNDS &&
           fabsf(z) <= PHYSICS_WORLD_BOUNDS;
}

#ifdef __cplusplus
}
#endif
