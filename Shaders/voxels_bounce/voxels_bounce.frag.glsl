#version 450

#include "compiled.inc"
#include "std/conetrace.glsl"
#include "std/gbuffer.glsl"

uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform int clipmapLevel;

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbuffer_refraction;

uniform sampler3D voxels;
uniform layout(rgba8) image3D voxelsBounce;

in vec2 texCoord;
in vec3 viewRay;

void main() {
	vec4 col = vec4(0.0);
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, roughness, metallic/matid
	float roughness = g0.b;
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec4 g1 = textureLod(gbuffer1, texCoord, 0.0);
    float spec = unpackFloat2(g1.a).y;

	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 p = getPos(eye, eyeLook, viewRay, depth, cameraProj);
	vec3 v = normalize(eye - p);

	float voxelSize = voxelgiVoxelSize * pow(2.0, clipmapLevel);
    vec3 clipmap_center = floor(eye + eyeLook);

	//trace cones
	col += traceDiffuse(p, n, voxels, clipmap_center);
	if(roughness < 1.0 && spec > 0.0)
        col += traceSpecular(p, n, voxels, -v, roughness, clipmap_center);

	#ifdef _VoxelRefract
    vec4 gr = textureLod(gbuffer_refraction, texCoord, 0.0);
    float ior = gr.x;
    float opacity = gr.y;
    if(opacity < 1.0)
        col.rgb = mix(traceRefraction(p, n, voxels, -v, ior, roughness, clipmap_center), col.rgb, opacity);
    #endif

	//write to voxelsBounce
    vec3 uvw = ((p - clipmap_center) / voxelSize * 1.0 / voxelgiResolution.x) * 0.5 + 0.5;
    uvw.y = uvw.y + clipmapLevel;
	uvw *= voxelgiResolution.x;

    imageStore(voxelsBounce, ivec3(uvw), col);
}
