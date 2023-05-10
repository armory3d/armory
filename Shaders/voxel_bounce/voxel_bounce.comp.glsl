
#version 450

#include "compiled.inc"
#include "std/conetrace.glsl"
#include "std/gbuffer.glsl"
#include "std/imageatomic.glsl"

// layout (local_size_x = 4, local_size_y = 4, local_size_z = 4) in;
layout (local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

uniform layout(binding = 0, rgba8) readonly image3D voxelsNor;
uniform layout(binding = 1) sampler3D voxelsFrom;
uniform layout(binding = 2, r32ui) uimage3D voxelsTo;

void main() {

    vec4 col = texelFetch(voxelsFrom, ivec3(gl_GlobalInvocationID.xyz), 0);
    if (col.a == 0.0) {
        // imageStore(voxelsTo, ivec3(gl_GlobalInvocationID.xyz), col);
    	imageAtomicAdd(voxelsTo, ivec3(gl_GlobalInvocationID.xyz), convVec4ToRGBA8(col));
    	return;
    }

    const vec3 hres = voxelgiResolution / 2;
    vec3 voxpos = (gl_GlobalInvocationID.xyz - hres) / hres;
    vec3 wposition = voxpos * voxelgiHalfExtents;

    vec3 wnormal = imageLoad(voxelsNor, ivec3(gl_GlobalInvocationID.xyz)).rgb;
    //vec3 wnormal = normalize(decNor(unor));

    col.rgb += traceDiffuse(voxpos, wnormal, voxelsFrom).rgb * voxelgiDiff * 0.5;
    col = clamp(col, vec4(0.0), vec4(1.0));

    imageAtomicAdd(voxelsTo, ivec3(gl_GlobalInvocationID.xyz), convVec4ToRGBA8(col * 255));
}
