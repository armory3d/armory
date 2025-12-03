#include "transform.h"
#include "../../types.h"
#include "../../data/scenes.h"
#include <t3d/t3dmath.h>

// Rotate a vector by a quaternion: v' = q * v * q^-1
// Using optimized formula: v' = v + 2w(q_xyz × v) + 2(q_xyz × (q_xyz × v))
static inline void quat_rotate_vec3(float *out, const T3DQuat *q, float vx, float vy, float vz)
{
    float qx = q->v[0], qy = q->v[1], qz = q->v[2], qw = q->v[3];

    // t = 2 * (q_xyz × v)
    float tx = 2.0f * (qy * vz - qz * vy);
    float ty = 2.0f * (qz * vx - qx * vz);
    float tz = 2.0f * (qx * vy - qy * vx);

    // v' = v + w*t + (q_xyz × t)
    out[0] = vx + qw * tx + (qy * tz - qz * ty);
    out[1] = vy + qw * ty + (qz * tx - qx * tz);
    out[2] = vz + qw * tz + (qx * ty - qy * tx);
}

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc.x += x;
	t->loc.y += y;
	t->loc.z += z;
	t->dirty = FB_COUNT;
}

void it_translate_local(ArmObject *obj, ArmObject *objects, float x, float y, float z)
{
	// If object has a parent, rotate the translation by parent's orientation
	if (obj->parent_index >= 0 && objects != NULL) {
		ArmObject *parent = &objects[obj->parent_index];
		float rotated[3];
		quat_rotate_vec3(rotated, &parent->transform.rot, x, y, z);
		x = rotated[0];
		y = rotated[1];
		z = rotated[2];
	}

	obj->transform.loc.x += x;
	obj->transform.loc.y += y;
	obj->transform.loc.z += z;
	obj->transform.dirty = FB_COUNT;
}

void it_rotate_axis(ArmTransform *t, float ax, float ay, float az, float angle)
{
	float axis[3] = {ax, ay, az};
	t3d_quat_rotate_euler(&t->rot, axis, angle);
	t->dirty = FB_COUNT;
}

void it_rotate_axis_global(ArmTransform *t, float ax, float ay, float az, float angle)
{
	fm_vec3_t axis = {{ax, ay, az}};
	fm_quat_t axis_rot;
	fm_quat_from_axis_angle(&axis_rot, &axis, angle);

	fm_quat_t current = t->rot;
	fm_quat_mul(&t->rot, &axis_rot, &current);

	t->dirty = FB_COUNT;
}

void it_set_loc(ArmTransform *t, float x, float y, float z)
{
	t->loc.x = x;
	t->loc.y = y;
	t->loc.z = z;
	t->dirty = FB_COUNT;
}

void it_set_rot(ArmTransform *t, float x, float y, float z, float w)
{
	t->rot.x = x;
	t->rot.y = y;
	t->rot.z = z;
	t->rot.w = w;
	t->dirty = FB_COUNT;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale.x = x;
	t->scale.y = y;
	t->scale.z = z;
	t->dirty = FB_COUNT;
}
