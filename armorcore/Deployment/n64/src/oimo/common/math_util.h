/**
 * OimoPhysics N64 Port - Math Utilities
 *
 * Mathematical operations using libdragon fastmath.
 * Based on OimoPhysics MathUtil.hx
 */

#ifndef OIMO_COMMON_MATH_UTIL_H
#define OIMO_COMMON_MATH_UTIL_H

#include "setting.h"
#include <libdragon.h>
#include <math.h>

// ============================================================================
// Constants
// ============================================================================
#define OIMO_PI         3.14159265358979f
#define OIMO_TWO_PI     6.28318530717958f
#define OIMO_HALF_PI    1.57079632679490f
#define OIMO_TO_RADIANS 0.01745329251994f   // PI / 180
#define OIMO_TO_DEGREES 57.2957795130823f   // 180 / PI

// ============================================================================
// Basic Math Functions
// ============================================================================

static inline OimoScalar oimo_abs(OimoScalar x) {
    return x > 0 ? x : -x;
}

static inline OimoScalar oimo_min(OimoScalar a, OimoScalar b) {
    return a < b ? a : b;
}

static inline OimoScalar oimo_max(OimoScalar a, OimoScalar b) {
    return a > b ? a : b;
}

static inline OimoScalar oimo_clamp(OimoScalar x, OimoScalar min_val, OimoScalar max_val) {
    return x < min_val ? min_val : (x > max_val ? max_val : x);
}

// ============================================================================
// Trigonometric Functions (using libdragon fastmath where available)
// ============================================================================

static inline OimoScalar oimo_sqrt(OimoScalar x) {
    return fm_sqrtf(x);
}

static inline OimoScalar oimo_sin(OimoScalar x) {
    return fm_sinf(x);
}

static inline OimoScalar oimo_cos(OimoScalar x) {
    return fm_cosf(x);
}

static inline OimoScalar oimo_tan(OimoScalar x) {
    return fm_tanf(x);
}

static inline OimoScalar oimo_asin(OimoScalar x) {
    return asinf(x);  // No fastmath version available
}

static inline OimoScalar oimo_acos(OimoScalar x) {
    return acosf(x);  // No fastmath version available
}

static inline OimoScalar oimo_atan(OimoScalar x) {
    return atanf(x);  // No fastmath version available
}

static inline OimoScalar oimo_atan2(OimoScalar y, OimoScalar x) {
    return atan2f(y, x);  // No fastmath version available
}

// ============================================================================
// Safe Trigonometric Functions (prevent NaN)
// ============================================================================

// Returns asin(clamp(x, -1, 1)) - never returns NaN
static inline OimoScalar oimo_safe_asin(OimoScalar x) {
    if (x <= -1.0f) return -OIMO_HALF_PI;
    if (x >= 1.0f) return OIMO_HALF_PI;
    return asinf(x);
}

// Returns acos(clamp(x, -1, 1)) - never returns NaN
static inline OimoScalar oimo_safe_acos(OimoScalar x) {
    if (x <= -1.0f) return OIMO_PI;
    if (x >= 1.0f) return 0.0f;
    return acosf(x);
}

// ============================================================================
// Utility Functions
// ============================================================================

// Inverse square root (1 / sqrt(x))
static inline OimoScalar oimo_inv_sqrt(OimoScalar x) {
    if (x <= 0) return 0;
    return 1.0f / fm_sqrtf(x);
}

// Sign function: returns -1, 0, or 1
static inline int oimo_sign(OimoScalar x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}

// Linear interpolation
static inline OimoScalar oimo_lerp(OimoScalar a, OimoScalar b, OimoScalar t) {
    return a + (b - a) * t;
}

#endif // OIMO_COMMON_MATH_UTIL_H
