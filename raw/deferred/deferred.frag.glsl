#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _HMTex
#define _NMTex
#endif
// #ifdef _NMTex
// #define _Tex
// #endif

uniform float mask;
#ifdef _AMTex
	uniform sampler2D salbedo;
#endif
#ifdef _NMTex
	uniform sampler2D snormal;
#endif
#ifdef _NMStr
	uniform float normalStrength;
#endif
#ifdef _OMTex
	uniform sampler2D som;
#else
	uniform float occlusion;
#endif
#ifdef _RMTex
	uniform sampler2D srm;
#else
	uniform float roughness;
#endif
#ifdef _RMStr
	uniform float roughnessStrength;
#endif
#ifdef _MMTex
	uniform sampler2D smm;
#else
	uniform float metalness;
#endif
#ifdef _HMTex
	uniform sampler2D shm;
	uniform float heightStrength;
#endif
#ifdef _Probes
	uniform int probeID;
	uniform vec3 probeVolumeCenter;
	uniform vec3 probeVolumeSize;
#endif

in vec4 matColor;
#ifdef _Tex
	in vec2 texCoord;
#endif
#ifdef _NMTex
	in mat3 TBN;
#else
	in vec3 normal;
#endif
#ifdef _HMTex
	in vec3 tanLightDir;
	in vec3 tanEyeDir;
#endif
#ifdef _Probes
	in vec4 mpos;
#endif
#ifdef _Veloc
	in vec4 mvppos;
	in vec4 prevmvppos;
#endif

#ifdef _Veloc
	out vec4[3] outColor;
#else
	out vec4[2] outColor;
#endif

