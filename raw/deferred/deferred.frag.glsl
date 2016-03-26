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

in vec3 position;
in vec4 mvpposition;
#ifdef _AMTex
in vec2 texCoord;
#endif
in vec4 lPos;
in vec4 matColor;
in vec3 lightDir;
in vec3 eyeDir;
#ifdef _NMTex
in mat3 TBN;
#else
in vec3 normal;
#endif

void main() {
	
#ifdef _NMTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif

#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	vec3 baseColor = texel.rgb;
#else
	vec3 baseColor = matColor.rgb;
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
	
	float depth = mvpposition.z / mvpposition.w;
	
	// occlusion
	
	gl_FragData[0] = vec4(n.xyz, depth);
	gl_FragData[1] = vec4(position.xyz, roughness);
	gl_FragData[2] = vec4(baseColor.rgb, metalness);
}
