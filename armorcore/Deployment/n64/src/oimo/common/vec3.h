#pragma once

#include "setting.h"
#include "math_util.h"

typedef struct OimoVec3 {
    OimoScalar x;
    OimoScalar y;
    OimoScalar z;
} OimoVec3;

static inline OimoVec3 oimo_vec3_zero(void) {
    return (OimoVec3){ 0, 0, 0 };
}

static inline OimoVec3 oimo_vec3(OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ x, y, z };
}

static inline OimoVec3 oimo_vec3_copy(const OimoVec3* v) {
    return (OimoVec3){ v->x, v->y, v->z };
}

// Core operations - by value for ease of chaining
static inline OimoVec3 oimo_vec3_add(OimoVec3 v1, OimoVec3 v2) {
    return (OimoVec3){ v1.x + v2.x, v1.y + v2.y, v1.z + v2.z };
}

static inline OimoVec3 oimo_vec3_add3(OimoVec3 v, OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ v.x + x, v.y + y, v.z + z };
}

static inline OimoVec3 oimo_vec3_add_scaled(OimoVec3 v1, OimoVec3 v2, OimoScalar s) {
    return (OimoVec3){ v1.x + v2.x * s, v1.y + v2.y * s, v1.z + v2.z * s };
}

static inline OimoVec3 oimo_vec3_sub(OimoVec3 v1, OimoVec3 v2) {
    return (OimoVec3){ v1.x - v2.x, v1.y - v2.y, v1.z - v2.z };
}

static inline OimoVec3 oimo_vec3_sub3(OimoVec3 v, OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ v.x - x, v.y - y, v.z - z };
}

static inline OimoVec3 oimo_vec3_scale(OimoVec3 v, OimoScalar s) {
    return (OimoVec3){ v.x * s, v.y * s, v.z * s };
}

static inline OimoVec3 oimo_vec3_scale3(OimoVec3 v, OimoScalar sx, OimoScalar sy, OimoScalar sz) {
    return (OimoVec3){ v.x * sx, v.y * sy, v.z * sz };
}

static inline OimoVec3 oimo_vec3_neg(OimoVec3 v) {
    return (OimoVec3){ -v.x, -v.y, -v.z };
}

static inline OimoScalar oimo_vec3_dot(OimoVec3 v1, OimoVec3 v2) {
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
}

static inline OimoVec3 oimo_vec3_cross(OimoVec3 v1, OimoVec3 v2) {
    return (OimoVec3){
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    };
}

// Squared length: |v|²
static inline OimoScalar oimo_vec3_len_sq(OimoVec3 v) {
    return v.x * v.x + v.y * v.y + v.z * v.z;
}

// Length: |v|
static inline OimoScalar oimo_vec3_len(OimoVec3 v) {
    return oimo_sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Normalize: v / |v| (returns zero vector if length is zero)
static inline OimoVec3 oimo_vec3_normalize(OimoVec3 v) {
    OimoScalar len = oimo_vec3_len(v);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        return (OimoVec3){ v.x * inv_len, v.y * inv_len, v.z * inv_len };
    }
    return (OimoVec3){ 0, 0, 0 };
}

// Normalize with explicit epsilon check
static inline OimoVec3 oimo_vec3_normalize_eps(OimoVec3 v, OimoScalar epsilon) {
    OimoScalar len_sq = oimo_vec3_len_sq(v);
    if (len_sq > epsilon * epsilon) {
        OimoScalar inv_len = 1.0f / oimo_sqrt(len_sq);
        return (OimoVec3){ v.x * inv_len, v.y * inv_len, v.z * inv_len };
    }
    return (OimoVec3){ 0, 0, 0 };
}

// out = v1 + v2
static inline void oimo_vec3_add_to(OimoVec3* out, const OimoVec3* v1, const OimoVec3* v2) {
    out->x = v1->x + v2->x;
    out->y = v1->y + v2->y;
    out->z = v1->z + v2->z;
}

// out = v1 - v2
static inline void oimo_vec3_sub_to(OimoVec3* out, const OimoVec3* v1, const OimoVec3* v2) {
    out->x = v1->x - v2->x;
    out->y = v1->y - v2->y;
    out->z = v1->z - v2->z;
}

// out = v * s
static inline void oimo_vec3_scale_to(OimoVec3* out, const OimoVec3* v, OimoScalar s) {
    out->x = v->x * s;
    out->y = v->y * s;
    out->z = v->z * s;
}

