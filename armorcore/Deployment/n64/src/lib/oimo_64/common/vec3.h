#ifndef OIMO_VEC3_H
#define OIMO_VEC3_H

#include <libdragon.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef fm_vec3_t Vec3;

Vec3 vec3_new(float x, float y, float z);
void vec3_init(Vec3* v, float x, float y, float z);
Vec3 vec3_zero(void);

void vec3_add(Vec3* v1, const Vec3* v2);
void vec3_add3(Vec3* v, float x, float y, float z);
void vec3_add_scaled(Vec3* v1, const Vec3* v2, float s);
void vec3_sub(Vec3* v1, const Vec3* v2);
void vec3_sub3(Vec3* v, float x, float y, float z);
void vec3_scale(Vec3* v, float s);
void vec3_scale3(Vec3* v, float x, float y, float z);
void vec3_negate(Vec3* v);

float vec3_dot(const Vec3* v1, const Vec3* v2);
Vec3 vec3_cross(const Vec3* v1, const Vec3* v2);

float vec3_length_sq(const Vec3* v);
float vec3_length(const Vec3* v);

Vec3 vec3_normalized(const Vec3* v);
void vec3_normalize(Vec3* v);

void vec3_copy_from(Vec3* v1, const Vec3* v2);
Vec3 vec3_clone(const Vec3* v);

#ifdef __cplusplus
}
#endif

#endif
