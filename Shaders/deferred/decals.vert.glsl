#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NorTex
#define _BaseTex
#endif

#ifdef _RampID
#include "../std/math.glsl"
// hash()
#endif

in vec3 pos;

uniform mat4 VP;
uniform mat4 W;
// uniform mat4 WV;
uniform vec4 baseCol;

#ifdef _RampID
uniform vec4 baseCol2;
uniform int uid;
#endif

out vec4 wvpposition;
out vec4 matColor;
// out vec3 orientation;

void main() {
	vec4 sPos = vec4(pos, 1.0);
	wvpposition = VP * W * sPos;

	// orientation = normalize(WV[1].xyz);

#ifdef _RampID
	vec2 p = vec2(float(uid), float(uid));
	float factor = hash(p);
	matColor = mix(baseCol, baseCol2, factor);
#else
	matColor = baseCol;
#endif

	gl_Position = wvpposition;
}
