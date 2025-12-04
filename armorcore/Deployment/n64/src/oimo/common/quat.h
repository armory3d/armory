#pragma once

#include "setting.h"
#include "math_util.h"
#include "vec3.h"
#include "mat3.h"

typedef struct OimoQuat {
    OimoScalar x, y, z, w;
} OimoQuat;

static inline OimoQuat oimo_quat_identity(void) {
    return (OimoQuat){ 0, 0, 0, 1 };
}

static inline OimoQuat oimo_quat(OimoScalar x, OimoScalar y, OimoScalar z, OimoScalar w) {
    return (OimoQuat){ x, y, z, w };
}

static inline OimoQuat oimo_quat_copy(const OimoQuat* q) {
    return (OimoQuat){ q->x, q->y, q->z, q->w };
}

static inline OimoQuat oimo_quat_add(const OimoQuat* q1, const OimoQuat* q2) {
    return (OimoQuat){ q1->x + q2->x, q1->y + q2->y, q1->z + q2->z, q1->w + q2->w };
}

static inline OimoQuat oimo_quat_sub(const OimoQuat* q1, const OimoQuat* q2) {
    return (OimoQuat){ q1->x - q2->x, q1->y - q2->y, q1->z - q2->z, q1->w - q2->w };
}

static inline OimoQuat oimo_quat_scale(const OimoQuat* q, OimoScalar s) {
    return (OimoQuat){ q->x * s, q->y * s, q->z * s, q->w * s };
}

static inline OimoQuat oimo_quat_neg(const OimoQuat* q) {
    return (OimoQuat){ -q->x, -q->y, -q->z, -q->w };
}

static inline OimoQuat oimo_quat_conjugate(const OimoQuat* q) {
    return (OimoQuat){ -q->x, -q->y, -q->z, q->w };
}

static inline OimoScalar oimo_quat_dot(const OimoQuat* q1, const OimoQuat* q2) {
    return q1->x * q2->x + q1->y * q2->y + q1->z * q2->z + q1->w * q2->w;
}

static inline OimoQuat oimo_quat_mul(const OimoQuat* q1, const OimoQuat* q2) {
    return (OimoQuat){
        q1->w * q2->x + q1->x * q2->w + q1->y * q2->z - q1->z * q2->y,
        q1->w * q2->y - q1->x * q2->z + q1->y * q2->w + q1->z * q2->x,
        q1->w * q2->z + q1->x * q2->y - q1->y * q2->x + q1->z * q2->w,
        q1->w * q2->w - q1->x * q2->x - q1->y * q2->y - q1->z * q2->z
    };
}

// Squared length: |q|²
static inline OimoScalar oimo_quat_len_sq(const OimoQuat* q) {
    return q->x * q->x + q->y * q->y + q->z * q->z + q->w * q->w;
}

// Length: |q|
static inline OimoScalar oimo_quat_len(const OimoQuat* q) {
    return oimo_sqrt(q->x * q->x + q->y * q->y + q->z * q->z + q->w * q->w);
}

// Normalize: q / |q| (returns identity if length is zero)
static inline OimoQuat oimo_quat_normalize(const OimoQuat* q) {
    OimoScalar len = oimo_quat_len(q);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        return (OimoQuat){ q->x * inv_len, q->y * inv_len, q->z * inv_len, q->w * inv_len };
    }
    return (OimoQuat){ 0, 0, 0, 1 };
}

static inline OimoMat3 oimo_quat_to_mat3(const OimoQuat* q) {
    OimoScalar x = q->x, y = q->y, z = q->z, w = q->w;
    OimoScalar x2 = 2 * x, y2 = 2 * y, z2 = 2 * z;
    OimoScalar xx = x * x2, yy = y * y2, zz = z * z2;
    OimoScalar xy = x * y2, yz = y * z2, xz = x * z2;
    OimoScalar wx = w * x2, wy = w * y2, wz = w * z2;

    return (OimoMat3){
        1 - yy - zz, xy - wz,     xz + wy,
        xy + wz,     1 - xx - zz, yz - wx,
        xz - wy,     yz + wx,     1 - xx - yy
    };
}

