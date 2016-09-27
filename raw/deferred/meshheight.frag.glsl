// Merge with mesh.frag
#version 450

#ifdef GL_ES
precision mediump float;
#endif

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
uniform sampler2D sheight;
uniform float heightStrength;

in vec2 te_texCoord;
#ifdef _NorTex
	in mat3 TBN;
#else
	in vec3 te_normal;
#endif

out vec4[2] outColor;

float packFloat(float f1, float f2) {
	float index = floor(f1 * 1000.0); // Temporary
	float alpha = clamp(f2, 0.0, 1.0 - 0.001);
	return index + alpha;
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

void main() {
	vec2 newCoord = te_texCoord;
	
#ifdef _NorTex
	vec3 n = (texture(snormal, newCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(te_normal);
#endif
#ifdef _NorStr
	n *= normalStrength;
#endif

	vec3 baseColor = vec3(1.0);//matColor.rgb;
#ifdef _BaseTex
	vec4 texel = texture(sbase, newCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2)); // Variant 1
	baseColor *= texel.rgb;
#endif

#ifdef _MetTex
	float metalness = texture(smetal, newCoord).r;
#endif

#ifdef _RoughTex
	float roughness = texture(srough, newCoord).r;
#endif
#ifdef _RoughStr
	roughness *= roughnessStrength;
#endif
		
#ifdef _OccTex
	float occ = texture(socclusion, newCoord).r;
#else
	float occ = occlusion; 
#endif
	
	// Pack normal
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);

	outColor[0] = vec4(n.xy, packFloat(metalness, roughness), mask);
	outColor[1] = vec4(baseColor.rgb, occ);
}
