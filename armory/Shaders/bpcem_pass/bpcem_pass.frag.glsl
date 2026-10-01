#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbuffer0; // Normal (octahedral encoded)
uniform sampler2D gbufferD; // Depth
uniform sampler2D envMap; // Cube map texture (6-face concatenated or cubemap)

uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

uniform float bpcemStrength;

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

// Box-project: instead of using a single cube map direction,
// project the reflection direction onto the nearest box face
// of the environment cube for better edge handling
vec3 boxProjectEnvMap(vec3 worldRefl, vec3 worldPos, mat3 worldToBox) {
    // Transform reflection into box-local space
    vec3 boxRefl = worldToBox * worldRefl;

    // Find the dominant axis (which face of the box)
    float absX = abs(boxRefl.x);
    float absY = abs(boxRefl.y);
    float absZ = abs(boxRefl.z);

    vec2 uv;
    if (absX >= absY && absX >= absZ) {
        // +/- X face
        uv = vec2(-boxRefl.z / absX, -boxRefl.y / absX);
    } else if (absY >= absX && absY >= absZ) {
        // +/- Y face
        uv = vec2(boxRefl.x / absY, -boxRefl.z / absY);
    } else {
        // +/- Z face
        uv = vec2(boxRefl.x / absZ, boxRefl.y / absZ);
    }

    uv = uv * 0.5 + 0.5; // Normalize to [0,1]
    return uv;
}

void main() {
    vec3 n = getNormal(gbuffer0, texCoord);
    float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    vec3 vpos = getPosView(viewRay, d, cameraProj);

    // View-space normal
    vec3 viewNormal = V3 * n;

    // View-space reflection direction
    vec3 viewRefl = reflect(normalize(-viewRay), viewNormal);

    // Transform to world space
    vec3 worldRefl = inverse(V3) * viewRefl;
    vec3 worldPos = inverse(V3) * vpos;

    // Simple world-to-box transform (identity for now, can be customized)
    mat3 worldToBox = mat3(
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0
    );

    // Box-project the environment UV
    vec2 uv = boxProjectEnvMap(worldRefl, worldPos, worldToBox);

    // Sample environment map
    vec3 envColor = texture(envMap, uv).rgb;

    // Apply strength
    fragColor = vec4(envColor * bpcemStrength, 1.0);
}