//Transparent shadow implemented by Yvain Douard with reference:
//https://wickedengine.net/2018/01/easy-transparent-shadow-maps/comment-page-1/

#ifndef _SHADOWS_GLSL_
#define _SHADOWS_GLSL_

#include "compiled.inc"

#ifdef _CSM
uniform vec4 casData[shadowmapCascades * 4 + 4];
#endif

#ifdef _SMSizeUniform
uniform vec2 smSizeUniform;
#endif

#ifdef _ShadowMap
	#ifdef _Clusters
		#ifdef _ShadowMapAtlas
			uniform vec4 pointLightDataArray[maxLightsCluster * 6];
		#endif
	#endif
#endif

#ifdef _ShadowMapAtlas
// https://www.khronos.org/registry/OpenGL/specs/gl/glspec20.pdf // p:168
// https://www.gamedev.net/forums/topic/687535-implementing-a-cube-map-lookup-function/5337472/
vec2 sampleCube(vec3 dir, out int faceIndex) {
	vec3 dirAbs = abs(dir);
	float ma;
	vec2 uv;
	if(dirAbs.z >= dirAbs.x && dirAbs.z >= dirAbs.y) {
		faceIndex = dir.z < 0.0 ? 5 : 4;
		ma = 0.5 / dirAbs.z;
		uv = vec2(dir.z < 0.0 ? -dir.x : dir.x, -dir.y);
	}
	else if(dirAbs.y >= dirAbs.x) {
		faceIndex = dir.y < 0.0 ? 3 : 2;
		ma = 0.5 / dirAbs.y;
		uv = vec2(dir.x, dir.y < 0.0 ? -dir.z : dir.z);
	}
	else {
		faceIndex = dir.x < 0.0 ? 1 : 0;
		ma = 0.5 / dirAbs.x;
		uv = vec2(dir.x < 0.0 ? dir.z : -dir.z, -dir.y);
	}
	// downscale uv a little to hide seams
	// transform coordinates from clip space to texture space
	#ifndef _FlipY
		return uv * 0.9976 * ma + 0.5;
	#else
		#ifdef HLSL
			return uv * 0.9976 * ma + 0.5;
		#else
			return vec2(uv.x * ma, uv.y * -ma) * 0.9976 + 0.5;
		#endif
	#endif
}
#endif

