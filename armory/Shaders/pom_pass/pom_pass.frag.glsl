#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbuffer0; // Normal (octahedral encoded)
uniform sampler2D gbufferD; // Depth
uniform sampler2D texColor; // Emissive/color

uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

uniform float pomStrength;
uniform float pomHeight;
uniform int pomMaxSteps;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 getNormal(sampler2D tex, vec2 coord) {
    vec2 enc = textureLod(tex, coord, 0.0).rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    return normalize(V3 * n);
}

vec3 getPosView(vec3 ray, float depth, vec2 proj) {
    float z = depth * 2.0 - 1.0;
    float x = (2.0 * ray.x / proj.x - 1.0) * z;
    float y = (2.0 * ray.y / proj.y - 1.0) * z;
    return vec3(x, y, z) * ray.z;
}

vec2 getProjectedCoord(vec3 hitCoord) {
    vec4 projectedCoord = P * vec4(hitCoord, 1.0);
    projectedCoord.xy /= projectedCoord.w;
    projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
    #ifdef _InvY
    projectedCoord.y = 1.0 - projectedCoord.y;
    #endif
    return projectedCoord.xy;
}

void main() {
    vec3 n = getNormal(gbuffer0, texCoord);
    float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    vec3 vpos = getPosView(viewRay, d, cameraProj);

    // Get tangent space basis
    vec3 t1 = normalize(cross(n, vec3(0.0, 0.0, 1.0)));
    if (length(t1) < 0.001) t1 = normalize(cross(n, vec3(0.0, 1.0, 0.0)));
    vec3 t2 = cross(n, t1);
    mat3 TBN = mat3(t1, t2, n);

    // Parallax offset direction (from viewer)
    vec2 projXY = vec2(
        (2.0 * viewRay.x / cameraProj.x - 2.0 * 0.5) / (-viewRay.z),
        (2.0 * viewRay.y / cameraProj.y - 2.0 * 0.5) / (-viewRay.z)
    );
    #ifdef _InvY
    projXY.y = -projXY.y;
    #endif
    vec2 offset = projXY * pomHeight;
    vec2 texCoords = texCoord;
    vec2 prevTexCoords = texCoord;

    // Steep parallax ray marching
    float zIter = 1.0;
    float zDelta = 1.0 / float(pomMaxSteps);
    float stepSize = 0.02;

    for (int i = 0; i < 32; i++) {
        if (i >= pomMaxSteps) break;

        zIter -= zDelta;
        texCoords = prevTexCoords + offset * zIter;

        float currZ = textureLod(gbufferD, texCoords, 0.0).r * 2.0 - 1.0;
        float depthVal = getPosView(viewRay, currZ, cameraProj).z;

        if (zIter < depthVal * 0.01 + 0.001) {
            break;
        }
        prevTexCoords = texCoords;
    }

    // Self-shadowing: check if surface occludes light from above
    float shadow = 0.0;
    vec3 lightDir = normalize(vec3(0.5, 1.0, 0.3));
    vec3 worldNormal = TBN * getNormal(gbuffer0, prevTexCoords).xyz;
    float NdotL = max(dot(worldNormal, lightDir), 0.0);

    // Simple self-shadow test
    for (int i = 0; i < 8; i++) {
        float t = float(i) * 0.125;
        vec3 shadowPos = vpos + lightDir * t * 0.5;
        vec4 shadowClip = P * vec4(shadowPos, 1.0);
        shadowClip.xy /= shadowClip.w;
        shadowClip.xy = shadowClip.xy * 0.5 + 0.5;
        if (shadowClip.x > 0.0 && shadowClip.x < 1.0 && shadowClip.y > 0.0 && shadowClip.y < 1.0) {
            float shadowDepth = textureLod(gbufferD, shadowClip.xy, 0.0).r * 2.0 - 1.0;
            float shadowWorldZ = getPosView(viewRay, shadowDepth, cameraProj).z;
            if (shadowWorldZ > shadowPos.z) {
                shadow += 1.0;
            }
        }
    }
    shadow = 1.0 - shadow / 8.0;

    // Sample color at final tex coords
    vec3 baseColor = textureLod(texColor, prevTexCoords, 0.0).rgb;
    vec3 surfaceNormal = TBN * getNormal(gbuffer0, prevTexCoords).xyz;
    float diffuse = max(dot(surfaceNormal, normalize(lightDir)), 0.0);

    fragColor = vec4(baseColor * (0.3 + 0.7 * diffuse) * shadow * pomStrength, 1.0);
}