#include "Mat3.h"
#include <math.h>

Mat3 mat3_new(float e00, float e01, float e02,
              float e10, float e11, float e12,
              float e20, float e21, float e22) {
    Mat3 m;
    m.m[0][0] = e00; m.m[0][1] = e01; m.m[0][2] = e02;
    m.m[1][0] = e10; m.m[1][1] = e11; m.m[1][2] = e12;
    m.m[2][0] = e20; m.m[2][1] = e21; m.m[2][2] = e22;
    return m;
}

void mat3_init(Mat3* m, float e00, float e01, float e02,
               float e10, float e11, float e12,
               float e20, float e21, float e22) {
    m->m[0][0] = e00; m->m[0][1] = e01; m->m[0][2] = e02;
    m->m[1][0] = e10; m->m[1][1] = e11; m->m[1][2] = e12;
    m->m[2][0] = e20; m->m[2][1] = e21; m->m[2][2] = e22;
}

Mat3 mat3_identity(void) {
    return (Mat3){{ {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }};
}

void mat3_add(Mat3* m1, const Mat3* m2) {
    m1->m[0][0] += m2->m[0][0]; m1->m[0][1] += m2->m[0][1]; m1->m[0][2] += m2->m[0][2];
    m1->m[1][0] += m2->m[1][0]; m1->m[1][1] += m2->m[1][1]; m1->m[1][2] += m2->m[1][2];
    m1->m[2][0] += m2->m[2][0]; m1->m[2][1] += m2->m[2][1]; m1->m[2][2] += m2->m[2][2];
}

void mat3_sub(Mat3* m1, const Mat3* m2) {
    m1->m[0][0] -= m2->m[0][0]; m1->m[0][1] -= m2->m[0][1]; m1->m[0][2] -= m2->m[0][2];
    m1->m[1][0] -= m2->m[1][0]; m1->m[1][1] -= m2->m[1][1]; m1->m[1][2] -= m2->m[1][2];
    m1->m[2][0] -= m2->m[2][0]; m1->m[2][1] -= m2->m[2][1]; m1->m[2][2] -= m2->m[2][2];
}

void mat3_scale(Mat3* m, float s) {
    m->m[0][0] *= s; m->m[0][1] *= s; m->m[0][2] *= s;
    m->m[1][0] *= s; m->m[1][1] *= s; m->m[1][2] *= s;
    m->m[2][0] *= s; m->m[2][1] *= s; m->m[2][2] *= s;
}

void mat3_mul(Mat3* m1, const Mat3* m2) {
    float a00 = m1->m[0][0], a01 = m1->m[0][1], a02 = m1->m[0][2];
    float a10 = m1->m[1][0], a11 = m1->m[1][1], a12 = m1->m[1][2];
    float a20 = m1->m[2][0], a21 = m1->m[2][1], a22 = m1->m[2][2];
    float b00 = m2->m[0][0], b01 = m2->m[0][1], b02 = m2->m[0][2];
    float b10 = m2->m[1][0], b11 = m2->m[1][1], b12 = m2->m[1][2];
    float b20 = m2->m[2][0], b21 = m2->m[2][1], b22 = m2->m[2][2];

    m1->m[0][0] = a00*b00 + a01*b10 + a02*b20;
    m1->m[0][1] = a00*b01 + a01*b11 + a02*b21;
    m1->m[0][2] = a00*b02 + a01*b12 + a02*b22;
    m1->m[1][0] = a10*b00 + a11*b10 + a12*b20;
    m1->m[1][1] = a10*b01 + a11*b11 + a12*b21;
    m1->m[1][2] = a10*b02 + a11*b12 + a12*b22;
    m1->m[2][0] = a20*b00 + a21*b10 + a22*b20;
    m1->m[2][1] = a20*b01 + a21*b11 + a22*b21;
    m1->m[2][2] = a20*b02 + a21*b12 + a22*b22;
}

void mat3_mul_out(Mat3* out, const Mat3* a, const Mat3* b) {
    float a00 = a->m[0][0], a01 = a->m[0][1], a02 = a->m[0][2];
    float a10 = a->m[1][0], a11 = a->m[1][1], a12 = a->m[1][2];
    float a20 = a->m[2][0], a21 = a->m[2][1], a22 = a->m[2][2];
    float b00 = b->m[0][0], b01 = b->m[0][1], b02 = b->m[0][2];
    float b10 = b->m[1][0], b11 = b->m[1][1], b12 = b->m[1][2];
    float b20 = b->m[2][0], b21 = b->m[2][1], b22 = b->m[2][2];

    out->m[0][0] = a00*b00 + a01*b10 + a02*b20;
    out->m[0][1] = a00*b01 + a01*b11 + a02*b21;
    out->m[0][2] = a00*b02 + a01*b12 + a02*b22;
    out->m[1][0] = a10*b00 + a11*b10 + a12*b20;
    out->m[1][1] = a10*b01 + a11*b11 + a12*b21;
    out->m[1][2] = a10*b02 + a11*b12 + a12*b22;
    out->m[2][0] = a20*b00 + a21*b10 + a22*b20;
    out->m[2][1] = a20*b01 + a21*b11 + a22*b21;
    out->m[2][2] = a20*b02 + a21*b12 + a22*b22;
}

void mat3_transpose(Mat3* m) {
    float t;
    t = m->m[0][1]; m->m[0][1] = m->m[1][0]; m->m[1][0] = t;
    t = m->m[0][2]; m->m[0][2] = m->m[2][0]; m->m[2][0] = t;
    t = m->m[1][2]; m->m[1][2] = m->m[2][1]; m->m[2][1] = t;
}

Mat3 mat3_transposed(const Mat3* m) {
    return mat3_new(
        m->m[0][0], m->m[1][0], m->m[2][0],
        m->m[0][1], m->m[1][1], m->m[2][1],
        m->m[0][2], m->m[1][2], m->m[2][2]
    );
}

float mat3_determinant(const Mat3* m) {
    return m->m[0][0] * (m->m[1][1] * m->m[2][2] - m->m[1][2] * m->m[2][1])
         - m->m[0][1] * (m->m[1][0] * m->m[2][2] - m->m[1][2] * m->m[2][0])
         + m->m[0][2] * (m->m[1][0] * m->m[2][1] - m->m[1][1] * m->m[2][0]);
}

void mat3_inverse(Mat3* m) {
    float det = mat3_determinant(m);
    if (fabsf(det) < FM_EPSILON) return;

    float invDet = 1.0f / det;
    Mat3 tmp;

    tmp.m[0][0] = (m->m[1][1] * m->m[2][2] - m->m[1][2] * m->m[2][1]) * invDet;
    tmp.m[0][1] = (m->m[0][2] * m->m[2][1] - m->m[0][1] * m->m[2][2]) * invDet;
    tmp.m[0][2] = (m->m[0][1] * m->m[1][2] - m->m[0][2] * m->m[1][1]) * invDet;
    tmp.m[1][0] = (m->m[1][2] * m->m[2][0] - m->m[1][0] * m->m[2][2]) * invDet;
    tmp.m[1][1] = (m->m[0][0] * m->m[2][2] - m->m[0][2] * m->m[2][0]) * invDet;
    tmp.m[1][2] = (m->m[0][2] * m->m[1][0] - m->m[0][0] * m->m[1][2]) * invDet;
    tmp.m[2][0] = (m->m[1][0] * m->m[2][1] - m->m[1][1] * m->m[2][0]) * invDet;
    tmp.m[2][1] = (m->m[0][1] * m->m[2][0] - m->m[0][0] * m->m[2][1]) * invDet;
    tmp.m[2][2] = (m->m[0][0] * m->m[1][1] - m->m[0][1] * m->m[1][0]) * invDet;

    *m = tmp;
}

void mat3_copy_from(Mat3* m1, const Mat3* m2) {
    *m1 = *m2;
}

Mat3 mat3_clone(const Mat3* m) {
    return *m;
}

Vec3 mat3_get_row(const Mat3* m, int index) {
    return vec3_new(m->m[index][0], m->m[index][1], m->m[index][2]);
}

Vec3 mat3_get_col(const Mat3* m, int index) {
    return vec3_new(m->m[0][index], m->m[1][index], m->m[2][index]);
}

void mat3_get_row_to(const Mat3* m, int index, Vec3* dst) {
    dst->x = m->m[index][0];
    dst->y = m->m[index][1];
    dst->z = m->m[index][2];
}

void mat3_get_col_to(const Mat3* m, int index, Vec3* dst) {
    dst->x = m->m[0][index];
    dst->y = m->m[1][index];
    dst->z = m->m[2][index];
}

Mat3 mat3_from_quat(const Quat* q) {
    float x = q->x, y = q->y, z = q->z, w = q->w;
    float x2 = x + x, y2 = y + y, z2 = z + z;
    float xx = x * x2, xy = x * y2, xz = x * z2;
    float yy = y * y2, yz = y * z2, zz = z * z2;
    float wx = w * x2, wy = w * y2, wz = w * z2;

    return (Mat3){{
        { 1 - (yy + zz), xy - wz, xz + wy },
        { xy + wz, 1 - (xx + zz), yz - wx },
        { xz - wy, yz + wx, 1 - (xx + yy) }
    }};
}

Quat mat3_to_quat(const Mat3* m) {
    Quat q;
    float trace = m->m[0][0] + m->m[1][1] + m->m[2][2];

    if (trace > 0) {
        float s = 0.5f / sqrtf(trace + 1.0f);
        q.w = 0.25f / s;
        q.x = (m->m[2][1] - m->m[1][2]) * s;
        q.y = (m->m[0][2] - m->m[2][0]) * s;
        q.z = (m->m[1][0] - m->m[0][1]) * s;
    } else if (m->m[0][0] > m->m[1][1] && m->m[0][0] > m->m[2][2]) {
        float s = 2.0f * sqrtf(1.0f + m->m[0][0] - m->m[1][1] - m->m[2][2]);
        q.w = (m->m[2][1] - m->m[1][2]) / s;
        q.x = 0.25f * s;
        q.y = (m->m[0][1] + m->m[1][0]) / s;
        q.z = (m->m[0][2] + m->m[2][0]) / s;
    } else if (m->m[1][1] > m->m[2][2]) {
        float s = 2.0f * sqrtf(1.0f + m->m[1][1] - m->m[0][0] - m->m[2][2]);
        q.w = (m->m[0][2] - m->m[2][0]) / s;
        q.x = (m->m[0][1] + m->m[1][0]) / s;
        q.y = 0.25f * s;
        q.z = (m->m[1][2] + m->m[2][1]) / s;
    } else {
        float s = 2.0f * sqrtf(1.0f + m->m[2][2] - m->m[0][0] - m->m[1][1]);
        q.w = (m->m[1][0] - m->m[0][1]) / s;
        q.x = (m->m[0][2] + m->m[2][0]) / s;
        q.y = (m->m[1][2] + m->m[2][1]) / s;
        q.z = 0.25f * s;
    }
    return q;
}

Mat3 mat3_from_euler_xyz(const Vec3* euler) {
    float sx, cx, sy, cy, sz, cz;
    fm_sincosf(euler->x, &sx, &cx);
    fm_sincosf(euler->y, &sy, &cy);
    fm_sincosf(euler->z, &sz, &cz);

    return (Mat3){{
        { cy * cz, -cy * sz, sy },
        { sx * sy * cz + cx * sz, -sx * sy * sz + cx * cz, -sx * cy },
        { -cx * sy * cz + sx * sz, cx * sy * sz + sx * cz, cx * cy }
    }};
}

Vec3 mat3_to_euler_xyz(const Mat3* m) {
    Vec3 euler;
    if (m->m[0][2] < 1.0f) {
        if (m->m[0][2] > -1.0f) {
            euler.y = asinf(m->m[0][2]);
            euler.x = fm_atan2f(-m->m[1][2], m->m[2][2]);
            euler.z = fm_atan2f(-m->m[0][1], m->m[0][0]);
        } else {
            euler.y = -FM_PI * 0.5f;
            euler.x = -fm_atan2f(m->m[1][0], m->m[1][1]);
            euler.z = 0;
        }
    } else {
        euler.y = FM_PI * 0.5f;
        euler.x = fm_atan2f(m->m[1][0], m->m[1][1]);
        euler.z = 0;
    }
    return euler;
}

void vec3_mul_mat3(Vec3* v, const Mat3* m) {
    float x = v->x, y = v->y, z = v->z;
    v->x = x * m->m[0][0] + y * m->m[1][0] + z * m->m[2][0];
    v->y = x * m->m[0][1] + y * m->m[1][1] + z * m->m[2][1];
    v->z = x * m->m[0][2] + y * m->m[1][2] + z * m->m[2][2];
}
