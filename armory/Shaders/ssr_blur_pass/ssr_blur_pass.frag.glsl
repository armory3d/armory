#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;

uniform vec2 dirInv;

in vec2 texCoord;
out vec4 fragColor;

const float blurWeights[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
const float discardThreshold = 0.95;

vec4 doBlur(const float blurWeight, const int pos, const vec3 nor, const vec2 texCoord) {
    const float posadd = float(pos) + 0.5;

    vec4 col1 = textureLod(tex, texCoord + pos * dirInv, 0.0);
    vec3 nor1 = getNor(textureLod(gbuffer0, texCoord + pos * dirInv, 0.0).rg);
    float influenceFactor = step(discardThreshold, dot(nor1, nor));
    col1.rgb *= influenceFactor;

    vec4 col2 = textureLod(tex, texCoord - pos * dirInv, 0.0);
    vec3 nor2 = getNor(textureLod(gbuffer0, texCoord - pos * dirInv, 0.0).rg);
    influenceFactor = step(discardThreshold, dot(nor2, nor));
    col2.rgb *= influenceFactor;

    return (col1 + col2) * blurWeight;
}

void main() {
    vec3 nor = getNor(textureLod(gbuffer0, texCoord, 0.0).rg);

    fragColor = textureLod(tex, texCoord, 0.0) * blurWeights[0];
    for (int i = 1; i < 5; i++) {
        fragColor += doBlur(blurWeights[i], i, nor, texCoord);
    }
}