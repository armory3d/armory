#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbuffer0; // Normal
uniform sampler2D gbufferD; // Depth
uniform sampler2D texColor; // Emissive/color buffer

uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

uniform float ddgiStrength;
uniform float ddgiAccumTime;

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

void main() {
    vec3 n = getNormal(gbuffer0, texCoord);
    float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    vec3 vpos = getPosView(viewRay, d, cameraProj);
    
    // Sample hemispherical diffuse GI using 8 directions
    vec3 gi = vec3(0.0);
    float samples = 0.0;
    
    // Simple hemisphere sampling for diffuse GI
    for (int i = 0; i < 8; i++) {
        float angle = float(i) * 3.14159265 / 4.0;
        vec3 dir = normalize(vec3(cos(angle), sin(angle), 1.0));
        
        // Project direction to screen space
        vec4 clipPos = P * vec4(vpos + dir * 0.5, 1.0);
        clipPos.xy /= clipPos.w;
        clipPos.xy = clipPos.xy * 0.5 + 0.5;
        
        if (clipPos.x > 0.0 && clipPos.x < 1.0 && clipPos.y > 0.0 && clipPos.y < 1.0) {
            vec3 sampleNormal = getNormal(gbuffer0, clipPos.xy);
            float dotProduct = max(dot(n, sampleNormal), 0.0);
            gi += textureLod(texColor, clipPos.xy, 0.0).rgb * dotProduct;
            samples += dotProduct;
        }
    }
    
    if (samples > 0.0) {
        gi /= samples;
    }
    
    // Accumulate over time for stable GI
    vec3 prevGI = textureLod(texColor, texCoord, 0.0).rgb;
    vec3 accumulated = mix(prevGI, gi, 1.0 / (1.0 + ddgiAccumTime));
    
    fragColor = vec4(accumulated * ddgiStrength, 1.0);
}