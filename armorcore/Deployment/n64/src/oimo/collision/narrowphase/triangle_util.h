// triangle_util.h - Shared triangle utility functions for mesh collision
#ifndef OIMO_COLLISION_NARROWPHASE_TRIANGLE_UTIL_H
#define OIMO_COLLISION_NARROWPHASE_TRIANGLE_UTIL_H

#include "../../common/vec3.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

// Quick signed distance from point to triangle plane
// Returns positive if on normal side, negative if behind
static inline float oimo_point_plane_distance(
    const OimoVec3* p,
    const OimoVec3* tri_v0,
    const OimoVec3* tri_normal
) {
    OimoVec3 to_point = oimo_vec3_sub(*p, *tri_v0);
    return oimo_vec3_dot(to_point, *tri_normal);
}

// Find closest point on triangle to a point (Barycentric method)
static inline OimoVec3 oimo_closest_point_on_triangle(
    const OimoVec3* p,
    const OimoVec3* a,
    const OimoVec3* b,
    const OimoVec3* c
) {
    // Check if P in vertex region outside A
    OimoVec3 ab = oimo_vec3_sub(*b, *a);
    OimoVec3 ac = oimo_vec3_sub(*c, *a);
    OimoVec3 ap = oimo_vec3_sub(*p, *a);

    float d1 = oimo_vec3_dot(ab, ap);
    float d2 = oimo_vec3_dot(ac, ap);
    if (d1 <= 0.0f && d2 <= 0.0f) return *a;  // barycentric coordinates (1,0,0)

    // Check if P in vertex region outside B
    OimoVec3 bp = oimo_vec3_sub(*p, *b);
    float d3 = oimo_vec3_dot(ab, bp);
    float d4 = oimo_vec3_dot(ac, bp);
    if (d3 >= 0.0f && d4 <= d3) return *b;  // barycentric coordinates (0,1,0)

    // Check if P in edge region of AB
    float vc = d1 * d4 - d3 * d2;
    if (vc <= 0.0f && d1 >= 0.0f && d3 <= 0.0f) {
        float v = d1 / (d1 - d3);
        OimoVec3 scaled = oimo_vec3_scale(ab, v);
        return oimo_vec3_add(*a, scaled);
    }

    // Check if P in vertex region outside C
    OimoVec3 cp = oimo_vec3_sub(*p, *c);
    float d5 = oimo_vec3_dot(ab, cp);
    float d6 = oimo_vec3_dot(ac, cp);
    if (d6 >= 0.0f && d5 <= d6) return *c;  // barycentric coordinates (0,0,1)

    // Check if P in edge region of AC
    float vb = d5 * d2 - d1 * d6;
    if (vb <= 0.0f && d2 >= 0.0f && d6 <= 0.0f) {
        float w = d2 / (d2 - d6);
        OimoVec3 scaled = oimo_vec3_scale(ac, w);
        return oimo_vec3_add(*a, scaled);
    }

    // Check if P in edge region of BC
    float va = d3 * d6 - d5 * d4;
    if (va <= 0.0f && (d4 - d3) >= 0.0f && (d5 - d6) >= 0.0f) {
        float w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        OimoVec3 bc = oimo_vec3_sub(*c, *b);
        OimoVec3 scaled = oimo_vec3_scale(bc, w);
        return oimo_vec3_add(*b, scaled);
    }

    // P inside face region
    float denom = 1.0f / (va + vb + vc);
    float v = vb * denom;
    float w = vc * denom;

    OimoVec3 ab_scaled = oimo_vec3_scale(ab, v);
    OimoVec3 ac_scaled = oimo_vec3_scale(ac, w);
    OimoVec3 result = oimo_vec3_add(*a, ab_scaled);
    return oimo_vec3_add(result, ac_scaled);
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_TRIANGLE_UTIL_H
