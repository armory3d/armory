#version 450

#include "compiled.inc"

uniform mat4 invP;

in vec2 pos;

out vec2 texCoord;
out vec3 viewRay;

void main() {
	// Scale vertex attribute to [0-1] range
	const vec2 madd = vec2(0.5, 0.5);
	texCoord = pos.xy * madd + madd;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	gl_Position = vec4(pos.xy, 0.0, 1.0);

	// NDC (at the back of cube)
	vec4 v = vec4(pos.x, pos.y, 1.0, 1.0);
	v = vec4(invP * v);
	viewRay = vec3(v.xy / v.z, 1.0);
}
