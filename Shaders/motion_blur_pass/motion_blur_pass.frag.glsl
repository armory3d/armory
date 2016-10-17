// Based on GPU Gems 3
// http://http.developer.nvidia.com/GPUGems3/gpugems3_ch27.html
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;

uniform sampler2D tex;
uniform mat4 prevVP;
uniform vec3 eye;
uniform vec3 eyeLook;

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

// const float motionBlurIntensity = 1.0;
// const int samples = 8;

vec2 getVelocity(vec2 coord, float depth) {
	vec4 currentPos = vec4(coord.xy * 2.0 - 1.0, depth, 1.0);
	vec4 worldPos = vec4(getPos(eye, eyelook, viewRay, depth), 1.0);
	vec4 previousPos = prevVP * worldPos;
	previousPos /= previousPos.w;
	vec2 velocity = (currentPos - previousPos).xy / 40.0;
	return velocity;
}

void main() {
	vec4 color = texture(tex, texCoord);
	
	// Do not blur masked objects
	if (texture(gbuffer0, texCoord).a == 1.0) {
		fragColor = color;
		return;
	}
	
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	if (depth == 1.0) {
		fragColor = color;
		return;
	}

	float blurScale = 1.0 * motionBlurIntensity; //currentFps / targeFps;
	// blurScale *= -1.0;
	vec2 velocity = getVelocity(texCoord, depth) * blurScale;
	
	vec2 offset = texCoord;
	int processed = 1;
	// for(int i = 1; i < samples; ++i) {
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}

		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).a != 1.0) {
			color += texture(tex, offset);
			processed++;
		}
	// }
	 
	vec4 finalColor = color / processed; 
	fragColor = finalColor;
}
