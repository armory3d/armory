#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../std/gbuffer.glsl"
// octahedronWrap()
// packFloat()

uniform float mask;
#ifdef _BaseTex
	uniform sampler2D sbase;
#endif
#ifdef _NorTex
	uniform sampler2D snormal;
#endif
#ifdef _NorStr
	uniform float normalStrength;
#endif
#ifdef _OccTex
	uniform sampler2D socclusion;
#else
	uniform float occlusion;
#endif
#ifdef _RoughTex
	uniform sampler2D srough;
#else
	uniform float roughness;
#endif
#ifdef _RoughStr
	uniform float roughnessStrength;
#endif
#ifdef _MetTex
	uniform sampler2D smetal;
#else
	uniform float metalness;
#endif
#ifdef _Probes
	uniform int probeID;
	uniform float probeBlending;
	uniform float probeStrength;
	uniform vec3 probeVolumeCenter;
	uniform vec3 probeVolumeSize;
#endif

in vec4 matColor;
#ifdef _Tex
	in vec2 texCoord;
#endif
#ifdef _NorTex
	in mat3 TBN;
#else
	in vec3 normal;
#endif
#ifdef _Probes
	in vec4 wpos;
#endif
#ifdef _Veloc
	in vec4 wvppos;
	in vec4 prevwvppos;
#endif

#ifdef _Veloc
	out vec4[3] fragColor;
#else
	out vec4[2] fragColor;
#endif

#ifdef _Probes
float distanceBox(vec3 point, vec3 center, vec3 halfExtents) {  	
	vec3 d = abs(point - center) - halfExtents;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}
#endif

void main() {
	
#ifdef _NorTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif
#ifdef _NorStr
	n *= normalStrength;
#endif

	vec3 baseColor = matColor.rgb;
#ifdef _BaseTex
	vec4 texel = texture(sbase, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2)); // Variant 1
	baseColor *= texel.rgb;
#endif
	// baseColor = pow(baseColor, vec3(2.2)); // Variant 2

#ifdef _MetTex
	float metalness = texture(smetal, texCoord).r;
#endif

#ifdef _RoughTex
	float roughness = texture(srough, texCoord).r;
#endif
#ifdef _RoughStr
	roughness *= roughnessStrength;
#endif
		
#ifdef _OccTex
	float occ = texture(socclusion, texCoord).r;
#else
	float occ = occlusion; 
#endif
	
	// Pack normal
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);

#ifdef _Probes
	float mask_probe;
	if (probeID > 0) { // Non-global probe attached
		// Distance of vertex located inside probe to probe bounds
		float dist = distanceBox(wpos.xyz, probeVolumeCenter, probeVolumeSize);
		if (dist > 0) mask_probe = 0;
		else {
			// Blend local probe with global probe		
			const float eps = 0.00001;
			float clampres = clamp(probeBlending + dist, 0.0, 1.0 - eps);
			mask_probe = probeID + clampres;
		}
	}
	fragColor[0] = vec4(n.xy, packFloat(metalness, roughness), mask_probe);
#else
	fragColor[0] = vec4(n.xy, packFloat(metalness, roughness), mask);
#endif
	fragColor[1] = vec4(baseColor.rgb, occ);

#ifdef _Veloc
	vec2 posa = (wvppos.xy / wvppos.w) * 0.5 + 0.5;
	vec2 posb = (prevwvppos.xy / prevwvppos.w) * 0.5 + 0.5;
	fragColor[2].rg = vec2(posa - posb);
#endif
}
