#ifndef OIMO_COMMON_TRANSFORM_H
#define OIMO_COMMON_TRANSFORM_H

#include "setting.h"
#include "vec3.h"
#include "mat3.h"
#include "quat.h"

typedef struct OimoTransform {
    OimoVec3 position;   // Translation
    OimoMat3 rotation;   // Rotation matrix (3x3 orthogonal)
} OimoTransform;

// Create identity transform (no translation, no rotation)
static inline OimoTransform oimo_transform_identity(void) {
    OimoTransform tf;
    tf.position = oimo_vec3_zero();
    tf.rotation = oimo_mat3_identity();
    return tf;
}

// Create transform with position and identity rotation
static inline OimoTransform oimo_transform_from_position(const OimoVec3* pos) {
    OimoTransform tf;
    tf.position = oimo_vec3_copy(pos);
    tf.rotation = oimo_mat3_identity();
    return tf;
}

// Create transform with position and rotation matrix
static inline OimoTransform oimo_transform(const OimoVec3* pos, const OimoMat3* rot) {
    OimoTransform tf;
    tf.position = oimo_vec3_copy(pos);
    tf.rotation = oimo_mat3_copy(rot);
    return tf;
}

// Create transform from position and quaternion
static inline OimoTransform oimo_transform_from_quat(const OimoVec3* pos, const OimoQuat* q) {
    OimoTransform tf;
    tf.position = oimo_vec3_copy(pos);
    tf.rotation = oimo_quat_to_mat3(q);
    return tf;
}

// Copy transform
static inline OimoTransform oimo_transform_copy(const OimoTransform* tf) {
    OimoTransform result;
    result.position = oimo_vec3_copy(&tf->position);
    result.rotation = oimo_mat3_copy(&tf->rotation);
    return result;
}

// Get position
static inline OimoVec3 oimo_transform_get_position(const OimoTransform* tf) {
    return oimo_vec3_copy(&tf->position);
}

// Get rotation matrix
static inline OimoMat3 oimo_transform_get_rotation(const OimoTransform* tf) {
    return oimo_mat3_copy(&tf->rotation);
}

// Get rotation as quaternion
static inline OimoQuat oimo_transform_get_orientation(const OimoTransform* tf) {
    return oimo_mat3_to_quat(&tf->rotation);
}

// Set to identity
static inline void oimo_transform_set_identity(OimoTransform* tf) {
    tf->position = oimo_vec3_zero();
    tf->rotation = oimo_mat3_identity();
}

// Set position
static inline void oimo_transform_set_position(OimoTransform* tf, const OimoVec3* pos) {
    oimo_vec3_copy_to(&tf->position, pos);
}

// Set position from components
static inline void oimo_transform_set_position3(OimoTransform* tf, OimoScalar x, OimoScalar y, OimoScalar z) {
    oimo_vec3_set(&tf->position, x, y, z);
}

// Set rotation matrix
static inline void oimo_transform_set_rotation(OimoTransform* tf, const OimoMat3* rot) {
    oimo_mat3_copy_to(&tf->rotation, rot);
}

// Set rotation from quaternion
static inline void oimo_transform_set_orientation(OimoTransform* tf, const OimoQuat* q) {
    oimo_mat3_from_quat(&tf->rotation, q);
}

// Set rotation from Euler angles (XYZ order)
static inline void oimo_transform_set_rotation_xyz(OimoTransform* tf, OimoScalar rx, OimoScalar ry, OimoScalar rz) {
    tf->rotation = oimo_mat3_from_euler_xyz(rx, ry, rz);
}

// Translate by offset
static inline void oimo_transform_translate(OimoTransform* tf, const OimoVec3* offset) {
    oimo_vec3_add_eq(&tf->position, offset);
}

// Rotate by rotation matrix (prepend: new_rotation * old_rotation)
static inline void oimo_transform_rotate(OimoTransform* tf, const OimoMat3* rot) {
    tf->rotation = oimo_mat3_mul(rot, &tf->rotation);
}

// Rotate by quaternion
static inline void oimo_transform_rotate_quat(OimoTransform* tf, const OimoQuat* q) {
    OimoMat3 rot = oimo_quat_to_mat3(q);
    tf->rotation = oimo_mat3_mul(&rot, &tf->rotation);
}

// Rotate by Euler angles (XYZ order)
static inline void oimo_transform_rotate_xyz(OimoTransform* tf, OimoScalar rx, OimoScalar ry, OimoScalar rz) {
    OimoMat3 rot = oimo_mat3_from_euler_xyz(rx, ry, rz);
    tf->rotation = oimo_mat3_mul(&rot, &tf->rotation);
}

// Transform a point: rotation * point + position
static inline OimoVec3 oimo_transform_point(const OimoTransform* tf, const OimoVec3* p) {
    OimoVec3 rotated = oimo_mat3_mul_vec3(&tf->rotation, *p);
    return oimo_vec3_add(rotated, tf->position);
}

// Transform a vector (direction): rotation * vector (no translation)
static inline OimoVec3 oimo_transform_vector(const OimoTransform* tf, const OimoVec3* v) {
    return oimo_mat3_mul_vec3(&tf->rotation, *v);
}

// Inverse transform a point: rotation^T * (point - position)
static inline OimoVec3 oimo_transform_inv_point(const OimoTransform* tf, const OimoVec3* p) {
    OimoVec3 local = oimo_vec3_sub(*p, tf->position);
    return oimo_mat3_tmul_vec3(&tf->rotation, local);
}

// Inverse transform a vector: rotation^T * vector
static inline OimoVec3 oimo_transform_inv_vector(const OimoTransform* tf, const OimoVec3* v) {
    return oimo_mat3_tmul_vec3(&tf->rotation, *v);
}

// Multiply transforms: tf1 * tf2
// Result position = tf1.rotation * tf2.position + tf1.position
// Result rotation = tf1.rotation * tf2.rotation
static inline OimoTransform oimo_transform_mul(const OimoTransform* tf1, const OimoTransform* tf2) {
    OimoTransform result;
    OimoVec3 rotated_pos = oimo_mat3_mul_vec3(&tf1->rotation, tf2->position);
    result.position = oimo_vec3_add(rotated_pos, tf1->position);
    result.rotation = oimo_mat3_mul(&tf1->rotation, &tf2->rotation);
    return result;
}

// Inverse transform: rotation^T, -rotation^T * position
static inline OimoTransform oimo_transform_inverse(const OimoTransform* tf) {
    OimoTransform result;
    result.rotation = oimo_mat3_transpose(&tf->rotation);
    OimoVec3 neg_pos = oimo_vec3_neg(tf->position);
    result.position = oimo_mat3_mul_vec3(&result.rotation, neg_pos);
    return result;
}

// Copy from another transform
static inline void oimo_transform_copy_to(OimoTransform* dst, const OimoTransform* src) {
    oimo_vec3_copy_to(&dst->position, &src->position);
    oimo_mat3_copy_to(&dst->rotation, &src->rotation);
}

// Get the X axis of the rotation (first column)
static inline OimoVec3 oimo_transform_get_x_axis(const OimoTransform* tf) {
    return oimo_mat3_get_col(&tf->rotation, 0);
}

// Get the Y axis of the rotation (second column)
static inline OimoVec3 oimo_transform_get_y_axis(const OimoTransform* tf) {
    return oimo_mat3_get_col(&tf->rotation, 1);
}

// Get the Z axis of the rotation (third column)
static inline OimoVec3 oimo_transform_get_z_axis(const OimoTransform* tf) {
    return oimo_mat3_get_col(&tf->rotation, 2);
}

#endif // OIMO_COMMON_TRANSFORM_H
