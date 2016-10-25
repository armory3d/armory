// Per-Object Motion Blur
// http://john-chapman-graphics.blogspot.com/2013/01/per-object-motion-blur.html
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D gbuffer0;
uniform sampler2D sveloc;
uniform sampler2D tex;
// uniform vec2 texStep;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec2 velocity = texture(sveloc, texCoord).rg;
	velocity *= motionBlurIntensity; // * (currentFps / targetFps);
	
	vec4 col = texture(tex, texCoord);

	// Do not blur masked objects
	if (texture(gbuffer0, texCoord).a == 1.0) {
		fragColor = col;
		return;
	}

	// float speed = length(velocity / texStep);
	// const int MAX_SAMPLES = 8;
	// int samples = clamp(int(speed), 1, MAX_SAMPLES);
	const int samples = 8;
	// for (int i = 1; i < samples; ++i) {
		vec2 offset = velocity * (float(0) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		//
		offset = velocity * (float(1) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(2) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(3) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(4) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(5) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(6) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
		offset = velocity * (float(7) / float(samples - 1) - 0.5);
		col += texture(tex, texCoord + offset);
	// }
	col /= float(samples + 1);

	fragColor = col;
}
