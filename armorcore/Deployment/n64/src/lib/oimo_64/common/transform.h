#ifndef OIMO_TRANSFORM_H
#define OIMO_TRANSFORM_H

#include "Mat3.h"
#include "Quat.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Transform - Position + Rotation
// =============================================================================

typedef struct Transform {
    Vec3 position;
    Mat3 rotation;
} Transform;

// Construction
Transform transform_new(const Vec3* position, const Mat3* rotation);
Transform transform_identity(void);

// Position
void transform_get_position(const Transform* t, Vec3* out);
void transform_set_position(Transform* t, const Vec3* pos);
void transform_translate(Transform* t, const Vec3* translation);

// Rotation (as Mat3)
void transform_get_rotation(const Transform* t, Mat3* out);
void transform_set_rotation(Transform* t, const Mat3* m);
void transform_set_rotation_xyz(Transform* t, const Vec3* euler);
void transform_rotate(Transform* t, const Mat3* m);
void transform_rotate_xyz(Transform* t, const Vec3* euler);

// Rotation (as Quat)
Quat transform_get_orientation(const Transform* t);
void transform_set_orientation(Transform* t, const Quat* q);

// Copy
Transform transform_clone(const Transform* t);
void transform_copy_from(Transform* t1, const Transform* t2);

// Point transformation
void vec3_mul_transform(Vec3* v, const Transform* t);
void vec3_mul_transform_inv(Vec3* v, const Transform* t);

#ifdef __cplusplus
}
#endif

#endif // OIMO_TRANSFORM_H
