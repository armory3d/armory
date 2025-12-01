/**
 * OimoPhysics N64 Port - 3D Vector
 *
 * 3D vector class for physics calculations.
 * Based on OimoPhysics Vec3.hx
 */

#ifndef OIMO_COMMON_VEC3_H
#define OIMO_COMMON_VEC3_H

#include "setting.h"
#include "math_util.h"

// ============================================================================
// Vec3 Type
// ============================================================================
typedef struct OimoVec3 {
    OimoScalar x;
    OimoScalar y;
    OimoScalar z;
} OimoVec3;

// ============================================================================
// Construction
// ============================================================================

// Create a zero vector
static inline OimoVec3 oimo_vec3_zero(void) {
    return (OimoVec3){ 0, 0, 0 };
}

// Create a vector with components
static inline OimoVec3 oimo_vec3(OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ x, y, z };
}

// Create a vector from another vector (copy)
static inline OimoVec3 oimo_vec3_copy(const OimoVec3* v) {
    return (OimoVec3){ v->x, v->y, v->z };
}

// ============================================================================
// Basic Operations
// ============================================================================

// v1 + v2
static inline OimoVec3 oimo_vec3_add(const OimoVec3* v1, const OimoVec3* v2) {
    return (OimoVec3){ v1->x + v2->x, v1->y + v2->y, v1->z + v2->z };
}

// v1 + (vx, vy, vz)
static inline OimoVec3 oimo_vec3_add3(const OimoVec3* v, OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ v->x + x, v->y + y, v->z + z };
}

// v1 + v2 * s
static inline OimoVec3 oimo_vec3_add_scaled(const OimoVec3* v1, const OimoVec3* v2, OimoScalar s) {
    return (OimoVec3){ v1->x + v2->x * s, v1->y + v2->y * s, v1->z + v2->z * s };
}

// v1 - v2
static inline OimoVec3 oimo_vec3_sub(const OimoVec3* v1, const OimoVec3* v2) {
    return (OimoVec3){ v1->x - v2->x, v1->y - v2->y, v1->z - v2->z };
}

// v1 - (vx, vy, vz)
static inline OimoVec3 oimo_vec3_sub3(const OimoVec3* v, OimoScalar x, OimoScalar y, OimoScalar z) {
    return (OimoVec3){ v->x - x, v->y - y, v->z - z };
}

// v * s
static inline OimoVec3 oimo_vec3_scale(const OimoVec3* v, OimoScalar s) {
    return (OimoVec3){ v->x * s, v->y * s, v->z * s };
}

// (v.x * sx, v.y * sy, v.z * sz)
static inline OimoVec3 oimo_vec3_scale3(const OimoVec3* v, OimoScalar sx, OimoScalar sy, OimoScalar sz) {
    return (OimoVec3){ v->x * sx, v->y * sy, v->z * sz };
}

// -v
static inline OimoVec3 oimo_vec3_neg(const OimoVec3* v) {
    return (OimoVec3){ -v->x, -v->y, -v->z };
}

// ============================================================================
// Products
// ============================================================================

// Dot product: v1 · v2
static inline OimoScalar oimo_vec3_dot(const OimoVec3* v1, const OimoVec3* v2) {
    return v1->x * v2->x + v1->y * v2->y + v1->z * v2->z;
}

// Cross product: v1 × v2
static inline OimoVec3 oimo_vec3_cross(const OimoVec3* v1, const OimoVec3* v2) {
    return (OimoVec3){
        v1->y * v2->z - v1->z * v2->y,
        v1->z * v2->x - v1->x * v2->z,
        v1->x * v2->y - v1->y * v2->x
    };
}

// ============================================================================
// Length Operations
// ============================================================================

// Squared length: |v|²
static inline OimoScalar oimo_vec3_len_sq(const OimoVec3* v) {
    return v->x * v->x + v->y * v->y + v->z * v->z;
}

// Length: |v|
static inline OimoScalar oimo_vec3_len(const OimoVec3* v) {
    return oimo_sqrt(v->x * v->x + v->y * v->y + v->z * v->z);
}

// Normalize: v / |v| (returns zero vector if length is zero)
static inline OimoVec3 oimo_vec3_normalize(const OimoVec3* v) {
    OimoScalar len = oimo_vec3_len(v);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        return (OimoVec3){ v->x * inv_len, v->y * inv_len, v->z * inv_len };
    }
    return (OimoVec3){ 0, 0, 0 };
}

// Normalize with explicit epsilon check
static inline OimoVec3 oimo_vec3_normalize_eps(const OimoVec3* v, OimoScalar epsilon) {
    OimoScalar len_sq = oimo_vec3_len_sq(v);
    if (len_sq > epsilon * epsilon) {
        OimoScalar inv_len = 1.0f / oimo_sqrt(len_sq);
        return (OimoVec3){ v->x * inv_len, v->y * inv_len, v->z * inv_len };
    }
    return (OimoVec3){ 0, 0, 0 };
}

// ============================================================================
// Output-Pointer Operations (store result in out)
// These are useful for cleaner code and avoiding temporary variables
// ============================================================================

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
    OimoScalar len = oimo_vec3_len(v);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
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

// ============================================================================
// Mutating Operations (modify v1 in-place)
// ============================================================================

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
    OimoScalar len = oimo_vec3_len(v);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        v->x *= inv_len;
        v->y *= inv_len;
        v->z *= inv_len;
    } else {
        v->x = v->y = v->z = 0;
    }
}

// ============================================================================
// Utility
// ============================================================================

// Copy: dst = src
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
static inline OimoVec3 oimo_vec3_lerp(const OimoVec3* v1, const OimoVec3* v2, OimoScalar t) {
    return (OimoVec3){
        v1->x + (v2->x - v1->x) * t,
        v1->y + (v2->y - v1->y) * t,
        v1->z + (v2->z - v1->z) * t
    };
}

// Check if approximately zero
static inline int oimo_vec3_is_zero(const OimoVec3* v, OimoScalar epsilon) {
    return oimo_vec3_len_sq(v) < epsilon * epsilon;
}

// Distance between two points
static inline OimoScalar oimo_vec3_distance(const OimoVec3* v1, const OimoVec3* v2) {
    OimoVec3 diff = oimo_vec3_sub(v1, v2);
    return oimo_vec3_len(&diff);
}

// Squared distance between two points
static inline OimoScalar oimo_vec3_distance_sq(const OimoVec3* v1, const OimoVec3* v2) {
    OimoVec3 diff = oimo_vec3_sub(v1, v2);
    return oimo_vec3_len_sq(&diff);
}

#endif // OIMO_COMMON_VEC3_H
