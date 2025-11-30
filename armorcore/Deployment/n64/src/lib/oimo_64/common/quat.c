#include "Quat.h"
#include <math.h>

Quat quat_new(float x, float y, float z, float w) {
    return (Quat){{ x, y, z, w }};
}

void quat_init(Quat* q, float x, float y, float z, float w) {
    q->x = x; q->y = y; q->z = z; q->w = w;
}

Quat quat_identity(void) {
    return (Quat){{ 0, 0, 0, 1 }};
}

void quat_add(Quat* q1, const Quat* q2) {
    q1->x += q2->x; q1->y += q2->y; q1->z += q2->z; q1->w += q2->w;
}

void quat_sub(Quat* q1, const Quat* q2) {
    q1->x -= q2->x; q1->y -= q2->y; q1->z -= q2->z; q1->w -= q2->w;
}

void quat_scale(Quat* q, float s) {
    q->x *= s; q->y *= s; q->z *= s; q->w *= s;
}

float quat_length_sq(const Quat* q) {
    return fm_quat_dot(q, q);
}

float quat_length(const Quat* q) {
    return sqrtf(quat_length_sq(q));
}

float quat_dot(const Quat* q1, const Quat* q2) {
    return fm_quat_dot(q1, q2);
}

Quat quat_normalized(const Quat* q) {
    Quat result;
    fm_quat_norm(&result, q);
    return result;
}

void quat_normalize(Quat* q) {
    fm_quat_norm(q, q);
}

Quat quat_slerp(const Quat* q1, const Quat* q2, float t) {
    Quat result;
    fm_quat_slerp(&result, q1, q2, t);
    return result;
}

void quat_copy_from(Quat* q1, const Quat* q2) {
    *q1 = *q2;
}

Quat quat_clone(const Quat* q) {
    return *q;
}

Quat quat_from_mat3(const Mat3* m) {
    return mat3_to_quat(m);
}

Mat3 quat_to_mat3(const Quat* q) {
    return mat3_from_quat(q);
}
