#include "Vec3.h"

Vec3 vec3_new(float x, float y, float z) {
    return (Vec3){{ x, y, z }};
}

void vec3_init(Vec3* v, float x, float y, float z) {
    v->x = x; v->y = y; v->z = z;
}

Vec3 vec3_zero(void) {
    return (Vec3){{ 0, 0, 0 }};
}

void vec3_add(Vec3* v1, const Vec3* v2) {
    fm_vec3_add(v1, v1, v2);
}

void vec3_add3(Vec3* v, float x, float y, float z) {
    v->x += x; v->y += y; v->z += z;
}

void vec3_add_scaled(Vec3* v1, const Vec3* v2, float s) {
    v1->x += v2->x * s;
    v1->y += v2->y * s;
    v1->z += v2->z * s;
}

void vec3_sub(Vec3* v1, const Vec3* v2) {
    fm_vec3_sub(v1, v1, v2);
}

void vec3_sub3(Vec3* v, float x, float y, float z) {
    v->x -= x; v->y -= y; v->z -= z;
}

void vec3_scale(Vec3* v, float s) {
    fm_vec3_scale(v, v, s);
}

void vec3_scale3(Vec3* v, float x, float y, float z) {
    v->x *= x; v->y *= y; v->z *= z;
}

void vec3_negate(Vec3* v) {
    fm_vec3_negate(v, v);
}

float vec3_dot(const Vec3* v1, const Vec3* v2) {
    return fm_vec3_dot(v1, v2);
}

Vec3 vec3_cross(const Vec3* v1, const Vec3* v2) {
    Vec3 result;
    fm_vec3_cross(&result, v1, v2);
    return result;
}

float vec3_length_sq(const Vec3* v) {
    return fm_vec3_len2(v);
}

float vec3_length(const Vec3* v) {
    return fm_vec3_len(v);
}

Vec3 vec3_normalized(const Vec3* v) {
    Vec3 result;
    fm_vec3_norm(&result, v);
    return result;
}

void vec3_normalize(Vec3* v) {
    fm_vec3_norm(v, v);
}

void vec3_copy_from(Vec3* v1, const Vec3* v2) {
    *v1 = *v2;
}

Vec3 vec3_clone(const Vec3* v) {
    return *v;
}
