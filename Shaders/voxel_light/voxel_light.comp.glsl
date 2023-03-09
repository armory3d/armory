#version 450

// layout (local_size_x = 4, local_size_y = 4, local_size_z = 4) in;
layout (local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/shadows.glsl"
#include "std/imageatomic.glsl"
#include "std/light.glsl"

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform int lightType;
uniform vec3 lightDir;
uniform vec2 spotData;
#ifdef _ShadowMap
uniform int lightShadow;
uniform float shadowsBias;
uniform mat4 LWVP;
#endif

uniform layout(binding = 0, r32ui) readonly uimage3D voxelsOpac;
uniform layout(binding = 1, r32ui) readonly uimage3D voxelsNor;
// uniform layout(binding = 2, rgba8) writeonly image3D voxels;
uniform layout(binding = 2, rgba16) image3D voxels;
#ifdef _ShadowsMap
uniform layout(binding = 3) sampler2D shadowMap;
uniform layout(binding = 4) samplerCube shadowMapCube;
#endif

void main() {
    uint ucol = imageLoad(voxelsOpac, ivec3(gl_GlobalInvocationID.xyz)).r;
    vec4 col = convRGBA8ToVec4(ucol);

    const vec3 hres = voxelgiResolution / 2;
    vec3 wposition = ((gl_GlobalInvocationID.xyz - hres) / hres) * voxelgiHalfExtents;

    float svisibility = 1.0;

    if (lightShadow == 1) {
        vec4 lightPosition = LWVP * vec4(wposition, 1.0);
        vec3 lPos = lightPosition.xyz / lightPosition.w;
        svisibility *= shadowTest(shadowMap, lPos, shadowsBias, shadowmapSize);
    }
    /*
    for (int i = 0; i < min(numLights, maxLightsCluster); i++) {
        float svisibility = 1.0;
        int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);
        svisibility *= attenuate(distance(wposition, lightsArray[li * 3].xyz));
        #ifdef _LTC
        if (li == 0) {
            vec4 lPos = LWVPSpot[0] * vec4(wposition + wnormal * lightsArray[li * 3 + 2].x * 10, 1.0);
            svisibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
        }
        else if (li == 1) {
            vec4 lPos = LWVPSpot[1] * vec4(wposition + wnormal * lightsArray[li * 3 + 2].x * 10, 1.0);
            svisibility *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
        }
        else if (li == 2) {
            vec4 lPos = LWVPSpot[2] * vec4(wposition + wnormal * lightsArray[li * 3 + 2].x * 10, 1.0);
            svisibility *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
        }
        else if (li == 3) {
            vec4 lPos = LWVPSpot[3] * vec4(wposition + wnormal * lightsArray[li * 3 + 2].x * 10, 1.0);
            svisibility *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
        }
        continue;
        #ifdef _Spot
        if (lightsArray[li * 3 + 2].y != 0.0) { //if isSpot')
            vec3 ld = lightsArray[li * 3].xyz - wposition;
            vec3 l = normalize(ld);
            svisibility *= spotlightMask(-l, lightsArraySpot[li].xyz, lightsArraySpot[li * 2 + 1].xyz, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w), lightsArray[li * 3 + 2].y, lightsArraySpot[li].w);
            vec4 lPos = LWVPSpotArray[li] * vec4(wposition + n * lightsArray[li * 3 + 2].x * 10, 1.0);
            #ifdef _ShadowMapAtlas
                svisibility *= shadowTest(
                #ifndef _SingleAtlas
                shadowMapAtlasSpot
                #else
                shadowMapAtlas
                #endif
                ,lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x
            );
            #else
            if      (li == 0) svisibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
            else if (li == 1) svisibility *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
            else if (li == 2) svisibility *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
            else if (li == 3) svisibility *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, lightsArray[li * 3 + 2].x);
            #endif
            continue;
        }
        #endif
        vec3 ld = lightsArray[li * 3].xyz - wposition; // lp
        vec3 l = normalize(ld);
        #ifdef _ShadowMapAtlas
        svisibility *= PCFFakeCube(
        #ifndef _SingleAtlas
        shadowMapAtlasPoint
        #else
        shadowMapAtlas
        #endif
        , ld, -l, lightsArray[li * 3 + 2].x, lightProj, wnormal, li);
        #else
        if      (li == 0) svisibility *= PCFCube(shadowMapPoint[0], ld, -l, lightsArray[li * 3 + 2].x, lightProj, wnormal);
        else if (li == 1) svisibility *= PCFCube(shadowMapPoint[1], ld, -l, lightsArray[li * 3 + 2].x, lightProj, wnormal);
        else if (li == 2) svisibility *= PCFCube(shadowMapPoint[2], ld, -l, lightsArray[li * 3 + 2].x, lightProj, wnormal);
        else if (li == 3) svisibility *= PCFCube(shadowMapPoint[3], ld, -l, lightsArray[li * 3 + 2].x, lightProj, wnormal);
        #endif
        continue;
    }
    */
    col += svisibility;
    imageStore(voxels, ivec3(gl_GlobalInvocationID.xyz), col);
}
