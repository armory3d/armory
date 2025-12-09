#pragma once

// triangle_util.h - Shared triangle utility functions for mesh collision

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

// Closest point on line segment
static inline OimoVec3 oimo_closest_point_on_segment(OimoVec3 p, OimoVec3 a, OimoVec3 b) {
    OimoVec3 ab = oimo_vec3_sub(b, a);
    OimoVec3 ap = oimo_vec3_sub(p, a);

    float ab_len_sq = oimo_vec3_dot(ab, ab);
    if (ab_len_sq < 1e-10f) return a;

    float t = oimo_vec3_dot(ap, ab) / ab_len_sq;
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;

    return oimo_vec3_add(a, oimo_vec3_scale(ab, t));
}

// Closest points between two line segments
static inline void oimo_closest_points_segments(
    OimoVec3 p1, OimoVec3 p2, OimoVec3 p3, OimoVec3 p4,
    OimoVec3* closest1, OimoVec3* closest2
) {
    OimoVec3 d1 = oimo_vec3_sub(p2, p1);
    OimoVec3 d2 = oimo_vec3_sub(p4, p3);
    OimoVec3 r = oimo_vec3_sub(p1, p3);

    float a = oimo_vec3_dot(d1, d1);
    float e = oimo_vec3_dot(d2, d2);
    float f = oimo_vec3_dot(d2, r);

    float s, t;

    if (a <= 1e-6f && e <= 1e-6f) {
        *closest1 = p1;
        *closest2 = p3;
        return;
    }

    if (a <= 1e-6f) {
        s = 0.0f;
        t = f / e;
        if (t < 0.0f) t = 0.0f;
        if (t > 1.0f) t = 1.0f;
    } else {
        float c = oimo_vec3_dot(d1, r);
        if (e <= 1e-6f) {
            t = 0.0f;
            s = -c / a;
            if (s < 0.0f) s = 0.0f;
            if (s > 1.0f) s = 1.0f;
        } else {
            float b = oimo_vec3_dot(d1, d2);
            float denom = a * e - b * b;

            if (denom != 0.0f) {
                s = (b * f - c * e) / denom;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            } else {
                s = 0.0f;
            }

            t = (b * s + f) / e;

            if (t < 0.0f) {
                t = 0.0f;
                s = -c / a;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            } else if (t > 1.0f) {
                t = 1.0f;
                s = (b - c) / a;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            }
        }
    }

    *closest1 = oimo_vec3_add(p1, oimo_vec3_scale(d1, s));
    *closest2 = oimo_vec3_add(p3, oimo_vec3_scale(d2, t));
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