float packFloat(float f1, float f2) {
	int index = int(f1 * 1000);
	float alpha = f2 == 0.0 ? f2 : (f2 - 0.0001);
	return index + alpha;
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

#ifdef _Probes
float distanceBox(vec3 point, vec3 center, vec3 halfExtents) {  	
	vec3 d = abs(point - center) - halfExtents * 0.75;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}
#endif

#ifdef _HMTex
float parallaxHeight;
const float minLayers = 20;
const float maxLayers = 30;
vec2 parallaxMapping(vec3 V, vec2 T) {
	float parallaxScale = -0.06 * heightStrength;
	// PM
	// float initialHeight = texture(shm, texCoord).r;
	// vec2 texCoordOffset = 0.03 * V.xy / V.z * initialHeight;
	// vec2 texCoordOffset = 0.03 * V.xy * initialHeight;
	// return texCoord + texCoordOffset;
	// POM
	float numLayers = mix(maxLayers, minLayers, abs(dot(vec3(0, 0, 1), V)));
	float layerHeight = 1.0 / numLayers;
	float curLayerHeight = 0;
	vec2 dtex = parallaxScale * V.xy / V.z / numLayers;
	
	vec2 currentTextureCoords = T;
	float heightFromTexture = texture(shm, currentTextureCoords).r;
	
	// while (heightFromTexture > curLayerHeight) {
		// curLayerHeight += layerHeight; 
		// currentTextureCoords -= dtex;
		// heightFromTexture = texture(shm, currentTextureCoords).r;
	// Waiting for loops
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	if (heightFromTexture > curLayerHeight) { curLayerHeight += layerHeight; currentTextureCoords -= dtex; heightFromTexture = texture(shm, currentTextureCoords).r; }
	// }
	
	vec2 texStep = dtex;
	vec2 prevTCoords = currentTextureCoords + texStep;
	// Heights for linear interpolation
	float nextH	= heightFromTexture - curLayerHeight;
	float prevH	= texture(shm, prevTCoords).r - curLayerHeight + layerHeight;
	float weight = nextH / (nextH - prevH);
	// Interpolation of texture coordinates
	vec2 finalTexCoords = prevTCoords * weight + currentTextureCoords * (1.0 - weight);
	// Interpolation of depth values
	parallaxHeight = curLayerHeight + prevH * weight + nextH * (1.0 - weight);
	return finalTexCoords;
}
float parallaxShadow(vec3 L, vec2 initialTexCoord, float initialHeight) {
	float parallaxScale = -0.06 * heightStrength;
	float shadowMultiplier = 1.0;
	// Calculate lighting only for surface oriented to the light source
	if (dot(vec3(0, 0, 1), L) > 0) {
		shadowMultiplier = 0;
		float numSamplesUnderSurface = 0;
		float numLayers = mix(maxLayers, minLayers, abs(dot(vec3(0, 0, 1), L)));
		float layerHeight = initialHeight / numLayers;
		vec2 texStep = parallaxScale * L.xy / L.z / numLayers;

		float currentLayerHeight = initialHeight - layerHeight;
		vec2 currentTextureCoords = initialTexCoord + texStep;
		float heightFromTexture	= texture(shm, currentTextureCoords).r;
		int stepIndex = 1;

		// while(currentLayerHeight > 0) {
		if (currentLayerHeight > 0) {
			if(heightFromTexture < currentLayerHeight) {
				numSamplesUnderSurface += 1;
				float newShadowMultiplier = (currentLayerHeight - heightFromTexture) * (1.0 - stepIndex / numLayers);
				shadowMultiplier = max(shadowMultiplier, newShadowMultiplier);
			}
			stepIndex += 1;
			currentLayerHeight -= layerHeight;
			currentTextureCoords += texStep;
			heightFromTexture = texture(shm, currentTextureCoords).r;
		}
		// ...
		
		// Shadowing factor should be 1 if there were no points under the surface
		if(numSamplesUnderSurface < 1) shadowMultiplier = 1;
		else shadowMultiplier = 1.0 - shadowMultiplier;
	}
	return shadowMultiplier;
}
#endif

void main() {
#ifdef _Tex
	vec2 newCoord = texCoord;
#endif	
	
#ifdef _HMTex
	vec3 tanv = normalize(tanEyeDir);
	vec3 tanl = normalize(tanLightDir);
	newCoord = parallaxMapping(tanv, texCoord);
	float shadowMultiplier = 1.0;//parallaxShadow(tanl, newCoord, parallaxHeight - 0.001);
#endif
	
#ifdef _NMTex
	vec3 n = (texture(snormal, newCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif
#ifdef _NMStr
	n *= normalStrength;
#endif

	vec3 baseColor = matColor.rgb;
#ifdef _AMTex
	vec4 texel = texture(salbedo, newCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2)); // Variant 1
	baseColor *= texel.rgb;
#endif
	// baseColor = pow(baseColor, vec3(2.2)); // Variant 2

#ifdef _MMTex
	float metalness = texture(smm, newCoord).r;
#endif

#ifdef _RMTex
	float roughness = texture(srm, newCoord).r;
#endif
#ifdef _RMStr
	roughness *= roughnessStrength;
#endif
		
#ifdef _OMTex
	float occ = texture(som, newCoord).r;
#else
	float occ = occlusion; 
#endif

#ifdef _HMTex
	occ *= shadowMultiplier;
#endif
	
	// Pack normal
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);

#ifdef _Probes
	float mask_probe = probeID;
	if (probeID > 0) { // Non-global probe attached
		const float eps = 0.00001;
		// Distance of vertex located inside probe to probe bounds
		float dist = distanceBox(mpos.xyz, probeVolumeCenter, probeVolumeSize);
		// Blend local probe with global probe		
		if (dist > -0.1) {
			const float blending = 10.0;
			float clampres = clamp((0.1 + dist) * blending, 0.0, 1.0 - eps);
			mask_probe += clampres;
		}
		if (dist > 0) mask_probe = 0;
	}
	outColor[0] = vec4(n.xy, packFloat(roughness, metalness), mask_probe);
#else
	outColor[0] = vec4(n.xy, packFloat(roughness, metalness), mask);
#endif
	outColor[1] = vec4(baseColor.rgb, occ);

#ifdef _Veloc
	vec2 posa = (mvppos.xy / mvppos.w) * 0.5 + 0.5;
	vec2 posb = (prevmvppos.xy / prevmvppos.w) * 0.5 + 0.5;
	outColor[2].rg = vec2(posa - posb);
#endif
}
