#ifndef OIMO_COMMON_MAT3_H
#define OIMO_COMMON_MAT3_H

#include "setting.h"
#include "math_util.h"
#include "vec3.h"

struct OimoQuat;

typedef struct OimoMat3 {
    OimoScalar e00, e01, e02;
    OimoScalar e10, e11, e12;
    OimoScalar e20, e21, e22;
} OimoMat3;

static inline OimoMat3 oimo_mat3_identity(void) {
    return (OimoMat3){
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    };
}

// Create zero matrix
static inline OimoMat3 oimo_mat3_zero(void) {
    return (OimoMat3){
        0, 0, 0,
        0, 0, 0,
        0, 0, 0
    };
}

// Create matrix with explicit elements
static inline OimoMat3 oimo_mat3(
    OimoScalar e00, OimoScalar e01, OimoScalar e02,
    OimoScalar e10, OimoScalar e11, OimoScalar e12,
    OimoScalar e20, OimoScalar e21, OimoScalar e22
) {
    return (OimoMat3){
        e00, e01, e02,
        e10, e11, e12,
        e20, e21, e22
    };
}

// Copy matrix
static inline OimoMat3 oimo_mat3_copy(const OimoMat3* m) {
    return (OimoMat3){
        m->e00, m->e01, m->e02,
        m->e10, m->e11, m->e12,
        m->e20, m->e21, m->e22
    };
}

static inline OimoMat3 oimo_mat3_add(const OimoMat3* m1, const OimoMat3* m2) {
    return (OimoMat3){
        m1->e00 + m2->e00, m1->e01 + m2->e01, m1->e02 + m2->e02,
        m1->e10 + m2->e10, m1->e11 + m2->e11, m1->e12 + m2->e12,
        m1->e20 + m2->e20, m1->e21 + m2->e21, m1->e22 + m2->e22
    };
}

// m1 - m2
static inline OimoMat3 oimo_mat3_sub(const OimoMat3* m1, const OimoMat3* m2) {
    return (OimoMat3){
        m1->e00 - m2->e00, m1->e01 - m2->e01, m1->e02 - m2->e02,
        m1->e10 - m2->e10, m1->e11 - m2->e11, m1->e12 - m2->e12,
        m1->e20 - m2->e20, m1->e21 - m2->e21, m1->e22 - m2->e22
    };
}

// m * s (scalar multiplication)
static inline OimoMat3 oimo_mat3_scale(const OimoMat3* m, OimoScalar s) {
    return (OimoMat3){
        m->e00 * s, m->e01 * s, m->e02 * s,
        m->e10 * s, m->e11 * s, m->e12 * s,
        m->e20 * s, m->e21 * s, m->e22 * s
    };
}

// m1 * m2 (matrix multiplication)
static inline OimoMat3 oimo_mat3_mul(const OimoMat3* m1, const OimoMat3* m2) {
    return (OimoMat3){
        m1->e00 * m2->e00 + m1->e01 * m2->e10 + m1->e02 * m2->e20,
        m1->e00 * m2->e01 + m1->e01 * m2->e11 + m1->e02 * m2->e21,
        m1->e00 * m2->e02 + m1->e01 * m2->e12 + m1->e02 * m2->e22,

        m1->e10 * m2->e00 + m1->e11 * m2->e10 + m1->e12 * m2->e20,
        m1->e10 * m2->e01 + m1->e11 * m2->e11 + m1->e12 * m2->e21,
        m1->e10 * m2->e02 + m1->e11 * m2->e12 + m1->e12 * m2->e22,

        m1->e20 * m2->e00 + m1->e21 * m2->e10 + m1->e22 * m2->e20,
        m1->e20 * m2->e01 + m1->e21 * m2->e11 + m1->e22 * m2->e21,
        m1->e20 * m2->e02 + m1->e21 * m2->e12 + m1->e22 * m2->e22
    };
}

static inline OimoVec3 oimo_mat3_mul_vec3(const OimoMat3* m, OimoVec3 v) {
    return (OimoVec3){
        m->e00 * v.x + m->e01 * v.y + m->e02 * v.z,
        m->e10 * v.x + m->e11 * v.y + m->e12 * v.z,
        m->e20 * v.x + m->e21 * v.y + m->e22 * v.z
    };
}

// m^T * v (transform vector by transposed matrix)
static inline OimoVec3 oimo_mat3_tmul_vec3(const OimoMat3* m, OimoVec3 v) {
    return (OimoVec3){
        m->e00 * v.x + m->e10 * v.y + m->e20 * v.z,
        m->e01 * v.x + m->e11 * v.y + m->e21 * v.z,
        m->e02 * v.x + m->e12 * v.y + m->e22 * v.z
    };
}

