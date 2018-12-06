// Based on GPU Gems 3
// http://http.developer.nvidia.com/GPUGems3/gpugems3_ch27.html
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;

uniform sampler2D tex;
uniform mat4 prevVP;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;
uniform float frameScale;

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

vec2 getVelocity(vec2 coord, float depth) {
	vec4 currentPos = vec4(coord.xy * 2.0 - 1.0, depth, 1.0);
	vec4 worldPos = vec4(getPos(eye, eyeLook, normalize(viewRay), depth, cameraProj), 1.0);
	vec4 previousPos = prevVP * worldPos;
	previousPos /= previousPos.w;
	vec2 velocity = (currentPos - previousPos).xy / 40.0;
	return velocity;
}

void main() {
	fragColor.rgb = textureLod(tex, texCoord, 0.0).rgb;
	
	// Do not blur masked objects
	if (textureLod(gbuffer0, texCoord, 0.0).a == 1.0) {
		return;
	}
	
	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (depth == 1.0) {
		return;
	}

	float blurScale = motionBlurIntensity * frameScale;
	vec2 velocity = getVelocity(texCoord, depth) * blurScale;
	
	vec2 offset = texCoord;
	int processed = 1;
	for(int i = 0; i < 8; ++i) {
		offset += velocity;
		if (textureLod(gbuffer0, offset, 0.0).a != 1.0) {
			fragColor.rgb += textureLod(tex, offset, 0.0).rgb;
			processed++;
		}
	}
	fragColor.rgb /= processed;
}
