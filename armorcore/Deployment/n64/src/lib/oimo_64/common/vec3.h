#ifndef OIMO_VEC3_H
#define OIMO_VEC3_H

#include <libdragon.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Vec3 - 3D Vector (wraps libdragon's fm_vec3_t)
// =============================================================================

typedef fm_vec3_t Vec3;

// Construction
Vec3 vec3_new(float x, float y, float z);
void vec3_init(Vec3* v, float x, float y, float z);
Vec3 vec3_zero(void);

// Arithmetic (in-place, modifies first argument)
void vec3_add(Vec3* v1, const Vec3* v2);
void vec3_add3(Vec3* v, float x, float y, float z);
void vec3_add_scaled(Vec3* v1, const Vec3* v2, float s);
void vec3_sub(Vec3* v1, const Vec3* v2);
void vec3_sub3(Vec3* v, float x, float y, float z);
void vec3_scale(Vec3* v, float s);
void vec3_scale3(Vec3* v, float x, float y, float z);
void vec3_negate(Vec3* v);

// Products
float vec3_dot(const Vec3* v1, const Vec3* v2);
Vec3 vec3_cross(const Vec3* v1, const Vec3* v2);

// Length
float vec3_length_sq(const Vec3* v);
float vec3_length(const Vec3* v);

// Normalization
Vec3 vec3_normalized(const Vec3* v);
void vec3_normalize(Vec3* v);

// Copy
void vec3_copy_from(Vec3* v1, const Vec3* v2);
Vec3 vec3_clone(const Vec3* v);

#ifdef __cplusplus
}
#endif

#endif // OIMO_VEC3_H
