#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform samplerCube probeTex;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform mat4 invVP;
uniform vec3 probep;
uniform vec3 eye;

in vec4 wvpposition;
out vec4 fragColor;

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, depth

	float roughness = unpackFloat(g0.b).y;
	if (roughness > 0.95) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float spec = fract(texture(gbuffer1, texCoord).a);
	if (spec == 0.0) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float depth = (1.0 - g0.a) * 2.0 - 1.0;
	vec3 wp = getPos2(invVP, depth, texCoord);

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 v = wp - eye;

	float intensity = clamp((1.0 - roughness) * dot(wp - probep, n), 0.0, 1.0);
	fragColor.rgb = texture(probeTex, reflect(v, n)).rgb * intensity;
}
