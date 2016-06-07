#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

#ifdef _AMTex
uniform sampler2D salbedo;
#endif
#ifdef _NMTex
uniform sampler2D snormal;
#endif
#ifdef _OMTex
uniform sampler2D som;
#endif
#ifdef _RMTex
uniform sampler2D srm;
#else
uniform float roughness;
#endif
#ifdef _MMTex
uniform sampler2D smm;
#else
uniform float metalness;
#endif
uniform float mask;

#ifdef _Probe1
uniform int probeID;
uniform vec3 probeVolumeCenter;
uniform vec3 probeVolumeSize;
#endif

in vec4 mvpposition;
#ifdef _AMTex
in vec2 texCoord;
#endif
in vec4 lPos;
in vec4 matColor;
#ifdef _NMTex
in mat3 TBN;
#else
in vec3 normal;
#endif

#ifdef _Probe1
in vec4 mpos;
#endif

float packFloat(float f1, float f2) {
	int index = int(f1 * 1000);
	float alpha = f2 == 0.0 ? f2 : (f2 - 0.0001);
	float result = index + alpha;
	return result;
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

#ifdef _Probe1
float distanceBox(vec3 point, vec3 center, vec3 halfExtents) {  	
	vec3 d = abs(point - center) - halfExtents;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}
#endif

void main() {
	
#ifdef _NMTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif

	vec3 baseColor = matColor.rgb;
#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel.rgb;
#endif

#ifdef _MMTex
	float metalness = texture(smm, texCoord).r;
#endif

#ifdef _RMTex
	float roughness = texture(srm, texCoord).r;
#endif
		
#ifdef _OMTex
	float occlusion = texture(som, texCoord).r;
#else
	float occlusion = 1.0; 
#endif
	
	// occlusion - pack with mask
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);
	
#ifdef _Probe1
	float dist = distanceBox(mpos.xyz, probeVolumeCenter, probeVolumeSize);
	float mask_probe = probeID;
	if (probeID > 0) {
		const float eps = 0.00001;
		mask_probe += clamp(0.5 + dist * 3.0, 0, 1.0 - eps);
	}
	gl_FragData[0] = vec4(n.xy, occlusion, mask_probe);
#else
	gl_FragData[0] = vec4(n.xy, occlusion, mask);
#endif
	gl_FragData[1] = vec4(baseColor.rgb, packFloat(roughness, metalness));
}
