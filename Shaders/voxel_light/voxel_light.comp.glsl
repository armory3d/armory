#version 450

// layout (local_size_x = 4, local_size_y = 4, local_size_z = 4) in;
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/shadows.glsl"
#include "std/imageatomic.glsl"

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform int lightType;
uniform vec3 lightDir;
uniform vec2 spotData;
uniform int clipmap_to_update;
#ifdef _ShadowMap
uniform int lightShadow;
uniform vec2 lightProj;
uniform float shadowsBias;
uniform mat4 LVP;
#endif

uniform layout(binding = 0, rgba8) readonly image3D voxelsOpac;
uniform layout(binding = 1, rgba8) readonly image3D voxelsNor;
uniform layout(binding = 2, rgba8) image3D voxels;
#ifdef _ShadowMap
uniform layout(binding = 3) sampler2DShadow shadowMap;
uniform layout(binding = 4) sampler2DShadow shadowMapSpot;
uniform layout(binding = 5) samplerCubeShadow shadowMapPoint;
#endif

void main() {
	vec3 texCoord = (gl_GlobalInvocationID.xyz / vec3(voxelgiResolution >> clipmap_to_update)) + vec3(0.5 / (voxelgiResolution >> clipmap_to_update));

	vec4 col = imageLoad(voxelsOpac, ivec3(texCoord));
	//vec4 col = convRGBA8ToVec4(ucol);
	if (col.a == 0.0) return;

	const vec3 hres = voxelgiResolution / 2;
	vec3 wposition = (texCoord - 0.5) * voxelgiHalfExtents * 2;

	vec3 wnormal = imageLoad(voxelsNor, ivec3(texCoord)).rgb;
	//vec3 wnormal = normalize(decNor(unor));
	//wposition -= wnormal * 0.01; // Offset

	float visibility;
	vec3 lp = lightPos - wposition;
	vec3 l;
	if (lightType == 0) { l = lightDir; visibility = 1.0; }
	else { l = normalize(lp); visibility = attenuate(distance(wposition, lightPos)); }

	float dotNL = max(dot(wnormal, l), 0.0);
	if (dotNL == 0.0) return;

#ifdef _ShadowMap
	if (lightShadow == 1) {
		vec4 lightPosition = LVP * vec4(wposition, 1.0);
		vec3 lPos = lightPosition.xyz / lightPosition.w;
		visibility = texture(shadowMap, vec3(lPos.xy, lPos.z - shadowsBias)).r;
	}
	else if (lightShadow == 2) {
		vec4 lightPosition = LVP * vec4(wposition, 1.0);
		vec3 lPos = lightPosition.xyz / lightPosition.w;
		visibility *= texture(shadowMapSpot, vec3(lPos.xy, lPos.z - shadowsBias)).r;
	}
	else if (lightShadow == 3) {
		visibility *= texture(shadowMapPoint, vec4(-l, lpToDepth(lp, lightProj) - shadowsBias)).r;
	}
#endif

	if (lightType == 2) {
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotData.x) {
			visibility *= smoothstep(spotData.y, spotData.x, spotEffect);
		}
	}

	col.rgb *= visibility * lightColor;// * dotNL;
	col = clamp(col, vec4(0.0), vec4(1.0));

	imageStore(voxels, ivec3(texCoord), col);
}
