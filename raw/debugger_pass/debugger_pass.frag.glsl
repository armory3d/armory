#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D tex;
uniform vec3 eye;
uniform vec3 eyeLook;

in vec2 texCoord;
in vec3 viewRay;

vec2 octahedronWrap(vec2 v) {
	return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec3 getPos(float depth) {
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	// float linearDepth = projectionB / (depth - projectionA);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}

void main() {
	// Normals
	vec4 col = texture(tex, texCoord);
    vec2 enc = col.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	gl_FragColor = vec4(n * 0.5 + 0.5, 1.0);

	// vec3 p = getPos(depth);
	// vec3 baseColor = g1.rgb;
	// vec2 roughmet = unpackFloat(g1.a);
	// float roughness = roughmet.x;
	// float metalness = roughmet.y;
}
