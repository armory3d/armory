#version 450

#ifdef GL_ES
precision highp float;
#endif

in vec2 pos;

out vec2 texCoord;
out vec3 cameraRay;

uniform mat4 invP;

const vec2 madd = vec2(0.5, 0.5);

void main() {
	// Scale vertex attribute to [0-1] range
	texCoord = pos.xy * madd + madd;
  
	vec4 ray = vec4(texcoord * 2.0 - 1.0, 1.0, 1.0);
	ray = invP * ray;
	cameraRay = ray.xyz / ray.w;

	gl_Position = vec4(pos.xy, 0.0, 1.0);
}
