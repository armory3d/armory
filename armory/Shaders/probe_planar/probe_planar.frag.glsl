#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D probeTex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform mat4 probeVP;
uniform mat4 invVP;
uniform vec3 proben;

in vec4 wvpposition;
out vec4 fragColor;

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, roughness, metallic/matid

	float roughness = g0.b;
	if (roughness > 0.95) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float spec = fract(textureLod(gbuffer1, texCoord, 0.0).a);
	if (spec == 0.0) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 wp = getPos2(invVP, depth, texCoord);
	vec4 pp = probeVP * vec4(wp.xyz, 1.0);
	vec2 tc = (pp.xy / pp.w) * 0.5 + 0.5;
	#ifdef _InvY
	tc.y = 1.0 - tc.y;
	#endif

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	float intensity = clamp((1.0 - roughness) * dot(n, proben), 0.0, 1.0);
	fragColor.rgb = texture(probeTex, tc).rgb * intensity;
}
