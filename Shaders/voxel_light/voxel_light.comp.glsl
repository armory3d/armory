#version 450

layout (local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/imageatomic.glsl"

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform int lightType;
uniform vec3 lightDir;
uniform vec2 spotData;
#ifdef _ShadowMap
uniform int lightShadow;
uniform vec2 lightProj;
uniform float shadowsBias;
uniform mat4 LVP;
#ifdef _ShadowMapAtlas
uniform int index;
uniform vec4 pointLightDataArray[maxLightsCluster * 6];
#endif
#endif

uniform float clipmaps[voxelgiClipmapCount * 10];
uniform int clipmapLevel;

uniform layout(r32ui) uimage3D voxelsLight;

#ifdef _ShadowMap
uniform sampler2DShadow shadowMap;
uniform sampler2DShadow shadowMapSpot;
#ifdef _ShadowMapAtlas
uniform sampler2DShadow shadowMapPoint;
#else
uniform samplerCubeShadow shadowMapPoint;
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

float lpToDepth(vec3 lp, const vec2 lightProj) {
	lp = abs(lp);
	float zcomp = max(lp.x, max(lp.y, lp.z));
	zcomp = lightProj.x - lightProj.y / zcomp;
	return zcomp * 0.5 + 0.5;
}

void main() {
	int res = voxelgiResolution.x;

	ivec3 dst = ivec3(gl_GlobalInvocationID.xyz);

	vec3 P = (gl_GlobalInvocationID.xyz + 0.5) / voxelgiResolution;
	P = P * 2.0 - 1.0;
	P *= clipmaps[int(clipmapLevel * 10)];
	P *= voxelgiResolution;
	P += vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)]);

	vec4 light = vec4(0.0);

	float visibility;
	vec3 lp = lightPos - P;
	vec3 l;
	if (lightType == 0) { l = lightDir; visibility = 1.0; }
	else { l = normalize(lp); visibility = attenuate(distance(P, lightPos)); }

	// float dotNL = max(dot(wnormal, l), 0.0);
	// if (dotNL == 0.0) return;

#ifdef _ShadowMap
	if (lightShadow == 1) {
		vec4 lightPosition = LVP * vec4(P, 1.0);
		vec3 lPos = lightPosition.xyz / lightPosition.w;
		visibility = texture(shadowMap, vec3(lPos.xy, lPos.z - shadowsBias)).r;
	}
	else if (lightShadow == 2) {
		vec4 lightPosition = LVP * vec4(P, 1.0);
		vec3 lPos = lightPosition.xyz / lightPosition.w;
		visibility *= texture(shadowMapSpot, vec3(lPos.xy, lPos.z - shadowsBias)).r;
	}
	else if (lightShadow == 3) {
		#ifdef _ShadowMapAtlas
		int faceIndex = 0;
		const int lightIndex = index * 6;
		const vec2 uv = sampleCube(-l, faceIndex);
		vec4 pointLightTile = pointLightDataArray[lightIndex + faceIndex]; // x: tile X offset, y: tile Y offset, z: tile size relative to atlas
		vec2 uvtiled = pointLightTile.z * uv + pointLightTile.xy;
		#ifdef _FlipY
		uvtiled.y = 1.0 - uvtiled.y; // invert Y coordinates for direct3d coordinate system
		#endif
		visibility *= texture(shadowMapPoint, vec3(uvtiled, lpToDepth(lp, lightProj) - shadowsBias)).r;
		#else
		visibility *= texture(shadowMapPoint, vec4(-l, lpToDepth(lp, lightProj) - shadowsBias)).r;
		#endif
	}
#endif

	if (lightType == 2) {
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotData.x) {
			visibility *= smoothstep(spotData.y, spotData.x, spotEffect);
		}
	}

	light.rgb += visibility * lightColor;
	light = clamp(light, vec4(0.0), vec4(1.0));

	imageAtomicMax(voxelsLight, dst, convVec4ToRGBA8(light));
}
