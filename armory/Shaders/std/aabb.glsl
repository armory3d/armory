#ifndef _AABB_GLSL
#define _AABB_GLSL

bool IntersectAABB(vec3[2] a, vec3[2] b)
{
	if (abs(a[0][0] - b[0][0]) > (a[1][0] + b[1][0]))
		return false;
	if (abs(a[0][1] - b[0][1]) > (a[1][1] + b[1][1]))
		return false;
	if (abs(a[0][2] - b[0][2]) > (a[1][2] + b[1][2]))
		return false;

	return true;
}

void AABBfromMinMax(inout vec3[2] aabb, vec3 _min, vec3 _max)
{
	aabb[0] = (_min + _max) * 0.5f;
	aabb[1] = abs(_max - aabb[0]);
}

#endif
