#version 450

#ifdef GL_ES
precision highp float;
#endif

uniform mat4 LVWVP;
// uniform mat4 invVP;
// uniform vec3 eye;

in vec3 pos;

// out vec2 texCoord;
out vec4 wvpposition;
// out vec3 viewRay;

// const vec2 madd = vec2(0.5, 0.5);

void main() {
	wvpposition = LVWVP * vec4(pos, 1.0);

	// Scale vertex attribute to [0-1] range
	// texCoord = wvpposition.xy * madd + madd;

	// NDC (at the back of cube)
	// vec4 v = vec4(wvpposition.xy, 1.0, 1.0);	
	// v = vec4(invVP * v);
	// v.xyz /= v.w;
	// viewRay = v.xyz - eye;

	gl_Position = wvpposition;
}