vec3 PCF(sampler2DShadow shadowMap, sampler2D shadowMapTransparent, const vec2 uv, const float compare, const vec2 smSize, const bool transparent) {
	vec3 result = vec3(0.0);
	result.x = texture(shadowMap, vec3(uv + (vec2(-1.0, -1.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(-1.0, 0.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(-1.0, 1.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(0.0, -1.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv, compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(0.0, 1.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(1.0, -1.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(1.0, 0.0) / smSize), compare));
	result.x += texture(shadowMap, vec3(uv + (vec2(1.0, 1.0) / smSize), compare));
	result = result.xxx / 9.0;

	if (transparent == false) {
		vec4 shadowmap_transparent = texture(shadowMapTransparent, uv);
		if (shadowmap_transparent.a < compare)
			result *= shadowmap_transparent.rgb;
	}

	return result;
}

float lpToDepth(vec3 lp, const vec2 lightProj) {
	lp = abs(lp);
	float zcomp = max(lp.x, max(lp.y, lp.z));
	zcomp = lightProj.x - lightProj.y / zcomp;
	return zcomp * 0.5 + 0.5;
}

vec3 PCFCube(samplerCubeShadow shadowMapCube, samplerCube shadowMapCubeTransparent, const vec3 lp, vec3 ml, const float bias, const vec2 lightProj, const vec3 n, const bool transparent) {
	const float s = shadowmapCubePcfSize; // TODO: incorrect...
	float compare = lpToDepth(lp, lightProj) - bias * 1.5;
	ml = ml + n * bias * 20;
	#ifdef _InvY
	ml.y = -ml.y;
	#endif
	vec3 result = vec3(0.0);
	result.x = texture(shadowMapCube, vec4(ml, compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(s, s, s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(-s, s, s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(s, -s, s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(s, s, -s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(-s, -s, s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(s, -s, -s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(-s, s, -s), compare));
	result.x += texture(shadowMapCube, vec4(ml + vec3(-s, -s, -s), compare));
	result = result.xxx / 9.0;

	if (transparent == false) {
		vec4 shadowmap_transparent = texture(shadowMapCubeTransparent, ml);
		if (shadowmap_transparent.a < compare)
			result *= shadowmap_transparent.rgb;
	}

	return result;
}

#ifdef _ShadowMapAtlas
// transform "out-of-bounds" coordinates to the correct face/coordinate system
// https://www.khronos.org/opengl/wiki/File:CubeMapAxes.png
vec2 transformOffsetedUV(const int faceIndex, out int newFaceIndex, vec2 uv) {
	if (uv.x < 0.0) {
		if (faceIndex == 0) { // X+
			newFaceIndex = 4; // Z+
		}
		else if (faceIndex == 1) { // X-
			newFaceIndex = 5; // Z-
		}
		else if (faceIndex == 2) { // Y+
			newFaceIndex = 1; // X-
		}
		else if (faceIndex == 3) { // Y-
			newFaceIndex = 1; // X-
		}
		else if (faceIndex == 4) { // Z+
			newFaceIndex = 1; // X-
		}
		else { // Z-
			newFaceIndex = 0; // X+
		}
		uv = vec2(1.0 + uv.x, uv.y);
	}
	else if (uv.x > 1.0)  {
		if (faceIndex == 0) { // X+
			newFaceIndex = 5; // Z-
		}
		else if (faceIndex == 1) { // X-
			newFaceIndex = 4; // Z+
		}
		else if (faceIndex == 2) { // Y+
			newFaceIndex = 0; // X+
		}
		else if (faceIndex == 3) { // Y-
			newFaceIndex = 0; // X+
		}
		else if (faceIndex == 4) { // Z+
			newFaceIndex = 0; // X+
		}
		else { // Z-
			newFaceIndex = 1; // X-
		}
		uv = vec2(1.0 - uv.x, uv.y);
	}
	else if (uv.y < 0.0) {
		if (faceIndex == 0) { // X+
			newFaceIndex = 2; // Y+
		}
		else if (faceIndex == 1) { // X-
			newFaceIndex = 2; // Y+
		}
		else if (faceIndex == 2) { // Y+
			newFaceIndex = 5; // Z-
		}
		else if (faceIndex == 3) { // Y-
			newFaceIndex = 4; // Z+
		}
		else if (faceIndex == 4) { // Z+
			newFaceIndex = 2; // Y+
		}
		else { // Z-
			newFaceIndex = 2; // Y+
		}
		uv = vec2(uv.x, 1.0 + uv.y);
	}
	else if (uv.y > 1.0) {
		if (faceIndex == 0) { // X+
			newFaceIndex = 3; // Y-
		}
		else if (faceIndex == 1) { // X-
			newFaceIndex = 3; // Y-
		}
		else if (faceIndex == 2) { // Y+
			newFaceIndex = 4; // Z+
		}
		else if (faceIndex == 3) { // Y-
			newFaceIndex = 5; // Z-
		}
		else if (faceIndex == 4) { // Z+
			newFaceIndex = 3; // Y-
		}
		else { // Z-
			newFaceIndex = 3; // Y-
		}
		uv = vec2(uv.x, 1.0 - uv.y);
	} else {
		newFaceIndex = faceIndex;
	}
	// cover corner cases too
	return uv;
}

vec3 PCFFakeCube(sampler2DShadow shadowMap, sampler2D shadowMapTransparent, const vec3 lp, vec3 ml, const float bias, const vec2 lightProj, const vec3 n, const int index, const bool transparent) {
	const vec2 smSize = smSizeUniform; // TODO: incorrect...
	const float compare = lpToDepth(lp, lightProj) - bias * 1.5;
	ml = ml + n * bias * 20;

	int faceIndex = 0;
	const int lightIndex = index * 6;
	const vec2 uv = sampleCube(ml, faceIndex);

	vec4 pointLightTile = pointLightDataArray[lightIndex + faceIndex]; // x: tile X offset, y: tile Y offset, z: tile size relative to atlas
	vec2 uvtiled = pointLightTile.z * uv + pointLightTile.xy;
	#ifdef _FlipY
	uvtiled.y = 1.0 - uvtiled.y; // invert Y coordinates for direct3d coordinate system
	#endif

	if (any(lessThan(uvtiled, vec2(0.0))) || any(greaterThan(uvtiled, vec2(1.0)))) {
		return vec3(1.0); // Or handle edge cases differently
	}

	vec3 result = vec3(0.0);
	// In PCFFakeCube(), modify the sampling pattern to be more robust:
	const vec2 offsets[9] = vec2[](
		vec2(0, 0),
		vec2(1, 0), vec2(-1, 0), vec2(0, 1), vec2(0, -1),
		vec2(1, 1), vec2(-1, 1), vec2(1, -1), vec2(-1, -1)
	);

	for (int i = 0; i < 9; i++) {
		vec2 sampleUV = uv + offsets[i] / smSize;
		int newFaceIndex;
		vec2 transformedUV = transformOffsetedUV(faceIndex, newFaceIndex, sampleUV);
		pointLightTile = pointLightDataArray[lightIndex + newFaceIndex];
		uvtiled = pointLightTile.z * transformedUV + pointLightTile.xy;
		#ifdef _FlipY
		uvtiled.y = 1.0 - uvtiled.y;
		#endif
		result.x += texture(shadowMap, vec3(uvtiled, compare));
	}
	result = result.xxx / 9.0;

	pointLightTile = pointLightDataArray[lightIndex + faceIndex]; // x: tile X offset, y: tile Y offset, z: tile size relative to atlas
	uvtiled = pointLightTile.z * uv + pointLightTile.xy;
	#ifdef _FlipY
	uvtiled.y = 1.0 - uvtiled.y; // invert Y coordinates for direct3d coordinate system
	#endif

	if (transparent == false) {
		vec4 shadowmap_transparent = texture(shadowMapTransparent, uvtiled);
		if (shadowmap_transparent.a < compare)
			result *= shadowmap_transparent.rgb;
	}

	return result;
}
#endif

vec3 shadowTest(sampler2DShadow shadowMap, sampler2D shadowMapTransparent, const vec3 lPos, const float shadowsBias, const bool transparent) {
	#ifdef _SMSizeUniform
	vec2 smSize = smSizeUniform;
	#else
	const vec2 smSize = shadowmapSize;
	#endif
	if (lPos.x < 0.0 || lPos.y < 0.0 || lPos.x > 1.0 || lPos.y > 1.0) return vec3(1.0);
	return PCF(shadowMap, shadowMapTransparent, lPos.xy, lPos.z - shadowsBias, smSize, transparent);
}

#ifdef _CSM
mat4 getCascadeMat(const float d, out int casi, out int casIndex) {
	const int c = shadowmapCascades;

	// Get cascade index
	// TODO: use bounding box slice selection instead of sphere
	const vec4 ci = vec4(float(c > 0), float(c > 1), float(c > 2), float(c > 3));
	// int ci;
	// if (d < casData[c * 4].x) ci = 0;
	// else if (d < casData[c * 4].y) ci = 1 * 4;
	// else if (d < casData[c * 4].z) ci = 2 * 4;
	// else ci = 3 * 4;
	// Splits
	vec4 comp = vec4(
		float(d > casData[c * 4].x),
		float(d > casData[c * 4].y),
		float(d > casData[c * 4].z),
		float(d > casData[c * 4].w));
	casi = int(min(dot(ci, comp), c));

	// Get cascade mat
	casIndex = casi * 4;

	return mat4(
		casData[casIndex    ],
		casData[casIndex + 1],
		casData[casIndex + 2],
		casData[casIndex + 3]);

	// if (casIndex == 0) return mat4(casData[0], casData[1], casData[2], casData[3]);
	// ..
}

vec3 shadowTestCascade(sampler2DShadow shadowMap, sampler2D shadowMapTransparent, const vec3 eye, const vec3 p, const float shadowsBias, const bool transparent) {
	#ifdef _SMSizeUniform
	vec2 smSize = smSizeUniform;
	#else
	const vec2 smSize = shadowmapSize * vec2(shadowmapCascades, 1.0);
	#endif
	const int c = shadowmapCascades;
	float d = distance(eye, p);

	int casi;
	int casIndex;
	mat4 LWVP = getCascadeMat(d, casi, casIndex);

	vec4 lPos = LWVP * vec4(p, 1.0);
	lPos.xyz /= lPos.w;

	vec3 visibility = vec3(1.0);
	if (lPos.w > 0.0) visibility = PCF(shadowMap, shadowMapTransparent, lPos.xy, lPos.z - shadowsBias, smSize, transparent);

	// Blend cascade
	// https://github.com/TheRealMJP/Shadows
	const float blendThres = 0.15;
	float nextSplit = casData[c * 4][casi];
	float splitSize = casi == 0 ? nextSplit : nextSplit - casData[c * 4][casi - 1];
	float splitDist = (nextSplit - d) / splitSize;
	if (splitDist <= blendThres && casi != c - 1) {
		int casIndex2 = casIndex + 4;
		mat4 LWVP2 = mat4(
			casData[casIndex2    ],
			casData[casIndex2 + 1],
			casData[casIndex2 + 2],
			casData[casIndex2 + 3]);

		vec4 lPos2 = LWVP2 * vec4(p, 1.0);
		lPos2.xyz /= lPos2.w;
		vec3 visibility2 = vec3(1.0);
		if (lPos2.w > 0.0) visibility2 = PCF(shadowMap, shadowMapTransparent, lPos2.xy, lPos2.z - shadowsBias, smSize, transparent);

		float lerpAmt = smoothstep(0.0, blendThres, splitDist);
		return mix(visibility2, visibility, lerpAmt);
	}
	return visibility;

	// Visualize cascades
	// if (ci == 0) albedo.rgb = vec3(1.0, 0.0, 0.0);
	// if (ci == 4) albedo.rgb = vec3(0.0, 1.0, 0.0);
	// if (ci == 8) albedo.rgb = vec3(0.0, 0.0, 1.0);
	// if (ci == 12) albedo.rgb = vec3(1.0, 1.0, 0.0);
}
#endif
#endif
