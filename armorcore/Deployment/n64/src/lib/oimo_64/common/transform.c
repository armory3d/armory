#include "Transform.h"

Transform transform_new(const Vec3* position, const Mat3* rotation) {
    Transform t;
    t.position = position ? *position : vec3_zero();
    t.rotation = rotation ? *rotation : mat3_identity();
    return t;
}

Transform transform_identity(void) {
    return (Transform){
        .position = {{ 0, 0, 0 }},
        .rotation = {{ {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }}
    };
}

void transform_get_position(const Transform* t, Vec3* out) {
    *out = t->position;
}

void transform_set_position(Transform* t, const Vec3* pos) {
    t->position = *pos;
}

void transform_translate(Transform* t, const Vec3* translation) {
    vec3_add(&t->position, translation);
}

void transform_get_rotation(const Transform* t, Mat3* out) {
    *out = t->rotation;
}

void transform_set_rotation(Transform* t, const Mat3* m) {
    t->rotation = *m;
}

void transform_set_rotation_xyz(Transform* t, const Vec3* euler) {
    t->rotation = mat3_from_euler_xyz(euler);
}

void transform_rotate(Transform* t, const Mat3* m) {
    mat3_mul(&t->rotation, m);
}

void transform_rotate_xyz(Transform* t, const Vec3* euler) {
    Mat3 rot = mat3_from_euler_xyz(euler);
    mat3_mul(&t->rotation, &rot);
}

Quat transform_get_orientation(const Transform* t) {
    return mat3_to_quat(&t->rotation);
}

void transform_set_orientation(Transform* t, const Quat* q) {
    t->rotation = mat3_from_quat(q);
}

Transform transform_clone(const Transform* t) {
    return *t;
}

void transform_copy_from(Transform* t1, const Transform* t2) {
    *t1 = *t2;
}

void vec3_mul_transform(Vec3* v, const Transform* t) {
    vec3_mul_mat3(v, &t->rotation);
    vec3_add(v, &t->position);
}

void vec3_mul_transform_inv(Vec3* v, const Transform* t) {
    vec3_sub(v, &t->position);
    const Mat3* m = &t->rotation;
    float x = v->x, y = v->y, z = v->z;
    v->x = x * m->m[0][0] + y * m->m[0][1] + z * m->m[0][2];
    v->y = x * m->m[1][0] + y * m->m[1][1] + z * m->m[1][2];
    v->z = x * m->m[2][0] + y * m->m[2][1] + z * m->m[2][2];
}