// out = -v
static inline void oimo_vec3_negate_to(OimoVec3* out, const OimoVec3* v) {
    out->x = -v->x;
    out->y = -v->y;
    out->z = -v->z;
}

// out = normalize(v)
static inline void oimo_vec3_normalize_to(OimoVec3* out, const OimoVec3* v) {
    OimoScalar len_sq = v->x * v->x + v->y * v->y + v->z * v->z;
    if (len_sq > 0) {
        OimoScalar inv_len = 1.0f / oimo_sqrt(len_sq);
        out->x = v->x * inv_len;
        out->y = v->y * inv_len;
        out->z = v->z * inv_len;
    } else {
        out->x = out->y = out->z = 0;
    }
}

// out = cross(v1, v2)
static inline void oimo_vec3_cross_to(OimoVec3* out, const OimoVec3* v1, const OimoVec3* v2) {
    // Use temp in case out aliases v1 or v2
    OimoScalar x = v1->y * v2->z - v1->z * v2->y;
    OimoScalar y = v1->z * v2->x - v1->x * v2->z;
    OimoScalar z = v1->x * v2->y - v1->y * v2->x;
    out->x = x;
    out->y = y;
    out->z = z;
}

// v1 = v1 + v2
static inline void oimo_vec3_add_eq(OimoVec3* v1, const OimoVec3* v2) {
    v1->x += v2->x;
    v1->y += v2->y;
    v1->z += v2->z;
}

// v1 = v1 + v2 * s
static inline void oimo_vec3_add_scaled_eq(OimoVec3* v1, const OimoVec3* v2, OimoScalar s) {
    v1->x += v2->x * s;
    v1->y += v2->y * s;
    v1->z += v2->z * s;
}

// v1 = v1 - v2
static inline void oimo_vec3_sub_eq(OimoVec3* v1, const OimoVec3* v2) {
    v1->x -= v2->x;
    v1->y -= v2->y;
    v1->z -= v2->z;
}

// v = v * s
static inline void oimo_vec3_scale_eq(OimoVec3* v, OimoScalar s) {
    v->x *= s;
    v->y *= s;
    v->z *= s;
}

// v = -v
static inline void oimo_vec3_neg_eq(OimoVec3* v) {
    v->x = -v->x;
    v->y = -v->y;
    v->z = -v->z;
}

// Normalize in-place
static inline void oimo_vec3_normalize_eq(OimoVec3* v) {
    OimoScalar len = oimo_vec3_len(*v);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        v->x *= inv_len;
        v->y *= inv_len;
        v->z *= inv_len;
    } else {
        v->x = v->y = v->z = 0;
    }
}

static inline void oimo_vec3_copy_to(OimoVec3* dst, const OimoVec3* src) {
    dst->x = src->x;
    dst->y = src->y;
    dst->z = src->z;
}

// Set components: v = (x, y, z)
static inline void oimo_vec3_set(OimoVec3* v, OimoScalar x, OimoScalar y, OimoScalar z) {
    v->x = x;
    v->y = y;
    v->z = z;
}

// Set to zero: v = (0, 0, 0)
static inline void oimo_vec3_set_zero(OimoVec3* v) {
    v->x = v->y = v->z = 0;
}

// Linear interpolation: lerp(v1, v2, t) = v1 + (v2 - v1) * t
static inline OimoVec3 oimo_vec3_lerp(OimoVec3 v1, OimoVec3 v2, OimoScalar t) {
    return (OimoVec3){
        v1.x + (v2.x - v1.x) * t,
        v1.y + (v2.y - v1.y) * t,
        v1.z + (v2.z - v1.z) * t
    };
}

// Check if approximately zero
static inline int oimo_vec3_is_zero(const OimoVec3* v, OimoScalar epsilon) {
    OimoScalar len_sq = v->x * v->x + v->y * v->y + v->z * v->z;
    return len_sq < epsilon * epsilon;
}

// Distance between two points
static inline OimoScalar oimo_vec3_distance(OimoVec3 v1, OimoVec3 v2) {
    OimoVec3 diff = oimo_vec3_sub(v1, v2);
    return oimo_vec3_len(diff);
}

// Squared distance between two points
static inline OimoScalar oimo_vec3_distance_sq(OimoVec3 v1, OimoVec3 v2) {
    OimoVec3 diff = oimo_vec3_sub(v1, v2);
    return oimo_vec3_len_sq(diff);
}

