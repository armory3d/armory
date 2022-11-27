#version 450

// Include functions for gbuffer operations (packFloat2() etc.)
#include "../std/gbuffer.glsl"

// World-space normal from the vertex shader stage
in vec3 wnormal;

// Gbuffer output. Deferred rendering uses the following layout:
// [0]: normal x      normal y      roughness     metallic/matID
// [1]: base color r  base color g  base color b  occlusion/specular
out vec4 fragColor[2];

void main() {
    // Pack normals into 2 components to fit into the gbuffer
    vec3 n = normalize(wnormal);
    n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);

    // Define PBR material values
    vec3 basecol = vec3(1.0);
    float roughness = 0.0;
    float metallic = 0.0;
    float occlusion = 1.0;
    float specular = 1.0;
    uint materialId = 0;

    // Store in gbuffer (see layout table above)
    fragColor[0] = vec4(n.xy, roughness, packFloatInt16(metallic, materialId));
    fragColor[1] = vec4(basecol.rgb, packFloat2(occlusion, specular));
}
