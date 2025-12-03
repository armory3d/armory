#ifndef OIMO_COMMON_MATH_UTIL_H
#define OIMO_COMMON_MATH_UTIL_H

#include "setting.h"
#include <libdragon.h>
#include <math.h>

#define OIMO_PI         3.14159265358979f
#define OIMO_TWO_PI     6.28318530717958f
#define OIMO_HALF_PI    1.57079632679490f
#define OIMO_TO_RADIANS 0.01745329251994f   // PI / 180
#define OIMO_TO_DEGREES 57.2957795130823f   // 180 / PI

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

static inline OimoScalar oimo_sqrt(OimoScalar x) {
    return sqrtf(x);
}

static inline OimoScalar oimo_sin(OimoScalar x) {
    return fm_sinf(x);
}

static inline OimoScalar oimo_cos(OimoScalar x) {
    return fm_cosf(x);
}

static inline OimoScalar oimo_tan(OimoScalar x) {
    return tanf(x);
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
    return fm_atan2f(y, x);
}

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

// Inverse square root (1 / sqrt(x))
static inline OimoScalar oimo_inv_sqrt(OimoScalar x) {
    if (x <= 0) return 0;
    return 1.0f / oimo_sqrt(x);
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

// Fast inverse square root (Quake III style) - useful for normalizing vectors
// Avoids expensive division and sqrt on N64
// Uses union to avoid strict-aliasing violations
static inline float oimo_fast_inv_sqrt(float x) {
    union { float f; int i; } conv;
    float xhalf = 0.5f * x;
    conv.f = x;
    conv.i = 0x5f375a86 - (conv.i >> 1);  // Magic number for float
    conv.f = conv.f * (1.5f - xhalf * conv.f * conv.f);  // One Newton-Raphson iteration
    return conv.f;
}

// Fast approximate sqrt using fast_inv_sqrt
static inline float oimo_fast_sqrt(float x) {
    if (x <= 0.0f) return 0.0f;
    return x * oimo_fast_inv_sqrt(x);
}

#endif // OIMO_COMMON_MATH_UTIL_H
