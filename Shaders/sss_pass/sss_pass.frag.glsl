#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D tex;
uniform sampler2D gbuffer_refraction;
uniform sampler2D gbuffer_subsurface_1;
uniform sampler2D gbuffer_subsurface_2;

uniform vec2 dir;
uniform vec2 cameraProj;

in vec2 texCoord;
out vec4 fragColor;

// Gaussian function for blur weights
float gaussian(float x, float sigma) {
    return exp(-0.5 * (x * x) / (sigma * sigma)) / (sigma * sqrt(2.0 * 3.141592653589793));
}

// Function to perform SSS blur
vec4 SSSSBlur(vec3 subsurface_color, vec3 subsurface_radius, float ior) {
    const int SSSS_N_SAMPLES = 11;
    vec4 kernel[SSSS_N_SAMPLES];
    float sigma = 0.2;
    float totalWeight = 0.0;

    // Generate Gaussian weights and initialize kernel
    for (int i = 0; i < SSSS_N_SAMPLES; i++) {
        float x = (float(i) - float(SSSS_N_SAMPLES / 2)) / float(SSSS_N_SAMPLES / 2);
        kernel[i] = vec4(subsurface_color, 0.0); // Initialize with subsurface radius
        kernel[i].w = gaussian(x, sigma); // Gaussian weight
        totalWeight += kernel[i].w;
    }

    // Normalize weights and scale RGB with radius
    for (int i = 0; i < SSSS_N_SAMPLES; i++) {
        kernel[i].rgb *= subsurface_radius;
        kernel[i].w /= totalWeight;
    }

    vec4 colorM = textureLod(tex, texCoord, 0.0);

    // Fetch linear depth of current pixel
    float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    float depthM = cameraProj.y / (depth - cameraProj.x);

    float stepSize = cameraProj.y / depthM;
    stepSize /= (SSSS_N_SAMPLES - 1);

    // Accumulate the center sample:
    vec4 colorBlurred = colorM * kernel[SSSS_N_SAMPLES / 2];

    // Accumulate the other samples with offset
    for (int i = 0; i < SSSS_N_SAMPLES; i++) {
        if (i != SSSS_N_SAMPLES / 2) {
            float offsetScale = (float(i) - float(SSSS_N_SAMPLES / 2)) / float(SSSS_N_SAMPLES / 2);
            vec2 offset = texCoord + offsetScale * dir * stepSize;
            vec4 color = textureLod(tex, offset, 0.0);
            colorBlurred.rgb += kernel[i].w * kernel[i].xyz * color.rgb;
        }
    }

    return colorBlurred;
}

void main() {
    float metallic;
    uint matid;
    unpackFloatInt16(textureLod(gbuffer0, texCoord, 0.0).a, metallic, matid);

	float opacity = textureLod(gbuffer_refraction, texCoord, 0.0).y;
    vec4 finalColor = textureLod(tex, texCoord, 0.0); // Default to background texture

    if (matid == 2) {
        vec3 subsurface_color = textureLod(gbuffer_subsurface_1, texCoord, 0.0).rgb;
        vec4 subsurface_data = textureLod(gbuffer_subsurface_2, texCoord, 0.0);
        vec3 subsurface_radius = subsurface_data.rgb;
        vec2 ior_scale = unpackFloat2(subsurface_data.a);

        // Perform SSS blur and clamp result
        vec4 sssColor = clamp(SSSSBlur(subsurface_color, subsurface_radius, ior_scale.x), 0.0, 1.0);

        // Blend SSS color with background
        finalColor = mix(finalColor, sssColor, ior_scale.y);
    }

    fragColor = finalColor;
}
