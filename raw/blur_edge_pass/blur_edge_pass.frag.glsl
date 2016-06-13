#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform vec2 dir;

in vec2 texCoord;

const float blurWeights[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);
const float discardThreshold = 0.95;

vec3 result = vec3(0.0);

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec3 getNor(vec2 enc) {
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);
    return n;
}

float doBlur(float blurWeight, int pos, vec3 nor) {
    vec2 texstep = dir / vec2(800.0, 600.0);
	vec2 texstep2 = dir / vec2(800.0, 600.0);
    
    vec3 nor2 = getNor(texture(gbuffer0, texCoord + pos * texstep2).rg);
    float influenceFactor = step(discardThreshold, dot(nor2, nor));
    vec3 col = texture(tex, texCoord + pos * texstep).rgb;
    result += col * blurWeight * influenceFactor;
    float weight = blurWeight * influenceFactor;
    
    nor2 = getNor(texture(gbuffer0, texCoord - pos * texstep2).rg);
    influenceFactor = step(discardThreshold, dot(nor2, nor));
    col = texture(tex, texCoord - pos * texstep).rgb;
    result += col * blurWeight * influenceFactor;
    weight += blurWeight * influenceFactor;
    
    return weight;
}

void main() {
	
	vec2 texstep = dir / vec2(800, 600);
	vec2 texstep2 = dir / vec2(800, 600);
	
	vec3 nor = getNor(texture(gbuffer0, texCoord).rg);
    
    float weight = 0.0;
	
	// for (int i = 0; i < 9; i++) {
        // float blurWeight = blurWeights[0];
        const float radius = 20.0;
        const float blurWeight = 1.0 / radius;
        
        vec3 col = texture(tex, texCoord).rgb;
        result += col * blurWeights[0];
        weight += blurWeight;
        
        // weight += doBlur(blurWeights[1], 1, nor);
        // weight += doBlur(blurWeights[2], 2, nor);
        // weight += doBlur(blurWeights[3], 3, nor);
        // weight += doBlur(blurWeights[4], 4, nor);
        // weight += doBlur(blurWeights[5], 5, nor);
        // weight += doBlur(blurWeights[6], 6, nor);
        // weight += doBlur(blurWeights[7], 7, nor);
        // weight += doBlur(blurWeights[8], 8, nor);
        // weight += doBlur(blurWeights[9], 9, nor);
        weight += doBlur(blurWeight, 1, nor);
        weight += doBlur(blurWeight, 2, nor);
        weight += doBlur(blurWeight, 3, nor);
        weight += doBlur(blurWeight, 4, nor);
        weight += doBlur(blurWeight, 5, nor);
        weight += doBlur(blurWeight, 6, nor);
        weight += doBlur(blurWeight, 7, nor);
        weight += doBlur(blurWeight, 8, nor);
        weight += doBlur(blurWeight, 9, nor);
        weight += doBlur(blurWeight, 10, nor);
        weight += doBlur(blurWeight, 11, nor);
        weight += doBlur(blurWeight, 12, nor);
        weight += doBlur(blurWeight, 13, nor);
        weight += doBlur(blurWeight, 14, nor);
        weight += doBlur(blurWeight, 15, nor);
        weight += doBlur(blurWeight, 16, nor);
        weight += doBlur(blurWeight, 17, nor);
        weight += doBlur(blurWeight, 18, nor);
        weight += doBlur(blurWeight, 19, nor);
    // }

    result /= weight;
    gl_FragColor = vec4(result.rgb, 1.0);
}
