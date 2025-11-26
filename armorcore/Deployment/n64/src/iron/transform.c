#include "transform.h"

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] += x;
	t->loc[1] += y;
	t->loc[2] += z;
}

void it_rotate(ArmTransform *t, float x, float y, float z)
{
	t->rot[0] += x;
	t->rot[1] += y;
	t->rot[2] += z;
}

void it_set_loc(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] = x;
	t->loc[1] = y;
	t->loc[2] = z;
}

void it_set_rot(ArmTransform *t, float x, float y, float z)
{
	t->rot[0] = x;
	t->rot[1] = y;
	t->rot[2] = z;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale[0] = x;
	t->scale[1] = y;
	t->scale[2] = z;
}