static inline OimoVec3 oimo_mat3_get_row(const OimoMat3* m, int i) {
    switch (i) {
        case 0: return (OimoVec3){ m->e00, m->e01, m->e02 };
        case 1: return (OimoVec3){ m->e10, m->e11, m->e12 };
        case 2: return (OimoVec3){ m->e20, m->e21, m->e22 };
        default: return (OimoVec3){ 0, 0, 0 };
    }
}

// Get column i as vector
static inline OimoVec3 oimo_mat3_get_col(const OimoMat3* m, int i) {
    switch (i) {
        case 0: return (OimoVec3){ m->e00, m->e10, m->e20 };
        case 1: return (OimoVec3){ m->e01, m->e11, m->e21 };
        case 2: return (OimoVec3){ m->e02, m->e12, m->e22 };
        default: return (OimoVec3){ 0, 0, 0 };
    }
}

// Set row i from vector
static inline void oimo_mat3_set_row(OimoMat3* m, int i, const OimoVec3* v) {
    switch (i) {
        case 0: m->e00 = v->x; m->e01 = v->y; m->e02 = v->z; break;
        case 1: m->e10 = v->x; m->e11 = v->y; m->e12 = v->z; break;
        case 2: m->e20 = v->x; m->e21 = v->y; m->e22 = v->z; break;
    }
}

// Set column i from vector
static inline void oimo_mat3_set_col(OimoMat3* m, int i, const OimoVec3* v) {
    switch (i) {
        case 0: m->e00 = v->x; m->e10 = v->y; m->e20 = v->z; break;
        case 1: m->e01 = v->x; m->e11 = v->y; m->e21 = v->z; break;
        case 2: m->e02 = v->x; m->e12 = v->y; m->e22 = v->z; break;
    }
}

// Create matrix from column vectors
static inline OimoMat3 oimo_mat3_from_cols(const OimoVec3* c0, const OimoVec3* c1, const OimoVec3* c2) {
    return (OimoMat3){
        c0->x, c1->x, c2->x,
        c0->y, c1->y, c2->y,
        c0->z, c1->z, c2->z
    };
}

// Create matrix from row vectors
static inline OimoMat3 oimo_mat3_from_rows(const OimoVec3* r0, const OimoVec3* r1, const OimoVec3* r2) {
    return (OimoMat3){
        r0->x, r0->y, r0->z,
        r1->x, r1->y, r1->z,
        r2->x, r2->y, r2->z
    };
}

static inline OimoMat3 oimo_mat3_transpose(const OimoMat3* m) {
    return (OimoMat3){
        m->e00, m->e10, m->e20,
        m->e01, m->e11, m->e21,
        m->e02, m->e12, m->e22
    };
}

// Determinant
static inline OimoScalar oimo_mat3_determinant(const OimoMat3* m) {
    return m->e00 * (m->e11 * m->e22 - m->e12 * m->e21)
         - m->e01 * (m->e10 * m->e22 - m->e12 * m->e20)
         + m->e02 * (m->e10 * m->e21 - m->e11 * m->e20);
}

// Trace
static inline OimoScalar oimo_mat3_trace(const OimoMat3* m) {
    return m->e00 + m->e11 + m->e22;
}

// Inverse (returns zero matrix if determinant is zero)
static inline OimoMat3 oimo_mat3_inverse(const OimoMat3* m) {
    OimoScalar d00 = m->e11 * m->e22 - m->e12 * m->e21;
    OimoScalar d01 = m->e10 * m->e22 - m->e12 * m->e20;
    OimoScalar d02 = m->e10 * m->e21 - m->e11 * m->e20;
    OimoScalar d10 = m->e01 * m->e22 - m->e02 * m->e21;
    OimoScalar d11 = m->e00 * m->e22 - m->e02 * m->e20;
    OimoScalar d12 = m->e00 * m->e21 - m->e01 * m->e20;
    OimoScalar d20 = m->e01 * m->e12 - m->e02 * m->e11;
    OimoScalar d21 = m->e00 * m->e12 - m->e02 * m->e10;
    OimoScalar d22 = m->e00 * m->e11 - m->e01 * m->e10;

    OimoScalar det = m->e00 * d00 - m->e01 * d01 + m->e02 * d02;
    OimoScalar inv_det = (oimo_abs(det) > OIMO_EPSILON) ? (1.0f / det) : 0;

    return (OimoMat3){
         d00 * inv_det, -d10 * inv_det,  d20 * inv_det,
        -d01 * inv_det,  d11 * inv_det, -d21 * inv_det,
         d02 * inv_det, -d12 * inv_det,  d22 * inv_det
    };
}