// Convert rotation matrix to quaternion
// Matrix must be a rotation matrix (orthogonal with determinant 1)
static inline OimoQuat oimo_mat3_to_quat(const OimoMat3* m) {
    OimoScalar e00 = m->e00, e11 = m->e11, e22 = m->e22;
    OimoScalar t = e00 + e11 + e22;
    OimoScalar s;
    OimoQuat q;

    if (t > 0) {
        s = oimo_sqrt(t + 1);
        q.w = 0.5f * s;
        s = 0.5f / s;
        q.x = (m->e21 - m->e12) * s;
        q.y = (m->e02 - m->e20) * s;
        q.z = (m->e10 - m->e01) * s;
    } else if (e00 >= e11 && e00 >= e22) {
        // e00 is the largest diagonal element
        s = oimo_sqrt(e00 - e11 - e22 + 1);
        q.x = 0.5f * s;
        s = 0.5f / s;
        q.y = (m->e01 + m->e10) * s;
        q.z = (m->e02 + m->e20) * s;
        q.w = (m->e21 - m->e12) * s;
    } else if (e11 >= e22) {
        // e11 is the largest diagonal element
        s = oimo_sqrt(e11 - e22 - e00 + 1);
        q.y = 0.5f * s;
        s = 0.5f / s;
        q.x = (m->e01 + m->e10) * s;
        q.z = (m->e12 + m->e21) * s;
        q.w = (m->e02 - m->e20) * s;
    } else {
        // e22 is the largest diagonal element
        s = oimo_sqrt(e22 - e00 - e11 + 1);
        q.z = 0.5f * s;
        s = 0.5f / s;
        q.x = (m->e02 + m->e20) * s;
        q.y = (m->e12 + m->e21) * s;
        q.w = (m->e10 - m->e01) * s;
    }

    return q;
}

// Set Mat3 from quaternion (in-place)
static inline void oimo_mat3_from_quat(OimoMat3* m, const OimoQuat* q) {
    OimoScalar x = q->x, y = q->y, z = q->z, w = q->w;
    OimoScalar x2 = 2 * x, y2 = 2 * y, z2 = 2 * z;
    OimoScalar xx = x * x2, yy = y * y2, zz = z * z2;
    OimoScalar xy = x * y2, yz = y * z2, xz = x * z2;
    OimoScalar wx = w * x2, wy = w * y2, wz = w * z2;

    m->e00 = 1 - yy - zz; m->e01 = xy - wz;     m->e02 = xz + wy;
    m->e10 = xy + wz;     m->e11 = 1 - xx - zz; m->e12 = yz - wx;
    m->e20 = xz - wy;     m->e21 = yz + wx;     m->e22 = 1 - xx - yy;
}

static inline OimoQuat oimo_quat_from_axis_angle(const OimoVec3* axis, OimoScalar angle) {
    OimoScalar half_angle = angle * 0.5f;
    OimoScalar s = oimo_sin(half_angle);
    return (OimoQuat){
        axis->x * s,
        axis->y * s,
        axis->z * s,
        oimo_cos(half_angle)
    };
}

// Extract axis-angle from quaternion
// angle is returned, axis is written to out_axis
static inline OimoScalar oimo_quat_to_axis_angle(const OimoQuat* q, OimoVec3* out_axis) {
    OimoScalar sin_half_sq = q->x * q->x + q->y * q->y + q->z * q->z;

    if (sin_half_sq <= OIMO_EPSILON * OIMO_EPSILON) {
        // Near identity, return arbitrary axis
        out_axis->x = 1;
        out_axis->y = 0;
        out_axis->z = 0;
        return 0;
    }

    OimoScalar sin_half = oimo_sqrt(sin_half_sq);
    OimoScalar inv_sin = 1.0f / sin_half;
    out_axis->x = q->x * inv_sin;
    out_axis->y = q->y * inv_sin;
    out_axis->z = q->z * inv_sin;

    return 2.0f * oimo_atan2(sin_half, q->w);
}

