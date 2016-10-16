#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _CompoPos
	uniform mat4 invVP;
	uniform vec3 eye;
#endif

in vec2 pos;

out vec2 texCoord;
#ifdef _CompoPos
	out vec3 viewRay;
#endif

const vec2 madd = vec2(0.5, 0.5);

void main() {
	// Scale vertex attribute to [0-1] range
	texCoord = pos.xy * madd + madd;

	gl_Position = vec4(pos.xy, 0.0, 1.0);

#ifdef _CompoPos
	// NDC (at the back of cube)
	vec4 v = vec4(pos.xy, 1.0, 1.0);	
	v = vec4(invVP * v);
	v.xyz /= v.w;
	viewRay = v.xyz - eye;
#endif
}