static inline OimoMat3 oimo_mat3_prepend_scale(const OimoMat3* m, OimoScalar sx, OimoScalar sy, OimoScalar sz) {
    return (OimoMat3){
        m->e00 * sx, m->e01 * sx, m->e02 * sx,
        m->e10 * sy, m->e11 * sy, m->e12 * sy,
        m->e20 * sz, m->e21 * sz, m->e22 * sz
    };
}

// append scale: m * scaling_matrix
static inline OimoMat3 oimo_mat3_append_scale(const OimoMat3* m, OimoScalar sx, OimoScalar sy, OimoScalar sz) {
    return (OimoMat3){
        m->e00 * sx, m->e01 * sy, m->e02 * sz,
        m->e10 * sx, m->e11 * sy, m->e12 * sz,
        m->e20 * sx, m->e21 * sy, m->e22 * sz
    };
}

static inline OimoMat3 oimo_mat3_from_axis_angle(OimoScalar rad, OimoScalar ax, OimoScalar ay, OimoScalar az) {
    OimoScalar s = oimo_sin(rad);
    OimoScalar c = oimo_cos(rad);
    OimoScalar c1 = 1.0f - c;

    return (OimoMat3){
        ax * ax * c1 + c,      ax * ay * c1 - az * s, ax * az * c1 + ay * s,
        ay * ax * c1 + az * s, ay * ay * c1 + c,      ay * az * c1 - ax * s,
        az * ax * c1 - ay * s, az * ay * c1 + ax * s, az * az * c1 + c
    };
}

// Create rotation matrix from Euler angles (XYZ order)
static inline OimoMat3 oimo_mat3_from_euler_xyz(OimoScalar rx, OimoScalar ry, OimoScalar rz) {
    OimoScalar sx = oimo_sin(rx), cx = oimo_cos(rx);
    OimoScalar sy = oimo_sin(ry), cy = oimo_cos(ry);
    OimoScalar sz = oimo_sin(rz), cz = oimo_cos(rz);

    return (OimoMat3){
        cy * cz,                -cy * sz,                 sy,
        cx * sz + cz * sx * sy,  cx * cz - sx * sy * sz, -cy * sx,
        sx * sz - cx * cz * sy,  cz * sx + cx * sy * sz,  cx * cy
    };
}

static inline void oimo_mat3_set_identity(OimoMat3* m) {
    m->e00 = 1; m->e01 = 0; m->e02 = 0;
    m->e10 = 0; m->e11 = 1; m->e12 = 0;
    m->e20 = 0; m->e21 = 0; m->e22 = 1;
}

// Copy from another matrix
static inline void oimo_mat3_copy_to(OimoMat3* dst, const OimoMat3* src) {
    dst->e00 = src->e00; dst->e01 = src->e01; dst->e02 = src->e02;
    dst->e10 = src->e10; dst->e11 = src->e11; dst->e12 = src->e12;
    dst->e20 = src->e20; dst->e21 = src->e21; dst->e22 = src->e22;
}

// m1 = m1 + m2
static inline void oimo_mat3_add_eq(OimoMat3* m1, const OimoMat3* m2) {
    m1->e00 += m2->e00; m1->e01 += m2->e01; m1->e02 += m2->e02;
    m1->e10 += m2->e10; m1->e11 += m2->e11; m1->e12 += m2->e12;
    m1->e20 += m2->e20; m1->e21 += m2->e21; m1->e22 += m2->e22;
}

// m = m * s
static inline void oimo_mat3_scale_eq(OimoMat3* m, OimoScalar s) {
    m->e00 *= s; m->e01 *= s; m->e02 *= s;
    m->e10 *= s; m->e11 *= s; m->e12 *= s;
    m->e20 *= s; m->e21 *= s; m->e22 *= s;
}

// Transpose in-place
static inline void oimo_mat3_transpose_eq(OimoMat3* m) {
    OimoScalar t;
    t = m->e01; m->e01 = m->e10; m->e10 = t;
    t = m->e02; m->e02 = m->e20; m->e20 = t;
    t = m->e12; m->e12 = m->e21; m->e21 = t;
}

#endif // OIMO_COMMON_MAT3_H