static inline OimoQuat oimo_quat_set_arc(const OimoVec3* v1, const OimoVec3* v2) {
    OimoScalar d = oimo_vec3_dot(*v1, *v2);
    OimoQuat q;

    q.w = oimo_sqrt((1.0f + d) * 0.5f);

    if (q.w < OIMO_EPSILON) {
        // Vectors are opposite, need perpendicular axis
        OimoScalar x2 = v1->x * v1->x;
        OimoScalar y2 = v1->y * v1->y;
        OimoScalar z2 = v1->z * v1->z;
        OimoScalar inv_len;

        if (x2 <= y2 && x2 <= z2) {
            // x is smallest, use x-axis
            inv_len = 1.0f / oimo_sqrt(y2 + z2);
            q.x = 0;
            q.y = v1->z * inv_len;
            q.z = -v1->y * inv_len;
        } else if (y2 <= z2) {
            // y is smallest, use y-axis
            inv_len = 1.0f / oimo_sqrt(z2 + x2);
            q.y = 0;
            q.z = v1->x * inv_len;
            q.x = -v1->z * inv_len;
        } else {
            // z is smallest, use z-axis
            inv_len = 1.0f / oimo_sqrt(x2 + y2);
            q.z = 0;
            q.x = v1->y * inv_len;
            q.y = -v1->x * inv_len;
        }
        q.w = 0;
        return q;
    }

    // Normal case: sin(theta/2) / sin(theta) = 1 / (2 * cos(theta/2))
    OimoScalar s = 0.5f / q.w;
    OimoVec3 cross = oimo_vec3_cross(*v1, *v2);
    q.x = cross.x * s;
    q.y = cross.y * s;
    q.z = cross.z * s;

    return q;
}

static inline OimoQuat oimo_quat_slerp(const OimoQuat* q1, const OimoQuat* q2, OimoScalar t) {
    OimoScalar qx = q2->x, qy = q2->y, qz = q2->z, qw = q2->w;
    OimoScalar d = oimo_quat_dot(q1, q2);

    // If dot is negative, negate one quaternion to take shorter path
    if (d < 0) {
        d = -d;
        qx = -qx;
        qy = -qy;
        qz = -qz;
        qw = -qw;
    }

    // If quaternions are very close, use linear interpolation
    if (d > 1.0f - OIMO_EPSILON) {
        OimoQuat result = {
            q1->x + (qx - q1->x) * t,
            q1->y + (qy - q1->y) * t,
            q1->z + (qz - q1->z) * t,
            q1->w + (qw - q1->w) * t
        };
        return oimo_quat_normalize(&result);
    }

    // Target angle
    OimoScalar theta = t * oimo_acos(d);

    // Make q orthogonal to q1
    qx -= q1->x * d;
    qy -= q1->y * d;
    qz -= q1->z * d;
    qw -= q1->w * d;
    OimoScalar inv_len = 1.0f / oimo_sqrt(qx * qx + qy * qy + qz * qz + qw * qw);
    qx *= inv_len;
    qy *= inv_len;
    qz *= inv_len;
    qw *= inv_len;

    // Mix them
    OimoScalar sin_theta = oimo_sin(theta);
    OimoScalar cos_theta = oimo_cos(theta);

    return (OimoQuat){
        q1->x * cos_theta + qx * sin_theta,
        q1->y * cos_theta + qy * sin_theta,
        q1->z * cos_theta + qz * sin_theta,
        q1->w * cos_theta + qw * sin_theta
    };
}

static inline void oimo_quat_set_identity(OimoQuat* q) {
    q->x = 0; q->y = 0; q->z = 0; q->w = 1;
}

// Copy from another quaternion
static inline void oimo_quat_copy_to(OimoQuat* dst, const OimoQuat* src) {
    dst->x = src->x;
    dst->y = src->y;
    dst->z = src->z;
    dst->w = src->w;
}

// Normalize in-place
static inline void oimo_quat_normalize_eq(OimoQuat* q) {
    OimoScalar len = oimo_quat_len(q);
    if (len > 0) {
        OimoScalar inv_len = 1.0f / len;
        q->x *= inv_len;
        q->y *= inv_len;
        q->z *= inv_len;
        q->w *= inv_len;
    } else {
        q->x = 0; q->y = 0; q->z = 0; q->w = 1;
    }
}

static inline OimoVec3 oimo_quat_rotate_vec3(const OimoQuat* q, const OimoVec3* v) {
    // Using the formula: v' = v + 2*w*(qv × v) + 2*(qv × (qv × v))
    // where qv = (x, y, z) is the vector part of quaternion
    OimoVec3 qv = { q->x, q->y, q->z };
    OimoVec3 uv = oimo_vec3_cross(qv, *v);
    OimoVec3 uuv = oimo_vec3_cross(qv, uv);

    return (OimoVec3){
        v->x + 2.0f * (q->w * uv.x + uuv.x),
        v->y + 2.0f * (q->w * uv.y + uuv.y),
        v->z + 2.0f * (q->w * uv.z + uuv.z)
    };
}

