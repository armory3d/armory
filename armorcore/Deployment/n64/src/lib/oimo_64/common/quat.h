#ifndef OIMO_QUAT_H
#define OIMO_QUAT_H

#include <libdragon.h>
#include "Mat3.h"

#ifdef __cplusplus
extern "C" {
#endif

// Quat is typedef'd in Mat3.h as fm_quat_t

Quat quat_new(float x, float y, float z, float w);
void quat_init(Quat* q, float x, float y, float z, float w);
Quat quat_identity(void);

void quat_add(Quat* q1, const Quat* q2);
void quat_sub(Quat* q1, const Quat* q2);
void quat_scale(Quat* q, float s);

float quat_length_sq(const Quat* q);
float quat_length(const Quat* q);
float quat_dot(const Quat* q1, const Quat* q2);

Quat quat_normalized(const Quat* q);
void quat_normalize(Quat* q);

Quat quat_slerp(const Quat* q1, const Quat* q2, float t);

void quat_copy_from(Quat* q1, const Quat* q2);
Quat quat_clone(const Quat* q);

Quat quat_from_mat3(const Mat3* m);
Mat3 quat_to_mat3(const Quat* q);

#ifdef __cplusplus
}
#endif

#endif
